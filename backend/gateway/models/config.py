import uuid
from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from .base import SoftDeleteModel

class Service(SoftDeleteModel):
    """
    Хранилище зарегистрированных upstream-сервисов.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    base_url = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'
        indexes = [
            models.Index(fields=['slug'], name='idx_services_slug'),
            models.Index(fields=['is_active'], name='idx_services_active'),
        ]

    def clean(self):
        super().clean()
        # Базовая валидация URL схемы
        parsed_url = urlparse(self.base_url)
        if parsed_url.scheme not in ['http', 'https']:
            raise ValidationError({'base_url': 'Only HTTP/HTTPS schemes are supported.'})

    def __str__(self):
        return f"{self.name} ({self.slug})"


class Route(SoftDeleteModel):
    """
    Конфигурация маршрутизации (Gateway routing configuration).
    """
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='routes')
    path_pattern = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    strip_prefix = models.BooleanField(default=True)
    cache_enabled = models.BooleanField(default=False)
    cache_ttl_seconds = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cache_ttl_seconds__gte=0),
                name='check_cache_ttl_seconds_gte_0'
            )
        ]
        indexes = [
            models.Index(fields=['path_pattern'], name='idx_routes_path_pattern'),
            models.Index(fields=['method'], name='idx_routes_method'),
            models.Index(fields=['service'], name='idx_routes_service'),
            models.Index(fields=['is_active'], name='idx_routes_active'),
            models.Index(fields=['priority'], name='idx_routes_priority'),
            models.Index(fields=['method', 'path_pattern'], name='idx_routes_method_path'),
        ]

    def __str__(self):
        return f"{self.method} {self.path_pattern} -> {self.service.name}"
