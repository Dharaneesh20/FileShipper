import socket

def server_ip(request):
    """Context processor to add server IP to all templates"""
    ip = get_local_ip()
    return {'server_ip': ip}

def get_local_ip():
    """Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
