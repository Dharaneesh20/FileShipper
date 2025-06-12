from djongo import models
from django.utils import timezone
import mimetypes
from bson import ObjectId

class UploadedFile(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)
    file_type = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
        super().save(*args, **kwargs)

    @property
    def id(self):
        return str(self._id)

class PeerDevice(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    device_name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    ip_address = models.CharField(max_length=100)
    port = models.IntegerField(default=8000)
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=True)

    @property
    def id(self):
        return str(self._id)

class TransferSession(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def id(self):
        return str(self._id)
