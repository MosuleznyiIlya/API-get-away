# Gateway Runtime

## Runtime Architecture

Gateway Runtime — это middleware pipeline, который обрабатывает каждый входящий запрос через упорядоченную цепочку компонентов.

## Middleware Order

```
JWT
↓
API Key
↓
Rate Limit
↓
Route Resolver
↓
Cache
↓
Proxy
↓
Metrics
↓
Logs
```

## Execution Pipeline

1. **Request Entry** — WSGI/ASGI получает HTTP запрос
2. **JWT Middleware** — проверяет Authorization header
   - Извлекает Bearer token
   - Валидирует подпись, exp, iss
   - Добавляет decoded payload в request context
3. **API Key Middleware** — проверяет X-API-Key header
   - Извлекает ключ
   - Ищет prefix в БД
   - Сравнивает bcrypt hash
   - Проверяет is_active
4. **Rate Limit Middleware** — проверяет лимиты
   - Определяет client_id (JWT sub или API Key id)
   - Формирует Redis key
   - Проверяет счетчик
   - Добавляет rate limit headers
5. **Route Resolver Middleware** — определяет маршрут
   - Сопоставляет path + method
   - Применяет priority rules
   - Добавляет upstream_url в request context
6. **Cache Middleware** — проверяет кэш
   - Формирует cache key
   - Проверяет Redis
   - При HIT — возвращает cached response, pipeline завершается
7. **Proxy Middleware** — проксирует запрос
   - Формирует HTTP запрос к upstream
   - Добавляет служебные заголовки
   - Устанавливает таймауты
   - Проксирует ответ
8. **Metrics Middleware** — записывает метрики
   - latency_ms
   - status_code
   - bytes_in / bytes_out
   - Сохраняет в PostgreSQL (async)
9. **Logs Middleware** — записывает лог
   - Формирует structured JSON log
   - Сохраняет в PostgreSQL (async)
10. **Response Exit** — возвращает HTTP ответ клиенту

## Gateway Lifecycle

### Startup
1. Загрузка конфигурации из PostgreSQL (services, routes)
2. Подключение к Redis
3. Инициализация middleware pipeline
4. Health check endpoint доступен

### Request Processing
1. Потоковая обработка через middleware pipeline
2. Каждый middleware может:
   - Модифицировать request context
   - Вернуть response (short-circuit)
   - Передать управление следующему middleware

### Shutdown
1. Graceful shutdown — завершение активных запросов
2. Закрытие соединений с Redis и PostgreSQL
3. Flush pending logs и metrics
