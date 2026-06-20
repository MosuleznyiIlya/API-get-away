import string
import secrets
import bcrypt
import logging
import redis
from django.db import transaction
from gateway.models import ApiKey

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
except Exception:
    redis_client = None

def _invalidate_api_key_cache(prefix: str):
    if redis_client:
        try:
            redis_client.delete(f"apikey:{prefix}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for api key prefix {prefix}: {e}")

def generate_random_string(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@transaction.atomic
def create_api_key(name: str, rate_limit_per_minute: int = 1000) -> tuple[ApiKey, str]:
    """
    Creates an API Key.
    Returns a tuple of (ApiKey instance, plaintext_key).
    The plaintext_key must NEVER be logged or stored.
    """
    # 1. Generate the raw random key
    raw_key = generate_random_string(32)
    prefix = f"ag_{raw_key[:10]}" # Or random independent prefix
    
    # Prefix needs to be 16 chars max according to models.py
    # Format: {prefix}_{random_base62}
    full_key = f"{prefix}_{raw_key}"
    
    # 2. Hash the full key
    salt = bcrypt.gensalt(rounds=12)
    key_hash = bcrypt.hashpw(full_key.encode('utf-8'), salt).decode('utf-8')
    
    # 3. Create the record
    api_key = ApiKey.objects.create(
        name=name,
        key_prefix=prefix,
        key_hash=key_hash,
        rate_limit_per_minute=rate_limit_per_minute
    )
    
    return api_key, full_key

@transaction.atomic
def update_api_key(api_key: ApiKey, data: dict) -> ApiKey:
    for field, value in data.items():
        if field in ['name', 'rate_limit_per_minute', 'is_active']:
            setattr(api_key, field, value)
    api_key.save()
    _invalidate_api_key_cache(api_key.key_prefix)
    return api_key

@transaction.atomic
def revoke_api_key(api_key: ApiKey) -> None:
    api_key.is_active = False
    api_key.delete() # Soft delete
    _invalidate_api_key_cache(api_key.key_prefix)
