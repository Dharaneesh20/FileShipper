from django.urls import path
from .views import (
    FileUploadView, FileListView, FileDownloadView, FileManagerView,
    SendFileView, ReceiveFileView, PeerDiscoveryView, TransferSessionView,
    DeviceDiscoveryView, DeviceScannerView
)

urlpatterns = [
    path('', FileManagerView.as_view(), name='file-manager'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('list/', FileListView.as_view(), name='file-list'),
    path('download/<str:pk>/', FileDownloadView.as_view(), name='file-download'),  # Changed to str for ObjectId
    path('send/', SendFileView.as_view(), name='send-file'),
    path('receive/', ReceiveFileView.as_view(), name='receive-file'),
    path('peers/', PeerDiscoveryView.as_view(), name='peer-discovery'),
    path('transfer/<str:pk>/', TransferSessionView.as_view(), name='transfer-session'),
    path('devices/', DeviceDiscoveryView.as_view(), name='device-discovery'),
    path('scan/', DeviceScannerView.as_view(), name='device-scanner'),
]
