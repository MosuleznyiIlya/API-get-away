# Technical Specification
## Project: API Gateway Platform

### Goal

Build an API Gateway with a web administration panel that provides:

- JWT validation
- API Key management
- Rate limiting
- Response caching
- Request routing
- Reverse proxying
- Request logging
- Metrics and analytics

---

# Technology Stack

## Backend

- Python 3.13+
- Django 5+
- Django REST Framework
- PostgreSQL 17
- Redis 8
- httpx
- PyJWT
- Uvicorn

## Frontend

- React
- TypeScript
- Vite
- React Query
- Zustand
- Tailwind CSS
- shadcn/ui
- Recharts

## Infrastructure

- Docker
- Docker Compose

---

# Architecture

Client -> React Admin Panel -> API Gateway

Gateway responsibilities:

1. Validate JWT/API Key
2. Check rate limits
3. Check cache
4. Resolve route
5. Forward request
6. Log request
7. Collect metrics

Target services:

- User Service
- Order Service
- Payment Service

---

# Backend Modules

gateway/

- services/
- routes/
- auth/
- ratelimit/
- cache/
- logs/
- metrics/
- proxy/
- dashboard/

---

# Functional Requirements

## 1. Service Management

The system must allow:

- Create service
- Update service
- Delete service
- View service list

Service model:

- id (UUID)
- name
- base_url
- is_active
- created_at

Example:

{
  "name": "user-service",
  "base_url": "http://user-service:8001",
  "is_active": true
}

---

## 2. Route Management

The system must allow:

- Create route
- Update route
- Delete route
- View routes

Route model:

- id (UUID)
- service_id (UUID)
- path_pattern
- method
- cache_enabled
- cache_ttl

Example:

{
  "path": "/api/users",
  "method": "GET",
  "service": "user-service",
  "cache_enabled": true,
  "cache_ttl": 60
}

Routing flow:

1. Receive request
2. Find matching route
3. Resolve target service
4. Forward request

---

## 3. JWT Validation

Header:

Authorization: Bearer <TOKEN>

Validation:

- Signature
- Expiration
- Issuer

Invalid token response:

HTTP 401

{
  "detail": "Invalid token"
}

---

## 4. API Keys

Header:

X-API-Key: <KEY>

Generated format:

agw_xxxxxxxxxxxxxxxxx

Store only hash values.

API Key model:

- id (UUID)
- name
- key_hash
- rate_limit
- is_active

---

## 5. Rate Limiting

Algorithm:

Token Bucket

Redis key:

rl:{api_key}

Configuration:

{
  "requests_per_minute": 100
}

Exceeded limit:

HTTP 429

{
  "detail": "Rate limit exceeded"
}

---

## 6. Response Cache

Cache only GET requests.

Do not cache:

- POST
- PUT
- PATCH
- DELETE

Redis key:

cache:{sha256}

TTL configured per route.

---

## 7. Reverse Proxy

Supported methods:

- GET
- POST
- PUT
- PATCH
- DELETE

Processing pipeline:

1. Validate authentication
2. Validate rate limits
3. Check cache
4. Resolve route
5. Forward request
6. Return response

---

## 8. Request Logging

Log every request.

Model:

- id (UUID)
- request_id (UUID)
- path
- method
- status_code
- latency_ms
- client_ip
- created_at

---

## 9. Metrics

Metrics to expose:

- Total requests
- Error count
- Average latency
- Cache hit rate
- Rate limit hits

Endpoint:

GET /api/dashboard/metrics

---

# REST API

## Services

GET    /api/services
POST   /api/services
GET    /api/services/{id}
PATCH  /api/services/{id}
DELETE /api/services/{id}

## Routes

GET    /api/routes
POST   /api/routes
PATCH  /api/routes/{id}
DELETE /api/routes/{id}

## API Keys

GET    /api/api-keys
POST   /api/api-keys
PATCH  /api/api-keys/{id}
DELETE /api/api-keys/{id}

## Logs

GET /api/logs

Filters:

?status=500
?method=GET

Pagination:

?page=1&page_size=50

---

# Frontend Requirements

## Dashboard

Cards:

- Total Requests
- Success Rate
- Cache Hit Rate
- Average Latency

Charts:

- Requests per minute
- Errors per minute
- Latency

## Services Page

- Table
- Create service
- Edit service
- Delete service

## Routes Page

- Table
- Filtering
- Create route
- Edit route
- Delete route

## API Keys Page

- Table
- Create key
- Deactivate key

## Logs Page

- Table
- Filtering
- Search
- Pagination

---

# Non-Functional Requirements

## Performance

- Support at least 1000+ RPS in local environment
- Redis used for all hot-path operations

## Security

- Store only hashed API keys
- JWT validation
- Configurable CORS

## Maintainability

- Type hints
- Ruff
- Pytest
- DRF serializers
- Service layer pattern

## Containerization

Single command:

docker compose up

Must start:

- frontend
- gateway
- postgres
- redis

---

# Database Tables

services
routes
api_keys
request_logs

---

# Development Roadmap

Sprint 1

- Database models
- Service CRUD
- Route CRUD

Sprint 2

- Routing engine
- Reverse proxy

Sprint 3

- JWT authentication
- API Keys

Sprint 4

- Rate limiting
- Redis cache

Sprint 5

- Logging
- Metrics

Sprint 6

- React dashboard

Sprint 7

- Docker
- Automated tests
- README
- Demo data

---

# Definition of Done

The project is complete when:

1. Requests can be routed to target services.
2. JWT and API Key authentication work.
3. Rate limiting is enforced through Redis.
4. GET responses can be cached.
5. Request logs are stored and viewable.
6. Metrics are available through API and dashboard.
7. Frontend administration panel is fully functional.
8. Entire system runs through Docker Compose.
9. Automated tests pass.
