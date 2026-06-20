# API Contract

## Authentication

Все endpoints требуют аутентификации через:
- **JWT**: `Authorization: Bearer <token>`
- **API Key**: `X-API-Key: <key>`

## Services API

### GET /api/v1/services/
**Request**: Query params: `page`, `page_size`, `is_active`
**Response**: 
```json
{
  "count": 100,
  "next": "?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "user-service",
      "upstream_url": "http://user-service:8080",
      "health_check_url": "http://user-service:8080/health",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```
**Validation Rules**: `page_size` <= 100
**Error Codes**: 401, 403, 500

### POST /api/v1/services/
**Request**:
```json
{
  "name": "user-service",
  "upstream_url": "http://user-service:8080",
  "health_check_url": "http://user-service:8080/health"
}
```
**Validation Rules**: `name` — unique, alphanumeric + hyphens; `upstream_url` — valid URL
**Error Codes**: 400, 401, 409, 500

### GET /api/v1/services/{id}/
**Response**: Service object
**Error Codes**: 401, 404, 500

### PUT /api/v1/services/{id}/
**Request**: Service object (full update)
**Validation Rules**: Same as POST
**Error Codes**: 400, 401, 404, 409, 500

### DELETE /api/v1/services/{id}/
**Response**: 204 No Content
**Error Codes**: 401, 404, 500

## Routes API

### GET /api/v1/routes/
**Request**: Query params: `page`, `page_size`, `service_id`, `is_active`
**Response**: Paginated list of Route objects
**Error Codes**: 401, 403, 500

### POST /api/v1/routes/
**Request**:
```json
{
  "service_id": "uuid",
  "path": "/api/v1/users/*",
  "method": "GET",
  "priority": 10
}
```
**Validation Rules**: `path` — not empty; `method` — valid HTTP method; `priority` — integer >= 0
**Error Codes**: 400, 401, 404 (service not found), 409, 500

### GET /api/v1/routes/{id}/
**Response**: Route object
**Error Codes**: 401, 404, 500

### PUT /api/v1/routes/{id}/
**Request**: Route object (full update)
**Error Codes**: 400, 401, 404, 409, 500

### DELETE /api/v1/routes/{id}/
**Response**: 204 No Content
**Error Codes**: 401, 404, 500

## API Keys API

### GET /api/v1/api-keys/
**Request**: Query params: `page`, `page_size`, `is_active`
**Response**: Paginated list of API Key objects (without key_hash)
**Error Codes**: 401, 403, 500

### POST /api/v1/api-keys/
**Request**:
```json
{
  "name": "mobile-app",
  "rate_limit": 1000
}
```
**Response**:
```json
{
  "id": "uuid",
  "name": "mobile-app",
  "prefix": "ag_",
  "key": "ag_abc123def456",  // shown only once
  "rate_limit": 1000,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```
**Validation Rules**: `name` — not empty; `rate_limit` — > 0
**Error Codes**: 400, 401, 409, 500

### DELETE /api/v1/api-keys/{id}/
**Response**: 204 No Content
**Error Codes**: 401, 404, 500

## Logs API

### GET /api/v1/logs/
**Request**: Query params: `page`, `page_size`, `service_id`, `route_id`, `status_code`, `start_date`, `end_date`
**Response**: Paginated list of RequestLog objects
**Error Codes**: 401, 403, 500

## Metrics API

### GET /api/v1/metrics/
**Request**: Query params: `name`, `start_date`, `end_date`, `service_id`, `route_id`
**Response**:
```json
{
  "metrics": [
    {
      "name": "request_count",
      "value": 1500,
      "labels": {"service": "user-service", "status": "200"},
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "aggregations": {
    "total_requests": 1500,
    "avg_latency_ms": 45.2,
    "error_rate": 0.01
  }
}
```
**Error Codes**: 401, 403, 500

## Validation Rules (Global)

- UUID fields — valid UUID v4 format
- Timestamps — ISO 8601 format
- URLs — valid HTTP/HTTPS URL
- Pagination: `page` >= 1, `page_size` between 1 and 100

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request — validation error |
| 401 | Unauthorized — invalid or missing credentials |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found — resource does not exist |
| 409 | Conflict — duplicate or constraint violation |
| 429 | Too Many Requests — rate limit exceeded |
| 500 | Internal Server Error |
| 502 | Bad Gateway — upstream error |
| 504 | Gateway Timeout — upstream timeout |
