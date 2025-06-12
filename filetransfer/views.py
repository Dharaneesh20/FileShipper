from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import FileResponse, JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import UploadedFile, PeerDevice, TransferSession
from .serializers import UploadedFileSerializer
from bson import ObjectId
import logging
import traceback
import socket
import json
import threading
import time
import uuid
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

class FileUploadView(generics.CreateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response({'error': 'No file provided'}, status=400)

            # Log debug info
            logger.debug(f"Received file: {file_obj.name}, size: {file_obj.size}")
            
            # Create migration if needed
            from django.core.management import call_command
            try:
                call_command('makemigrations', 'filetransfer')
                call_command('migrate')
            except Exception as e:
                logger.warning(f"Migration error: {e}")
            
            # Create the file upload record
            upload = UploadedFile(
                file=file_obj,
                filename=file_obj.name,
                uploaded_by=request.user.username
            )
            upload.save()
            
            # Return serialized data
            serializer = self.get_serializer(upload)
            return Response(serializer.data, status=201)
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}\n{traceback.format_exc()}")
            return Response({'error': f'Upload failed: {str(e)}'}, status=400)

class FileListView(generics.ListAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

class FileDownloadView(generics.RetrieveAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Override to support ObjectId lookup"""
        pk = self.kwargs.get('pk')
        try:
            from bson import ObjectId
            if ObjectId.is_valid(pk):
                return UploadedFile.objects.get(_id=ObjectId(pk))
        except:
            pass
        return super().get_object()

    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        return FileResponse(file_obj.file, as_attachment=True, filename=file_obj.filename)

class FileManagerView(LoginRequiredMixin, TemplateView):
    template_name = 'filetransfer/file_manager.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = UploadedFile.objects.all().order_by('-uploaded_at')
        # No need to modify files, the id property will be used in template
        context['files'] = files
        return context

# Add broadcast service for device discovery
class NetworkDiscoveryService:
    _instance = None
    _devices = {}
    _running = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start(self):
        if not self._running:
            self._running = True
            self._discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
            self._discovery_thread.start()
    
    def _discovery_loop(self):
        # UDP broadcast for device discovery
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', 0))  # Bind to any available port
        
        # Listen for incoming discovery requests
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind(('', 45678))  # Discovery port
        listen_sock.settimeout(1)
        
        while self._running:
            try:
                # Send discovery broadcast
                device_info = {
                    "app": "File-Shipper",
                    "version": "1.0",
                    "host": socket.gethostname(),
                    "port": 8000,
                    "uuid": str(uuid.uuid4())
                }
                sock.sendto(json.dumps(device_info).encode(), ('<broadcast>', 45678))
                
                # Listen for responses
                try:
                    data, addr = listen_sock.recvfrom(1024)
                    try:
                        device = json.loads(data.decode())
                        if device.get("app") == "File-Shipper" and addr[0] != self.get_local_ip():
                            self._devices[device.get("uuid")] = {
                                "name": device.get("host", "Unknown Device"),
                                "ip": addr[0],
                                "port": device.get("port", 8000),
                                "last_seen": time.time()
                            }
                    except:
                        pass
                except socket.timeout:
                    pass
                    
                # Clean old devices
                now = time.time()
                to_remove = []
                for device_id, device in self._devices.items():
                    if now - device["last_seen"] > 30:  # 30 seconds timeout
                        to_remove.append(device_id)
                for device_id in to_remove:
                    del self._devices[device_id]
                    
                time.sleep(3)  # Send discovery broadcast every 3 seconds
                
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                time.sleep(5)  # Wait before retry on error
    
    def get_devices(self):
        return list(self._devices.values())
    
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

# Start the discovery service
discovery_service = NetworkDiscoveryService.get_instance()
discovery_service.start()

class DeviceDiscoveryView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        devices = discovery_service.get_devices()
        return Response(devices)

class DeviceScannerView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Provide event stream for real-time device updates"""
        def event_stream():
            last_devices = []
            while True:
                current_devices = discovery_service.get_devices()
                
                # Only send update if device list has changed
                if current_devices != last_devices:
                    last_devices = current_devices.copy()
                    yield f"data: {json.dumps(current_devices)}\n\n"
                
                time.sleep(1)
        
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

# Enhance existing views with better discovery
class SendFileView(LoginRequiredMixin, TemplateView):
    template_name = 'filetransfer/send_file.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = UploadedFile.objects.all().order_by('-uploaded_at')
        context['found_devices'] = discovery_service.get_devices()
        
        # Get device connection info
        device_info = {
            'device_id': self.get_device_id(),
            'username': self.request.user.username,
            'ip': self.get_local_ip(),
            'port': 8000,
            'app': "File-Shipper",  # App identifier for discovery
            'version': "1.0"
        }
        context['device_info'] = json.dumps(device_info)
        return context
    
    def get_device_id(self):
        # Simplified device ID generation
        hostname = socket.gethostname()
        # Create a reproducible ID based on hostname
        return f"web-{hash(hostname) % 10000:04d}"
    
    def get_local_ip(self):
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))  # Google DNS
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

