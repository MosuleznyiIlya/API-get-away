# Request Flows

## Request Flow

1. Client отправляет HTTP запрос на Gateway Runtime
2. Gateway извлекает заголовки Authorization (JWT) или X-API-Key
3. JWT Module валидирует токен (подпись, exp, issuer)
4. API Key Module валидирует ключ (поиск в БД, проверка статуса)
5. Rate Limit Module проверяет лимиты через Redis
6. Route Resolver определяет upstream по path + method
7. Cache Module проверяет наличие кэшированного ответа
8. Proxy Module перенаправляет запрос к upstream-сервису
9. Metrics Module записывает latency, status code, bytes
10. Logs Module записывает структурированный лог в PostgreSQL
11. Cache Module сохраняет ответ в Redis (если настроен TTL)
12. Gateway возвращает ответ клиенту

## Cache Flow

1. Gateway получает запрос
2. Формирует cache key: `{method}:{path}:{normalized_query}`
3. Проверяет наличие в Redis
4. Если HIT — возвращает кэшированный ответ
5. Если MISS — проксирует к upstream, сохраняет в Redis с TTL
6. При обновлении маршрута/сервиса — инвалидирует связанный кэш

## JWT Flow

1. Client отправляет запрос с заголовком `Authorization: Bearer <token>`
2. Gateway извлекает токен из заголовка
3. Проверяет формат JWT (3 части, разделенные точками)
4. Валидирует подпись с использованием секретного ключа
5. Проверяет срок действия (exp claim)
6. Проверяет issuer (iss claim)
7. Если валиден — добавляет decoded payload в request context
8. Если невалиден — возвращает 401 Unauthorized

## Rate Limit Flow

1. Gateway определяет идентификатор клиента (API Key или JWT sub)
2. Формирует Redis key: `ratelimit:{client_id}:{route_id}:{window}`
3. Увеличивает счетчик через INCR
4. Устанавливает TTL окна через EXPIRE
5. Если счетчик > лимита — возвращает 429 Too Many Requests
6. Добавляет заголовки X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

## Proxy Flow

1. Gateway получает upstream URL из Route Resolver
2. Формирует HTTP запрос к upstream (метод, заголовки, body)
3. Добавляет служебные заголовки: X-Request-ID, X-Forwarded-For
4. Устанавливает таймауты: connect=5s, read=30s
5. Отправляет запрос к upstream
6. Получает ответ от upstream
7. Проксирует status code, заголовки, body обратно клиенту
8. Обрабатывает ошибки соединения (502 Bad Gateway, 504 Gateway Timeout)

## Failure Flow

### JWT Validation Failure
- 401 Unauthorized
- Тело: `{ "error": "invalid_token", "message": "Token has expired" }`

### API Key Validation Failure
- 401 Unauthorized
- Тело: `{ "error": "invalid_api_key", "message": "API key not found or revoked" }`

### Rate Limit Exceeded
- 429 Too Many Requests
- Тело: `{ "error": "rate_limit_exceeded", "message": "Too many requests" }`
- Заголовки: Retry-After

### Route Not Found
- 404 Not Found
- Тело: `{ "error": "route_not_found", "message": "No matching route found" }`

### Upstream Connection Error
- 502 Bad Gateway
- Тело: `{ "error": "upstream_error", "message": "Cannot connect to upstream service" }`

### Upstream Timeout
- 504 Gateway Timeout
- Тело: `{ "error": "upstream_timeout", "message": "Upstream service did not respond in time" }`
