# Final Django Architecture

The architecture is built around two logically independent subsystems.

## Control Plane

Platform management.

```
React Admin
        │
        ▼
Django REST API
        │
        ▼
PostgreSQL
```

Functions:

- Services CRUD
- Routes CRUD
- API Keys CRUD
- Logs API
- Metrics API
- Dashboard API

## Data Plane

User traffic processing.

```
Client
   │
   ▼
Gateway Runtime
   │
   ▼
Upstream Services
```

Functions:

- JWT Validation
- API Key Validation
- Rate Limiting
- Cache
- Reverse Proxy
- Metrics Collection
- Request Logging

## Repository Structure

```
backend/

  gateway/

  apps/
    services/
    routes/
    api_keys/

    proxy/
    auth/
    ratelimit/
    cache/

    logs/
    metrics/

    dashboard/

  core/
```

---

# 2. Apps Boundaries (Strict Separation)

## services

**Responsibility:** Service Registry

**Allowed:** CRUD Services

**Forbidden:** Routing, Cache, JWT, Rate Limiting

## routes

**Responsibility:** Route Configuration

**Allowed:** Route CRUD, Route Resolution Rules

**Forbidden:** Proxy Execution

## api_keys

**Responsibility:** API Key Management

**Allowed:** Generate, Rotate, Revoke, Validate Metadata

**Forbidden:** Rate Limiting

## auth

**Responsibility:** Authentication

**Contains:** JWT Validation, API Key Validation

**Knows nothing about:** Cache, Proxy, Metrics

## ratelimit

**Responsibility:** Traffic Control

**Only:** Redis Token Buckets

## cache

**Responsibility:** Response Cache

## proxy

**Responsibility:** Reverse Proxy, Request Forwarding

## logs

**Responsibility:** Request Logging

## metrics

**Responsibility:** Runtime Metrics

## dashboard

**Responsibility:** Dashboard Read APIs

**Does not store data.** Only aggregates.

## core

**Common components:** Exceptions, Base Classes, Settings, Utilities, Constants

---

# 3. Layered Architecture

Each application uses the same structure.

```
app/
  api/
    serializers/
  services/
  repositories/
  models/
  selectors/
```

## Controller Layer

**Purpose:** HTTP Layer

**Contains:** Views, ViewSets

**Tasks:** accept request, call service, return response

## Service Layer

**Purpose:** Business Logic

**Tasks:** orchestration, validation, business rules

## Repository Layer

**Purpose:** Data Access

**Tasks:** ORM queries, filtering, selections

### Rule

```
View
  ↓
Service
  ↓
Repository
  ↓
Database
```

**Forbidden:**

- View → ORM
- View → Database
- View → Redis

---

# 4. Middleware Pipeline Order (Critical)

For Gateway Runtime, the order is strictly fixed.

```
Request
  ↓
Request ID Middleware
  ↓
Structured Logging Context
  ↓
JWT Validation
  ↓
API Key Validation
  ↓
Rate Limiter
  ↓
Route Resolver
  ↓
Cache Layer
  ↓
Reverse Proxy
  ↓
Metrics Collector
  ↓
Request Logger
  ↓
Response
```

## Why This Order

- **JWT before Cache** — Protected cache cannot be returned without access verification.
- **Rate Limit before Proxy** — Protection of upstream services.
- **Cache before Proxy** — Load reduction.
- **Metrics after Proxy** — Measures actual latency.

---

# 5. Dependency Graph

```
    services
    routes
    api_keys
       │
       ▼
      auth
       │
       ▼
   ratelimit
       │
       ▼
     cache
       │
       ▼
     proxy
       │
       ▼
  logs     metrics
       │
       ▼
    dashboard
```

## Allowed Dependencies

- proxy → routes
- proxy → services
- auth → api_keys
- dashboard → metrics
- dashboard → logs

## Forbidden Dependencies

- cache → proxy
- proxy → cache
- metrics → proxy
- logs → proxy
- services → routes
- routes → services ORM access

Interaction only through the service layer.

---

# 6. Data Flow Inside Backend

## Admin Flow

```
React
  ↓
DRF API
  ↓
Serializer
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

## Gateway Flow

```
Request
  ↓
Middleware
  ↓
Auth
  ↓
Rate Limiter
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
  ↓
