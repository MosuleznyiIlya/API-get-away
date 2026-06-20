# Caching

## Cache Strategy

Используется **Response Caching** с Redis для кэширования ответов upstream-сервисов.

## Cache Keys

Формат: `cache:{method}:{path}:{normalized_query}:{api_key_id}`

Примеры:
- `cache:GET:/api/v1/users:page=1&size=10:api_key_123`
- `cache:GET:/api/v1/users/123::api_key_123`

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

TTL может быть переопределен в конфигурации маршрута.

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
Cache -> Redis: GET cache:GET:/api/v1/users:page=1&size=10:api_key_123

alt HIT
    Redis --> Cache: Cached Response
    Cache --> Gateway: Return cached
    Gateway --> Client: 200 OK (from cache)
else MISS
    Redis --> Cache: None
    Cache --> Gateway: No cache
    Gateway -> Upstream: GET /api/v1/users?page=1
    Upstream --> Gateway: Response
    Gateway -> Cache: Store
    Cache -> Redis: SETEX key TTL response
    Gateway --> Client: 200 OK
end
```

## Cache Headers

Gateway добавляет заголовки для информирования клиента:
- `X-Cache-Status`: HIT / MISS / BYPASS
- `X-Cache-TTL`: оставшееся время жизни кэша (секунды)
- `Cache-Control`: max-age, no-cache (проксируется от upstream)
