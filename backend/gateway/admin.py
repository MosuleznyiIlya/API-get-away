from django.contrib import admin
from .models import Service, Route, ApiKey, RequestLog

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'base_url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'base_url')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        return Service.all_objects.all()

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('path_pattern', 'method', 'service', 'priority', 'cache_enabled', 'is_active')
    list_filter = ('method', 'is_active', 'cache_enabled', 'service')
    search_fields = ('path_pattern',)
    
    def get_queryset(self, request):
        return Route.all_objects.all()

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_prefix', 'rate_limit_per_minute', 'is_active', 'expires_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'key_prefix')
    readonly_fields = ('key_hash', 'key_prefix')  # Не позволяем изменять хеш в админке
    
    def get_queryset(self, request):
        return ApiKey.all_objects.all()

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'method', 'path', 'status_code', 'latency_ms', 'cache_hit')
    list_filter = ('method', 'status_code', 'cache_hit', 'rate_limited')
    search_fields = ('path', 'client_ip', 'request_id')
    readonly_fields = [f.name for f in RequestLog._meta.fields]  # Логи нельзя редактировать
    
    # Для логов отключаем возможность ручного удаления и добавления через админку
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
