import django_filters
from gateway.models import Service, Route, ApiKey, RequestLog

class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='exact')
    
    class Meta:
        model = Service
        fields = ['is_active', 'name', 'slug']

class RouteFilter(django_filters.FilterSet):
    path_pattern = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Route
        fields = ['method', 'service', 'is_active', 'cache_enabled', 'path_pattern']

class ApiKeyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    key_prefix = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = ApiKey
        fields = ['is_active', 'name', 'key_prefix']

class RequestLogFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = RequestLog
        fields = ['method', 'status_code', 'cache_hit', 'rate_limited', 'route', 'service', 'api_key']
