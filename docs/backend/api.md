# API Contract

## API Information

### Base URL

/api/v1

### Content Type

```http
Content-Type: application/json
```

### Authentication

Все endpoints требуют JWT аутентификацию.

```http
Authorization: Bearer <jwt_token>
```

---

## API Versioning

Текущая версия:

```text
v1
```

Пример:

```text
/api/v1/services
/api/v1/routes
/api/v1/api-keys
```

Правила:

- новые поля могут добавляться без изменения версии
- breaking changes требуют новой версии API
- v2 будет опубликована отдельным namespace

---

# Error Response Format

Все ошибки возвращаются в едином формате.

```json
{
  "error": {
    "code": "ROUTE_NOT_FOUND",
    "message": "Route not found",
    "request_id": "uuid",
    "details": {}
  }
}
```

---

# Pagination

Для всех коллекций используется Offset Pagination.

## Request

```text
?page=1&page_size=50
```

## Rules

```text
page >= 1

page_size >= 1

page_size <= 100
```

## Response

```json
{
  "count": 1000,
  "page": 1,
  "page_size": 50,
  "results": []
}
```

---

# Services API

## Service Model

```json
{
  "id": "uuid",
  "name": "user-service",
  "slug": "user-service",
  "base_url": "http://user-service:8001",
  "description": "User Service",
  "is_active": true,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## GET /api/v1/services

Получить список сервисов.

### Filters

```text
?is_active=true
?name=user
```

### Sorting

```text
?ordering=name
?ordering=-created_at
```

### Response

Paginated Service List

### Error Codes

```text
401
403
500
```

---

## POST /api/v1/services

Создать сервис.

### Request

```json
{
  "name": "user-service",
  "slug": "user-service",
  "base_url": "http://user-service:8001",
  "description": "User Service",
  "is_active": true
}
```

### Validation

```text
name unique
slug unique
base_url valid URL
```

### Error Codes

```text
400
401
409
500
```

---

## GET /api/v1/services/{id}

Получить сервис.

### Error Codes

```text
401
404
500
```

---

## PATCH /api/v1/services/{id}

Частичное обновление сервиса.

### Error Codes

```text
400
401
404
409
500
```

---

## DELETE /api/v1/services/{id}

Soft Delete.

### Response

```text
204 No Content
```

---

# Routes API

## Route Model

```json
{
  "id": "uuid",
  "service_id": "uuid",
  "path_pattern": "/api/users/*",
  "method": "GET",
  "cache_enabled": true,
  "cache_ttl_seconds": 60,
  "priority": 100,
  "is_active": true,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## GET /api/v1/routes

### Filters

```text
?service_id=uuid
?method=GET
?cache_enabled=true
?is_active=true
```

### Sorting

```text
?ordering=priority
?ordering=-created_at
```

### Response

Paginated Route List

---

## POST /api/v1/routes

### Request

```json
{
  "service_id": "uuid",
  "path_pattern": "/api/users/*",
  "method": "GET",
  "cache_enabled": true,
  "cache_ttl_seconds": 60,
  "priority": 100,
  "is_active": true
}
```

### Validation

```text
service exists

valid HTTP method

cache_ttl_seconds >= 0

priority >= 0
```

---

## GET /api/v1/routes/{id}

---

## PATCH /api/v1/routes/{id}

---

## DELETE /api/v1/routes/{id}

### Response

```text
204 No Content
```

---

# API Keys API

## API Key Model

### Create Response

```json
{
  "id": "uuid",
  "name": "Mobile App",
  "api_key": "agw_xxxxxxxxxxxxxxxxx",
  "rate_limit_per_minute": 100
}
```

Полный ключ возвращается только один раз.

---

## Read Response

```json
{
  "id": "uuid",
  "name": "Mobile App",
  "key_prefix": "agw_4f8",
  "rate_limit_per_minute": 100,
  "is_active": true,
  "last_used_at": "timestamp",
  "created_at": "timestamp"
}
```

---

## GET /api/v1/api-keys

### Filters

```text
?is_active=true
```

### Sorting

```text
?ordering=-last_used_at
```

---

## POST /api/v1/api-keys

### Request

```json
{
  "name": "Mobile App",
  "rate_limit_per_minute": 100
}
```

### Validation

```text
name required

rate_limit_per_minute > 0
```

---

## GET /api/v1/api-keys/{id}

Получить API Key.

---

## PATCH /api/v1/api-keys/{id}

Обновить API Key.

---

## DELETE /api/v1/api-keys/{id}

Деактивировать API Key.

### Response

```text
204 No Content
```

---

# Logs API

Request Logs являются read-only.

---

## Request Log Model

```json
{
  "id": 1,
  "request_id": "uuid",
  "service_id": "uuid",
  "route_id": "uuid",
  "api_key_id": "uuid",
  "method": "GET",
  "path": "/api/users/1",
  "status_code": 200,
  "latency_ms": 34,
  "cache_hit": true,
  "created_at": "timestamp"
}
```

---

## GET /api/v1/logs

### Filters

```text
?service_id=uuid

?route_id=uuid

?api_key_id=uuid

?method=GET

?status_code=200

?cache_hit=true

?created_from=2026-01-01

?created_to=2026-01-31
```

### Sorting

```text
?ordering=-created_at
```

---

## GET /api/v1/logs/{id}

Получить запись лога.

---

# Dashboard API

## GET /api/v1/dashboard/metrics

### Response

```json
{
  "total_requests": 100000,
  "success_rate": 99.8,
  "error_rate": 0.2,
  "cache_hit_rate": 85.4,
  "average_latency_ms": 34
}
```

---

## GET /api/v1/dashboard/metrics/timeseries

### Query Parameters

```text
?period=1h

?period=24h

?period=7d
```

### Response

```json
{
  "points": [
    {
      "timestamp": "2026-01-01T10:00:00Z",
      "requests": 1200,
      "errors": 5,
      "avg_latency_ms": 42
    }
  ]
}
```

---

# Gateway Headers

## Rate Limiting Headers

Возвращаются Gateway Runtime.

```http
X-RateLimit-Limit: 100

X-RateLimit-Remaining: 76

X-RateLimit-Reset: 1710000120
```

---

## Cache Headers

### Cache Hit

```http
X-Cache: HIT
```

### Cache Miss

```http
X-Cache: MISS
```

### Cache TTL

```http
Cache-Control: max-age=60
```

---

## Tracing Headers

### Request ID

```http
X-Request-ID: uuid
```

### Correlation ID

```http
X-Correlation-ID: uuid
```

### Forwarded Headers

```http
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
```

---

# Global Validation Rules

```text
UUID → UUID v4

Timestamp → ISO 8601

URL → valid HTTP/HTTPS URL

page >= 1

page_size <= 100
```

---

# Standard Error Codes

| Code | Description |
|--------|--------|
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 409 | Conflict |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

---

# API Design Decisions

### APD-001

URL Versioning через `/api/v1`.

### APD-002

Единый формат ошибок для всех модулей.

### APD-003

Все коллекции поддерживают pagination.

### APD-004

Все коллекции поддерживают filtering и sorting.

### APD-005

API Key показывается полностью только при создании.

### APD-006

Request Logs являются append-only и read-only.

### APD-007

Все ответы содержат `X-Request-ID`.

### APD-008

Rate Limit и Cache состояние передаются через HTTP headers.