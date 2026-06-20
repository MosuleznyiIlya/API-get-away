# Database Architecture Overview

PostgreSQL is the single source of truth for:

- Gateway configuration
- Routes
- API keys
- Historical logs

Redis is used only as runtime storage:

- Cache
- Rate limiting
- Counters
- Temporary metrics

## 2. ERD

```
┌─────────────────┐
│    services     │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│     routes      │
└─────────────────┘

┌─────────────────┐
│    api_keys     │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│  request_logs   │
└─────────────────┘
```

Logical relationships:

- Service
  - Routes
- API Key
  - Request Logs

## 3. Table: services

### Purpose

Storage of registered upstream services.

Examples:

- user-service
- order-service
- billing-service

### Fields

| Field | Type |
|-------|------|
| id | UUID |
| name | VARCHAR(100) |
| slug | VARCHAR(100) |
| base_url | TEXT |
| description | TEXT |
| is_active | BOOLEAN |
| created_at | TIMESTAMP WITH TZ |
| updated_at | TIMESTAMP WITH TZ |
| deleted_at | TIMESTAMP WITH TZ NULL |

### Constraints

| Constraint | Field(s) |
|------------|----------|
| PK | id |
| UNIQUE | name |
| UNIQUE | slug |

### Indexes

- idx_services_slug
- idx_services_active
- idx_services_deleted

### Sample Data

```
id: 4e...
name: user-service
slug: user-service
base_url: http://user-service:8001
is_active: true
```

### Table Size

| Environment | Records |
|-------------|---------|
| MVP | 10 - 100 |
| Production | 100 - 5,000 |

## 4. Table: routes

### Purpose

Gateway routing configuration.

### Fields

| Field | Type |
|-------|------|
| id | UUID |
| service_id | UUID |
| path_pattern | VARCHAR(255) |
| method | VARCHAR(10) |
| strip_prefix | BOOLEAN |
| cache_enabled | BOOLEAN |
| cache_ttl_seconds | INTEGER |
| is_active | BOOLEAN |
| priority | INTEGER |
| created_at | TIMESTAMP WITH TZ |
| updated_at | TIMESTAMP WITH TZ |
| deleted_at | TIMESTAMP WITH TZ NULL |

### Foreign Key

| Field | References |
|-------|------------|
| service_id | services.id |

### Constraints

| Constraint | Details |
|------------|---------|
| PK | id |
| CHECK | method IN (GET, POST, PUT, PATCH, DELETE) |
| CHECK | cache_ttl_seconds >= 0 |

### Indexes

**Route Lookup**
- idx_routes_path_pattern
- idx_routes_method
- idx_routes_service

**Runtime**
- idx_routes_active
- idx_routes_priority

**Composite Index**
- (method, path_pattern)

### Sample Data

```
service_id: user-service
path_pattern: /api/users/*
method: GET
cache_enabled: true
cache_ttl_seconds: 60
```

### Table Size

| Environment | Records |
|-------------|---------|
| MVP | 50 - 500 routes |
| Production | 1,000 - 50,000 routes |

## 5. Table: api_keys

### Purpose

Client access management.

### Fields

| Field | Type |
|-------|------|
| id | UUID |
| name | VARCHAR(150) |
| key_prefix | VARCHAR(16) |
| key_hash | VARCHAR(255) |
| rate_limit_per_minute | INTEGER |
| is_active | BOOLEAN |
| last_used_at | TIMESTAMP WITH TZ NULL |
| expires_at | TIMESTAMP WITH TZ NULL |
| created_at | TIMESTAMP WITH TZ |
| updated_at | TIMESTAMP WITH TZ |
| deleted_at | TIMESTAMP WITH TZ NULL |

### Why key_prefix?

In the UI you can display:

```
agw_4f8d...
```

without revealing the full key.

### Constraints

| Constraint | Field(s) |
|------------|----------|
| PK | id |
| UNIQUE | key_hash |
| CHECK | rate_limit_per_minute > 0 |

### Indexes

- idx_api_keys_active
- idx_api_keys_prefix
- idx_api_keys_expiration

### Sample Data

```
name: Mobile App
key_prefix: agw_a4f
key_hash: 8e4c7f7c7e...
```

### Table Size

