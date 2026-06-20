# Deployment

## Deployment Strategy

### Blue-Green Deployment (Future)
- Два идентичных окружения
- Мгновенное переключение трафика
- Откат за секунды

### Rolling Deployment (Current)
- Постепенное обновление инстансов
- Проверка health check перед следующим инстансом
- Автоматический rollback при ошибках

## Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: gateway
      POSTGRES_USER: gateway
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gateway"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgres://gateway:${DB_PASSWORD}@postgres:5432/gateway
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=False
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 10s
      timeout: 5s
      retries: 3

  gateway:
    build: ./backend
    command: gunicorn gateway.wsgi:application --bind 0.0.0.0:8080
    environment:
      - DATABASE_URL=postgres://gateway:${DB_PASSWORD}@postgres:5432/gateway
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GATEWAY_MODE=runtime
    ports:
      - "8080:8080"
    depends_on:
      - backend
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `JWT_SECRET_KEY` | Secret for JWT signing | `super-secret-key-32-chars-long` |
| `DEBUG` | Debug mode | `False` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60` |
| `RATE_LIMIT_DEFAULT` | Default rate limit | `1000` |
| `CACHE_DEFAULT_TTL` | Default cache TTL (seconds) | `300` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ALLOWED_HOSTS` | Django allowed hosts | `*` |
| `CORS_ORIGIN_WHITELIST` | CORS origins | `http://localhost:3000` |

## Production Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Steps

1. **Clone repository**
   ```bash
   git clone https://github.com/MosuleznyiIlya/gateway.git
   cd gateway
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Build and start**
   ```bash
   docker-compose up -d --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Verify deployment**
   ```bash
   curl http://localhost:8000/health/
   curl http://localhost:8080/health/
   ```

### SSL/TLS (Future)
- Traefik или Nginx reverse proxy
- Let's Encrypt автоматические сертификаты
- HTTPS redirect
