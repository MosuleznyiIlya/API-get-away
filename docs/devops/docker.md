# Docker

## Containers

### Backend Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "gateway.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Gateway Runtime Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "gateway.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "8"]
```

### Frontend Container

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### PostgreSQL Container

```dockerfile
FROM postgres:15-alpine

ENV POSTGRES_DB=gateway
ENV POSTGRES_USER=gateway

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
```

### Redis Container

```dockerfile
FROM redis:7-alpine

COPY redis.conf /usr/local/etc/redis/redis.conf

EXPOSE 6379

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
```

## Networks

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # no external access
  database:
    driver: bridge
    internal: true
```

### Network Rules

- Frontend → Backend: через `frontend` network
- Backend → Database: через `database` network
- Backend → Redis: через `backend` network
- Gateway → Redis: через `backend` network
- Gateway → Upstream: через `frontend` network

## Volumes

```yaml
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  backend_static:
    driver: local
```

### Volume Rules

- `postgres_data` — persistent database storage
- `redis_data` — persistent Redis data (RDB snapshots)
- `backend_static` — Django static files (collected)

## Health Checks

### Backend Health Check

```python
# gateway/health/views.py
from django.http import JsonResponse
from django.db import connection
import redis

def health_check(request):
    try:
        # DB check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Redis check
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()

        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": timezone.now().isoformat()
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": timezone.now().isoformat()
        }, status=503)
```

### Docker Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### Frontend Health Check

```nginx
location /health {
    access_log off;
    return 200 "healthy
";
    add_header Content-Type text/plain;
}
```
