from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import TemplateView

def health_check(request):
    return JsonResponse({
        "status": "ok",
        "service": "File-Shipper",
        "version": "1.0"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Add this line
    path('', lambda request: redirect('file-manager'), name='root'),
    path('api/', include('filetransfer.urls')),
    path('health/', health_check, name='health-check'),
    path('help/', TemplateView.as_view(template_name='help.html'), name='help'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)