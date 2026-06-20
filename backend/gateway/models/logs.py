import uuid
from django.db import models

class RequestLog(models.Model):
    """
    История всех запросов (Request Log).
    Самая тяжелая таблица в БД.
    """
    id = models.BigAutoField(primary_key=True)  # BIGSERIAL в PostgreSQL
    request_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # ForeignKey используем SET_NULL, чтобы soft_delete не удалял логи
    route = models.ForeignKey('gateway.Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    service = models.ForeignKey('gateway.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    api_key = models.ForeignKey('gateway.ApiKey', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    
    method = models.CharField(max_length=10)
    path = models.TextField()
    query_string = models.TextField(blank=True)
    status_code = models.IntegerField()
    latency_ms = models.IntegerField()
    response_size_bytes = models.IntegerField()
    client_ip = models.GenericIPAddressField(protocol='both')
    user_agent = models.TextField(blank=True)
    
    cache_hit = models.BooleanField(default=False)
    rate_limited = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'request_logs'
        indexes = [
            models.Index(fields=['created_at'], name='idx_logs_created_at'),
            models.Index(fields=['status_code'], name='idx_logs_status_code'),
            models.Index(fields=['route'], name='idx_logs_route'),
            models.Index(fields=['service'], name='idx_logs_service'),
            models.Index(fields=['api_key'], name='idx_logs_api_key'),
            models.Index(fields=['latency_ms'], name='idx_logs_latency'),
            models.Index(fields=['cache_hit'], name='idx_logs_cache_hit'),
            # Композитные индексы для частых запросов на аналитику
            models.Index(fields=['created_at', 'status_code'], name='idx_logs_created_status'),
            models.Index(fields=['created_at', 'service'], name='idx_logs_created_service'),
            models.Index(fields=['created_at', 'api_key'], name='idx_logs_created_apikey'),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.latency_ms}ms)"
