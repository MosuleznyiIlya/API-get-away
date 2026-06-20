from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

from gateway.models import Service, Route, ApiKey, RequestLog
from .serializers import (
    ServiceSerializer, RouteSerializer, 
    ApiKeySerializer, ApiKeyCreateResponseSerializer, 
    RequestLogSerializer
)
from gateway.services import (
    create_service, update_service, delete_service,
    create_route, update_route, delete_route,
    create_api_key, update_api_key, revoke_api_key
)

class BaseAdminViewSet(viewsets.ModelViewSet):
    """
    Base viewset enforcing Admin only access.
    """
    permission_classes = [IsAdminUser]


class ServiceViewSet(BaseAdminViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filterset_fields = ['is_active', 'slug']

    def perform_create(self, serializer):
        # Delegate to Service Layer
        instance = create_service(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        instance = update_service(serializer.instance, serializer.validated_data)
        serializer.instance = instance

    def perform_destroy(self, instance):
        delete_service(instance)


class RouteViewSet(BaseAdminViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filterset_fields = ['service', 'method', 'is_active']

    def perform_create(self, serializer):
        instance = create_route(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        instance = update_route(serializer.instance, serializer.validated_data)
        serializer.instance = instance

    def perform_destroy(self, instance):
        delete_route(instance)


class ApiKeyViewSet(BaseAdminViewSet):
    queryset = ApiKey.objects.all()
    filterset_fields = ['is_active', 'key_prefix']

    def get_serializer_class(self):
        if self.action == 'create':
            return ApiKeyCreateResponseSerializer
        return ApiKeySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        name = serializer.validated_data.get('name')
        rate_limit = serializer.validated_data.get('rate_limit_per_minute', 1000)
        
        # Delegate creation to service layer. Returns the tuple.
        api_key_instance, plaintext_key = create_api_key(name=name, rate_limit_per_minute=rate_limit)
        
        # Inject plaintext key purely for the response presentation
        api_key_instance.plaintext_key = plaintext_key
        
        response_serializer = self.get_serializer(api_key_instance)
        headers = self.get_success_headers(response_serializer.data)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        instance = update_api_key(serializer.instance, serializer.validated_data)
        serializer.instance = instance

    def perform_destroy(self, instance):
        revoke_api_key(instance)


class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Strictly Read-Only API for logs.
    """
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    permission_classes = [IsAdminUser]
    # filterset_class = RequestLogFilter is defined in urls/filters implicitly or configured there.
