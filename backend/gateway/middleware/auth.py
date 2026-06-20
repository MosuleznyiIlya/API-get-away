import logging
import jwt
import redis
import bcrypt
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse
from gateway.models import ApiKey

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except Exception:
    redis_client = None

def get_redis_client():
    return redis_client

def fast_hmac(key: str) -> str:
    """Generates a fast HMAC for Redis storage to avoid bcrypt overhead in hot path."""
    return hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        key.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

class AuthenticationMiddleware:
    """
    Dumb enforcement layer:
    - Extracts credentials.
    - Validates (API Key > JWT).
    - Puts auth context in request.
    - Passes on.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce on Data Plane
        if getattr(request, 'is_control_plane', False):
            return self.get_response(request)

        # 1. API Key Auth Priority
        api_key_header = request.headers.get('X-API-Key')
        if api_key_header:
            error = self._authenticate_api_key(request, api_key_header)
            if error:
                return self._error_response(error['error'], error['message'], error.get('status', 401))
            return self.get_response(request)

        # 2. JWT Auth Fallback
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            error = self._authenticate_jwt(request, token)
            if error:
                return self._error_response(error['error'], error['message'], 401)
            return self.get_response(request)

        # 3. No credentials
        return self._error_response('unauthorized', 'Authentication credentials were not provided.', 401)

    def _authenticate_api_key(self, request, full_key):
        if '_' not in full_key:
            return {'error': 'invalid_api_key_format', 'message': 'Invalid API Key format'}
        
        prefix = full_key.split('_')[0]
        f_hmac = fast_hmac(full_key)
        r_client = get_redis_client()
        
        # Redis Primary Lookup (Hot Path)
        if r_client:
            try:
                # We check two keys:
                # 1. Is the prefix active?
                # 2. Is this specific full_key hmac proven valid?
                is_active = r_client.get(f"apikey_active:{prefix}")
                is_valid_hash = r_client.get(f"apikey_valid:{f_hmac}")
                
                if is_active == '0':
                    return {'error': 'api_key_revoked', 'message': 'API Key is deactivated'}
                    
                if is_active == '1' and is_valid_hash:
                    # Cache HIT - Valid key
                    request.gateway_auth = {
                        'type': 'api_key',
                        'id': is_valid_hash,  # We cached the DB ID here
                    }
                    return None
            except Exception as e:
                logger.error(f"Redis cache lookup failed: {e}")
                # Fall open to DB fallback

        # DB Fallback (Cold Path)
        try:
            api_key_record = ApiKey.objects.get(key_prefix=prefix, deleted_at__isnull=True)
        except ApiKey.DoesNotExist:
            return {'error': 'invalid_api_key', 'message': 'API Key not found'}
        
        if not api_key_record.is_active:
            # Cache the revocation
            if r_client:
                r_client.setex(f"apikey_active:{prefix}", 3600, '0')
            return {'error': 'api_key_revoked', 'message': 'API Key is deactivated'}
        
        # Expensive bcrypt check
        if not bcrypt.checkpw(full_key.encode('utf-8'), api_key_record.key_hash.encode('utf-8')):
            return {'error': 'invalid_api_key', 'message': 'API Key signature invalid'}

        # Populate Redis Cache on Miss (valid key)
        if r_client:
            try:
                # Cache prefix as active
                r_client.setex(f"apikey_active:{prefix}", 86400, '1')
                # Cache the proven hmac with the record ID
                r_client.setex(f"apikey_valid:{f_hmac}", 86400, str(api_key_record.id))
            except Exception as e:
                logger.error(f"Failed to populate Redis cache: {e}")
            
        request.gateway_auth = {
            'type': 'api_key',
            'id': str(api_key_record.id)
        }
        return None

    def _authenticate_jwt(self, request, token):
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            request.gateway_auth = {
                'type': 'jwt',
                'payload': payload,
                'sub': payload.get('sub')
            }
            return None
        except jwt.ExpiredSignatureError:
            return {'error': 'token_expired', 'message': 'Token has expired'}
        except jwt.InvalidSignatureError:
            return {'error': 'invalid_signature', 'message': 'Token signature is invalid'}
        except jwt.DecodeError:
            return {'error': 'invalid_token_format', 'message': 'Token must consist of 3 parts separated by dots'}
        except Exception:
            return {'error': 'invalid_token', 'message': 'Invalid token'}

    def _error_response(self, error_code, message, status_code):
        return JsonResponse({
            'error': error_code,
            'message': message
        }, status=status_code)
