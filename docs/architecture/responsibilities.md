# Responsibilities

## Component Responsibilities

### JWT Module

Responsible:
- token validation
- signature verification
- expiration checking
- issuer validation

Not Responsible:
- routing
- caching
- rate limiting

### Cache Module

Responsible:
- Cache lookup
- Cache storage
- TTL management
- Cache invalidation

Not Responsible:
- Authentication
- Authorization
- Routing decisions

### Proxy Module

Responsible:
- Upstream communication
- Request forwarding
- Response streaming
- Timeout handling

Not Responsible:
- Business logic
- Data transformation
- Authentication

### Rate Limit Module

Responsible:
- Counter increment
- Limit checking
- Window management
- Redis key operations

Not Responsible:
- Request routing
- Response caching
- User management

### Route Resolver Module

Responsible:
- Path matching
- Method matching
- Priority evaluation
- Upstream selection

Not Responsible:
- Authentication
- Rate limiting
- Caching

## Service Responsibilities

- **Services Service** — CRUD операции над upstream-сервисами
- **Routes Service** — CRUD операции над маршрутами проксирования
- **Auth Service** — JWT и API Key валидация
- **RateLimit Service** — управление лимитами и счетчиками
- **Cache Service** — операции чтения/записи кэша
- **Proxy Service** — выполнение HTTP проксирования
- **Logs Service** — запись и чтение логов запросов
- **Metrics Service** — агрегация и предоставление метрик
- **Dashboard Service** — API для фронтенда Dashboard

## Module Responsibilities

### gateway/apps/

- `services/` — управление upstream-сервисами
- `routes/` — управление маршрутами
- `auth/` — аутентификация и авторизация
- `ratelimit/` — ограничение частоты запросов
- `cache/` — кэширование ответов
- `proxy/` — проксирование запросов
- `logs/` — логирование
- `metrics/` — сбор метрик
- `dashboard/` — API для админ-панели

## Dependency Rules

- Apps communicate through service layer
- Domain layer не зависит от инфраструктуры
- Infrastructure layer зависит от domain layer
- Gateway Runtime использует все модули через четкий pipeline
