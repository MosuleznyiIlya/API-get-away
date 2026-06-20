from rest_framework import serializers
from gateway.models import Service, Route, ApiKey, RequestLog

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'slug', 'base_url', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'service', 'path_pattern', 'method', 'strip_prefix', 'cache_enabled', 
                  'cache_ttl_seconds', 'is_active', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key_prefix', 'rate_limit_per_minute', 'is_active', 
                  'last_used_at', 'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'key_prefix', 'last_used_at', 'created_at', 'updated_at']

class ApiKeyCreateResponseSerializer(serializers.ModelSerializer):
    plaintext_key = serializers.CharField(read_only=True)
    
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key_prefix', 'plaintext_key', 'rate_limit_per_minute', 'is_active', 'created_at']
        read_only_fields = ['id', 'key_prefix', 'plaintext_key', 'created_at']

class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'
        read_only_fields = [f.name for f in RequestLog._meta.fields] # strictly read-only