| Environment | Records |
|-------------|---------|
| MVP | 10 - 1,000 |
| Production | 100,000+ |

## 6. Table: request_logs

### Purpose

History of all requests through the Gateway.

The largest table in the system.

### Fields

| Field | Type |
|-------|------|
| id | BIGINT |
| request_id | UUID |
| route_id | UUID NULL |
| service_id | UUID NULL |
| api_key_id | UUID NULL |
| method | VARCHAR(10) |
| path | TEXT |
| query_string | TEXT |
| status_code | INTEGER |
| latency_ms | INTEGER |
| response_size_bytes | INTEGER |
| client_ip | INET |
| user_agent | TEXT |
| cache_hit | BOOLEAN |
| rate_limited | BOOLEAN |
| created_at | TIMESTAMP WITH TZ |

### Foreign Keys

| Field | References |
|-------|------------|
| route_id | routes.id |
| service_id | services.id |
| api_key_id | api_keys.id |

### Why BIGINT?

Logs grow rapidly. UUID increases index size. For logs, BIGINT (BIGSERIAL) is preferred:

- Smaller index
- Faster sorting
- Cheaper storage

### Indexes

**Most Frequent Queries**
- idx_logs_created_at
- idx_logs_status_code
- idx_logs_route
- idx_logs_service
- idx_logs_api_key

**Analytics**
- idx_logs_latency
- idx_logs_cache_hit

**Composite**
- (created_at, status_code)
- (created_at, service_id)
- (created_at, api_key_id)

### Sample Data

```
method: GET
path: /api/users/123
status_code: 200
latency_ms: 34
cache_hit: true
```

### Table Size

| Environment | Records |
|-------------|---------|
| MVP | 100,000 - 1,000,000 |
| Production | 100M+ |

## 7. Foreign Keys Summary

```
routes.service_id
        ↓
services.id

request_logs.route_id
        ↓
routes.id

request_logs.service_id
        ↓
services.id

request_logs.api_key_id
        ↓
api_keys.id
```

## 8. Audit Strategy

For MVP, a full audit_log is not needed.

We use the following fields for all configuration entities:

- created_at
- updated_at
- deleted_at

Tracked entities:

- Services
  - Creation
  - Modification
  - Deletion
- Routes
  - Creation
  - Modification
  - Deletion
- API Keys
  - Creation
  - Deactivation
  - Deletion

Future table: **audit_logs**

Example fields:

- entity_type
- entity_id
- action
- old_data
- new_data
- created_at

## 9. Soft Delete Strategy

Applied to:

- services
- routes
- api_keys

Via the field: **deleted_at**

Deletion means: `deleted_at IS NOT NULL`

All queries default to: `WHERE deleted_at IS NULL`

### Why not hard delete?

- Configuration restoration
- Change audit
- Log relationship preservation

## 10. Query Optimization Strategy

### Route Lookup

The hottest operation in the Gateway.

Strategy:

On startup, the Gateway loads routes from PostgreSQL into memory.

Runtime should **NOT** execute:

```sql
SELECT route ...
```

for each HTTP request.

### API Key Validation

After verification, the key is cached in Redis:

```
apikey:{hash}
```

### Request Logs

Never do:

```sql
SELECT *
FROM request_logs
```

Use:

- Pagination
- Cursor Pagination
- Date Filters

### Table Partitioning

For Production, immediately plan for:

**request_logs** — Partition By: `MONTH(created_at)`

Examples:

- request_logs_2026_01
- request_logs_2026_02
- request_logs_2026_03

### Storage Growth Estimate

| Table | MVP | Production |
|-------|-----|------------|
| services | 100 | 5,000 |
| routes | 500 | 50,000 |
| api_keys | 1,000 | 100,000+ |
| request_logs | 1M | 100M+ |

## Database Design Decisions

### DD-001

UUID for business entities.

Reason: services, routes, and api_keys may be used in external APIs.

### DD-002

BIGINT for logs.

Reason: smaller index, faster sorting, cheaper storage.

### DD-003

Soft Delete for configuration.

Reason: audit, restoration, security.

### DD-004

Partitioning only for request_logs.

Reason: the only table with high data growth.

### DD-005

Route Configuration is stored in PostgreSQL but executed from Gateway Runtime memory.

Reason: exclude SQL from the critical path of HTTP request processing.
