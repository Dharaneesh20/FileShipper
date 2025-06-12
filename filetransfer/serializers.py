from rest_framework import serializers
from .models import UploadedFile
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)

class UploadedFileSerializer(serializers.ModelSerializer):
    id = ObjectIdField(source='_id')
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedFile
        fields = ('id', 'file', 'filename', 'uploaded_at', 'uploaded_by', 'file_size', 'file_type', 'file_url')
        read_only_fields = ('id', 'file_url', 'file_size', 'file_type', 'uploaded_by', 'uploaded_at')

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
