import uuid
from django.db import models
from .base import SoftDeleteModel

class ApiKey(SoftDeleteModel):
    """
    Управление доступом клиентов через API Keys.
    Хранит только bcrypt хеш ключа.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    key_prefix = models.CharField(max_length=16)
    key_hash = models.CharField(max_length=255, unique=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=1000)
    is_active = models.BooleanField(default=True)
    
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_keys'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rate_limit_per_minute__gt=0),
                name='check_rate_limit_gt_0'
            )
        ]
        indexes = [
            models.Index(fields=['is_active'], name='idx_api_keys_active'),
            models.Index(fields=['key_prefix'], name='idx_api_keys_prefix'),
            models.Index(fields=['expires_at'], name='idx_api_keys_expiration'),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}***)"
