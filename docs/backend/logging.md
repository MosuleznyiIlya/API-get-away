# Logging

## Structured Logs

Все логи в формате JSON для удобства парсинга и анализа.

### Log Format

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "request_id": "uuid",
  "method": "GET",
  "path": "/api/v1/users",
  "status_code": 200,
  "latency_ms": 45,
  "client_ip": "192.168.1.1",
  "api_key_id": "uuid",
  "user_id": "user_123",
  "service_id": "uuid",
  "route_id": "uuid",
  "upstream_url": "http://user-service:8080",
  "cache_status": "MISS",
  "error": null,
  "message": "Request processed successfully"
}
```

### Log Levels

| Level | Использование |
|-------|---------------|
| DEBUG | Отладочная информация, request/response details |
| INFO | Успешные операции, request completion |
| WARNING | Не критичные ошибки (Redis unavailable, cache miss) |
| ERROR | Ошибки обработки (upstream timeout, invalid token) |
| CRITICAL | Критичные ошибки (DB connection lost) |

## Request Logs

### Storage
- Таблица: `request_logs`
- БД: PostgreSQL
- Запись: async через Celery или Django signals

### Fields
- request_id — UUID correlation ID
- method — HTTP метод
- path — путь запроса
- status_code — HTTP статус ответа
- latency_ms — время обработки в мс
- client_ip — IP адрес клиента
- api_key_id — ссылка на API Key (nullable)
- user_id — JWT subject (nullable)
- service_id — ссылка на сервис (nullable)
- route_id — ссылка на маршрут (nullable)
- created_at — timestamp

### Query Examples

```sql
-- Top 10 slowest requests
SELECT path, AVG(latency_ms) as avg_latency
FROM request_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY path
ORDER BY avg_latency DESC
LIMIT 10;

-- Error rate by service
SELECT service_id, 
       COUNT(*) as total,
       SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as errors,
       errors::float / total as error_rate
FROM request_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY service_id;
```

## Audit Logs

### Events
- Создание/обновление/удаление сервиса
- Создание/обновление/удаление маршрута
- Создание/отзыв API Key
- Изменение конфигурации rate limiting
- Очистка кэша

### Format
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "event": "service_created",
  "actor": "admin_user_123",
  "resource": "service",
  "resource_id": "uuid",
  "changes": {
    "name": "user-service",
    "upstream_url": "http://user-service:8080"
  },
  "ip": "192.168.1.1"
}
```

## Retention Rules

| Log Type | Retention | Action |
|----------|-----------|--------|
| Request Logs | 30 days | Автоматическое удаление старых записей |
| Audit Logs | 1 year | Архивация в S3 после 90 дней |
| Error Logs | 90 days | Автоматическое удаление |
| Debug Logs | 7 days | Автоматическое удаление |

### Cleanup Strategy
- Ежедневный Celery task
- DELETE с условием created_at < retention_date
- Батчами по 10,000 записей для снижения нагрузки на БД