Response
```

---

# 7. Error Handling Strategy

## Global Exception Handler

Single point of error handling.

Returns:

```json
{
  "error": {
    "code": "ROUTE_NOT_FOUND",
    "message": "Route not found",
    "request_id": "..."
  }
}
```

## Error Categories

| Category | Code |
|----------|------|
| Validation Errors | 400 |
| Authentication Errors | 401 |
| Authorization Errors | 403 |
| Route Not Found | 404 |
| Rate Limit Exceeded | 429 |
| Upstream Errors | 502, 503, 504 |
| Internal Errors | 500 |

## Local Error Handling

Each service raises domain exceptions.

Examples: `InvalidApiKey`, `RouteNotFound`, `ServiceUnavailable`

HTTP conversion happens only by the global handler.

---

# 8. Logging Strategy (Structured Logging)

Format:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "request_id": "...",
  "path": "...",
  "method": "GET",
  "status_code": 200,
  "latency_ms": 34
}
```

## Log Categories

- **Access Logs** — Every request.
- **Application Logs** — CRUD operations.
- **Security Logs** — JWT errors, API Key errors, Rate Limit events.
- **System Logs** — Redis failures, Database failures, Proxy failures.

## Never Log

- JWT tokens
- API keys
- Passwords
- Authorization headers

---

# 9. Validation Strategy

## DRF Serializers

**Responsible for:** Input Shape Validation

Examples: required fields, field types, max length, regex

## Service Layer

**Responsible for:** Business Validation

Examples: service name uniqueness, route conflicts, api key expiration, service activation rules

### Rule

```
Serializer
  ↓
Service Validation
  ↓
Repository
```

---

# 10. Transaction Boundaries

Transactions are used only for write operations.

## Service Creation

```
BEGIN
  create service
COMMIT
```

## Route Creation

```
BEGIN
  create route
  invalidate route cache
COMMIT
```

## API Key Creation

```
BEGIN
  create key
  store hash
COMMIT
```

## Logging

Does not require transactions. Append-only.

## Metrics

Does not use PostgreSQL transactions. Only Redis atomic operations.

---

# Redis Operations Location

- **auth** — API Key Runtime Cache
- **ratelimit** — Token Buckets
- **cache** — Response Cache
- **metrics** — Counters, Aggregations

# Database Access Location

Only through the Repository Layer.

**Allowed:** `services.repositories`, `routes.repositories`, `api_keys.repositories`, `logs.repositories`

**Forbidden:** middleware, proxy, cache, ratelimit

# Proxy Layer Location

`apps/proxy`

**Responsibility:** Build Upstream URL, Forward Request, Receive Response, Return Response

# Cache Layer Location

`apps/cache`

**Responsibility:** Cache Key Generation, Cache Read, Cache Write, Cache Invalidation

---

# Architecture Decisions (ADR v1)

| ADR | Decision |
|-----|----------|
| ADR-001 | Control Plane and Data Plane are logically separated. |
| ADR-002 | Gateway Runtime is Stateless. |
| ADR-003 | Redis is used exclusively as a Runtime Store. |
| ADR-004 | PostgreSQL is the single Source of Truth. |
| ADR-005 | All ORM operations go through the Repository Layer. |
| ADR-006 | All business rules are in the Service Layer. |
| ADR-007 | Route Resolution is performed from memory, not from PostgreSQL. |
| ADR-008 | Request Logs are append-only. |
| ADR-009 | Token Bucket is chosen as the primary Rate Limiting algorithm. |
| ADR-010 | Global Exception Handler is the single point of error response formation. |

---

# Known Risks

## High

- **Reverse Proxy Correctness** — multipart uploads, large payloads, streaming responses
- **Redis Dependency** — cache, rate limiting, metrics depend on Redis.
- **Route Cache Invalidation** — Risk of desynchronization between Gateway memory and PostgreSQL.
- **Request Log Growth** — Table can grow to hundreds of millions of records.

---

# Scalability Constraints

## PostgreSQL

Main constraint: `request_logs`. Partitioning is required.

## Redis

Main constraint: cache storage. Memory consumption grows linearly.

## Gateway Runtime

Constraint: CPU + network throughput. Gateway remains horizontally scalable due to the absence of local state.

## Dashboard

As load grows, a transition will be required:

```
request_logs
      ↓
aggregated metrics
      ↓
time-series storage
```

for example Prometheus/OpenTelemetry in future versions of the platform.
