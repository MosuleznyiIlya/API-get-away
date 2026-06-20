# Rate Limiting

## Algorithm

Используется **Fixed Window Counter** алгоритм с Redis.

### Fixed Window

```
Window: 1 minute
Key: ratelimit:{client_id}:{route_id}:{timestamp_minute}

Example:
ratelimit:api_key_123:route_456:202401011200
```

### Algorithm Steps

1. Определить текущее окно: `floor(current_timestamp / window_size)`
2. Сформировать Redis key
3. Выполнить `INCR key`
4. Если key новый — установить TTL = window_size
5. Получить текущее значение
6. Если значение > limit — отклонить запрос (429)
7. Добавить rate limit headers

### Redis Commands

```redis
MULTI
INCR ratelimit:client:route:window
EXPIRE ratelimit:client:route:window 60
EXEC
```

## Redis Keys

| Pattern | Описание | TTL |
|---------|----------|-----|
| `ratelimit:{api_key_id}:{route_id}:{window}` | Счетчик для API Key | 60s |
| `ratelimit:{jwt_sub}:{route_id}:{window}` | Счетчик для JWT | 60s |
| `ratelimit:ip:{client_ip}:{route_id}:{window}` | Счетчик по IP (fallback) | 60s |

## Flow

```
Client -> Gateway: Request
Gateway -> Rate Limit: Check Limit
Rate Limit -> Redis: INCR + EXPIRE
Redis --> Rate Limit: Count
alt Count <= Limit
    Rate Limit --> Gateway: ALLOW
    Gateway -> Upstream: Request
    Upstream --> Gateway: Response
    Gateway --> Client: Response + Rate Limit Headers
else Count > Limit
    Rate Limit --> Gateway: DENY
    Gateway --> Client: 429 Too Many Requests
end
```

## Error Handling

### Rate Limit Exceeded
- Status: 429 Too Many Requests
- Headers:
  - `X-RateLimit-Limit`: 1000
  - `X-RateLimit-Remaining`: 0
  - `X-RateLimit-Reset`: 1704067260
  - `Retry-After`: 45
- Body:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 45 seconds.",
  "limit": 1000,
  "window": 60,
  "reset_at": "2024-01-01T12:01:00Z"
}
```

### Redis Unavailable
- Если Redis недоступен — пропускаем rate limiting (fail open)
- Логируем warning
- Метрика: `rate_limit_redis_error`

### Configuration

| Параметр | Значение | Описание |
|----------|----------|----------|
| `RATE_LIMIT_WINDOW` | 60 | Размер окна в секундах |
| `RATE_LIMIT_DEFAULT` | 1000 | Лимит по умолчанию |
| `RATE_LIMIT_REDIS_TIMEOUT` | 0.5 | Таймаут подключения к Redis |
| `RATE_LIMIT_FAIL_OPEN` | True | Пропускать при недоступности Redis |