class ReceiveFileView(LoginRequiredMixin, TemplateView):
    template_name = 'filetransfer/receive_file.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transfers'] = TransferSession.objects.filter(
            receiver=self.request.user.username
        ).order_by('-created_at')
        
        # Add device info for JavaScript to use
        device_info = {
            'device_id': SendFileView.get_device_id(self),
            'ip': SendFileView.get_local_ip(self),
            'username': self.request.user.username
        }
        context['device_info'] = json.dumps(device_info)
        return context

class PeerDiscoveryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Clean up old peers
        PeerDevice.objects.filter(
            last_seen__lt=timezone.now() - timezone.timedelta(minutes=5)
        ).update(is_online=False)
        
        # Get online peers
        peers = PeerDevice.objects.filter(is_online=True)
        
        # Register this device
        device_id = request.GET.get('device_id', socket.gethostname())
        device_name = request.GET.get('device_name', request.user.username)
        ip_address = request.GET.get('ip', request.META.get('REMOTE_ADDR'))
        
        PeerDevice.objects.update_or_create(
            device_id=device_id,
            defaults={
                'device_name': device_name,
                'ip_address': ip_address,
                'is_online': True
            }
        )
        
        return JsonResponse({
            'peers': list(peers.values('device_id', 'device_name', 'ip_address', 'port'))
        })

class TransferSessionView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = TransferSession.objects.all()
    
    def post(self, request, *args, **kwargs):
        file_id = request.data.get('file_id')
        receiver = request.data.get('receiver')
        
        if not file_id or not receiver:
            return Response({'error': 'File ID and receiver are required'}, status=400)
        
        try:
            file_obj = UploadedFile.objects.get(_id=ObjectId(file_id))
            transfer = TransferSession.objects.create(
                file=file_obj,
                sender=request.user.username,
                receiver=receiver
            )
            return Response({
                'transfer_id': transfer.id,
                'status': transfer.status
            }, status=201)
        except Exception as e:
            logger.error(f"Transfer error: {str(e)}")
            return Response({'error': f'Transfer failed: {str(e)}'}, status=400)
    
    def put(self, request, pk, *args, **kwargs):
        try:
            transfer = TransferSession.objects.get(_id=ObjectId(pk))
            
            # Only receiver can update status
            if request.user.username != transfer.receiver:
                return Response({'error': 'Not authorized'}, status=403)
            
            status = request.data.get('status')
            if status in ['accepted', 'rejected']:
                transfer.status = status
                if status == 'accepted':
                    # Start file transfer (in real world this would be WebSocket)
                    pass
                
                transfer.save()
                return Response({'status': transfer.status})
            
            return Response({'error': 'Invalid status'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
