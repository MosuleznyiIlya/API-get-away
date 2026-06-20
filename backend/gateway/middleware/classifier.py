from django.urls import resolve, Resolver404

class RequestClassificationMiddleware:
    """
    Classifies the request as Control Plane or Data Plane BEFORE any authentication.
    - Uses Django's URL resolver.
    - If the route is defined in the Django application (e.g. /api/v1/..., /admin/...), it's Control Plane.
    - If Resolver404 is raised, the route is meant for the Reverse Proxy (Data Plane).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Attempt to resolve the path using Django's URLconf
            resolve(request.path_info)
            request.is_control_plane = True
            request.is_data_plane = False
        except Resolver404:
            # Path not found in Django -> must be a Gateway proxy route
            request.is_control_plane = False
            request.is_data_plane = True

        return self.get_response(request)
