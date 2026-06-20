# Rate Limiting

## Algorithm: Token Bucket

Выбран **Token Bucket** для поддержки burst-запросов и предсказуемого поведения.

### Bucket Structure

Redis Key: `rl:{client_id}:{route_id}`

Value (Hash):
```json
{
  "tokens": 84,
  "capacity": 100,
  "last_refill": 1710000000
}
```

### Algorithm Steps

1. Загрузить bucket из Redis: `HGETALL rl:{client_id}:{route_id}`
2. Вычислить прошедшее время с `last_refill`
3. Пополнить токены: `tokens = min(capacity, tokens + elapsed * rate)`
4. Если `tokens >= 1`:
   - Уменьшить `tokens` на 1
   - Обновить `last_refill`
   - Сохранить bucket: `HMSET`
   - Разрешить запрос
5. Если `tokens < 1`:
   - Отклонить запрос (429)

### Redis Atomicity

Для предотвращения race condition используется **Lua script**:

```lua
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HGETALL', key)
local tokens, last_refill

if #bucket == 0 then
    tokens = capacity
    last_refill = now
else
    tokens = tonumber(bucket[2])
    last_refill = tonumber(bucket[4])
end

local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * rate)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 120)
    return 1
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', last_refill)
    redis.call('EXPIRE', key, 120)
    return 0
end
```

## Per-Key Limits

| Limit Type | Redis Key Pattern | Default |
|------------|-------------------|---------|
| API Key | `rl:{api_key_id}:{route_id}` | 1000/min |
| JWT User | `rl:{jwt_sub}:{route_id}` | 1000/min |
| IP Fallback | `rl:ip:{client_ip}:{route_id}` | 100/min |

## Configuration

| Параметр | Значение | Описание |
|----------|----------|----------|
| `RATE_LIMIT_CAPACITY` | 100 | Максимум токенов в bucket |
| `RATE_LIMIT_RATE` | 1000/min | Скорость пополнения токенов |
| `RATE_LIMIT_REDIS_TIMEOUT` | 0.5s | Таймаут подключения к Redis |
| `RATE_LIMIT_FAIL_OPEN` | True | Пропускать при недоступности Redis |

## Error Handling

### Rate Limit Exceeded
- Status: 429 Too Many Requests
- Headers:
  ```http
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1704067260
  Retry-After: 45
  ```
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
- Пропускаем rate limiting (fail-open)
- Логируем warning: `rate_limit_redis_error`
- Метрика: `rate_limit_redis_error`
- Gateway продолжает работу

## Abuse Scenarios

| Сценарий | Защита |
|----------|--------|
| Distributed brute force | По `api_key_id` + IP correlation |
| Key sharing | Уникальный `api_key_id` per client |
| Bypass через JWT | JWT sub также rate-limited |
| Redis down | Fail-open + алерт |

## Redis TTL

- Bucket TTL: `2 × refill window` (по умолчанию 120s)
- Inactive users автоматически очищаются
