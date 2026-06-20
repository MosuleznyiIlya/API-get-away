import logging
import redis
from django.db import transaction
from django.conf import settings
from gateway.models import Service, Route

logger = logging.getLogger(__name__)

# Very basic mock for Redis client. In production, this should be properly configured.
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
except Exception:
    redis_client = None


def _invalidate_service_cache(service_id):
    """
    Invalidates all cached routes for a given service.
    """
    if redis_client:
        try:
            keys = redis_client.keys(f"cache:route:*") # Extremely simplified for now.
            for key in keys:
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to invalidate cache for service {service_id}: {e}")


def _invalidate_route_cache(route_id):
    """
    Invalidates a specific cached route.
    """
    if redis_client:
        try:
            pattern = f"cache:route:{route_id}:*"
            keys = redis_client.keys(pattern)
            for key in keys:
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to invalidate cache for route {route_id}: {e}")


@transaction.atomic
def create_service(data: dict) -> Service:
    service = Service.objects.create(**data)
    return service


@transaction.atomic
def update_service(service: Service, data: dict) -> Service:
    for field, value in data.items():
        setattr(service, field, value)
    service.save()
    _invalidate_service_cache(service.id)
    return service


@transaction.atomic
def delete_service(service: Service) -> None:
    service.delete() # Soft delete handled by model
    _invalidate_service_cache(service.id)


@transaction.atomic
def create_route(data: dict) -> Route:
    route = Route.objects.create(**data)
    return route


@transaction.atomic
def update_route(route: Route, data: dict) -> Route:
    for field, value in data.items():
        setattr(route, field, value)
    route.save()
    _invalidate_route_cache(route.id)
    return route


@transaction.atomic
def delete_route(route: Route) -> None:
    route.delete() # Soft delete handled by model
    _invalidate_route_cache(route.id)
