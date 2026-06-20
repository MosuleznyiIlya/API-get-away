# Caching

## Cache Strategy

Используется **Response Caching** с Redis для кэширования ответов upstream-сервисов.

## Cache Keys

Формат: `cache:response:{hash}`

Где `hash` = SHA256(`method` + `path` + `normalized_query` + `api_key_id`)

Примеры:
- `cache:response:f48d67aa8b`
- `cache:response:9e2c1d4a5f`

### Key Components

- `method` — HTTP метод (GET, HEAD)
- `path` — нормализованный путь (без query string)
- `normalized_query` — отсортированные query params (только для GET)
- `api_key_id` — идентификатор клиента (для изоляции кэша)

## TTL Rules

| Route Pattern | Default TTL | Max TTL |
|---------------|-------------|---------|
| `GET /api/v1/users` | 300s | 3600s |
| `GET /api/v1/users/*` | 60s | 300s |
| `GET /api/v1/orders` | 120s | 600s |
| `POST /api/v1/*` | 0s (no cache) | 0s |
| `PUT /api/v1/*` | 0s (no cache) | 0s |
| `DELETE /api/v1/*` | 0s (no cache) | 0s |

TTL может быть переопределён в конфигурации маршрута.

## Cache Value Structure

```json
{
  "status_code": 200,
  "headers": {},
  "body": "...",
  "created_at": 1710000000
}
```

## Invalidation Rules

### Automatic Invalidation
- При обновлении сервиса — инвалидировать все кэши этого сервиса
- При обновлении маршрута — инвалидировать кэши этого маршрута
- При отзыве API Key — инвалидировать кэши этого ключа

### Manual Invalidation
- `POST /api/v1/cache/invalidate` — инвалидировать по pattern
- `DELETE /api/v1/cache/` — полная очистка кэша

### TTL-Based Expiration
- Redis автоматически удаляет ключи по истечении TTL
- Не требует дополнительных действий

## Cache Flow

```
Client -> Gateway: GET /api/v1/users?page=1
Gateway -> Cache: Check
Cache -> Redis: GET cache:response:{hash}

alt HIT
    Redis --> Cache: Cached Response
    Cache --> Gateway: Return cached
    Gateway --> Client: 200 OK (X-Cache: HIT)
else MISS
    Redis --> Cache: None
    Cache --> Gateway: No cache
    Gateway -> Upstream: GET /api/v1/users?page=1
    Upstream --> Gateway: Response
    Gateway -> Cache: Store
    Cache -> Redis: SETEX key TTL response
    Gateway --> Client: 200 OK (X-Cache: MISS)
end
```

## Cache Headers

Gateway добавляет заголовки для информирования клиента:
- `X-Cache-Status`: HIT / MISS / BYPASS
- `X-Cache-TTL`: оставшееся время жизни кэша (секунды)
- `Cache-Control`: max-age, no-cache (проксируется от upstream)

## Redis Fallback Behavior

Если Redis недоступен:
- **Cache bypass** — запрос идёт напрямую к upstream
- Логируется warning: `cache_redis_unavailable`
- Метрика: `cache_redis_error`
- Gateway продолжает работу (fail-open)

## Cache Safety

### Poisoning Protection
- Кэшируются только ответы с status_code 200-299
- Ответы с ошибками (4xx, 5xx) не кэшируются
- Кэш изолирован по `api_key_id` (не пересекается между клиентами)

### Leakage Protection
- Каждый API Key имеет изолированное пространство кэша
- JWT-пользователи разделяют кэш по `api_key_id` (если запрос через API Key) или по `service_id` (если через JWT)

## Memory Estimation

- 10 000 объектов кэша
- Средний размер ответа: 5 KB
- Потребление памяти Redis: ≈ 50 MB

## Cleanup Scenarios

- Автоматическое удаление по TTL
- Принудительная очистка при:
  - обновлении маршрута
  - удалении маршрута
  - деактивации сервиса
- Политика eviction: `allkeys-lru` (старые кэш-записи удаляются первыми)
