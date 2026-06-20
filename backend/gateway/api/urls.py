from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, RouteViewSet, ApiKeyViewSet, RequestLogViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'api-keys', ApiKeyViewSet, basename='apikey')
router.register(r'logs', RequestLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
