# Service Diagrams

## Component Diagram

```
┌─────────────────────────────────────┐
│           React Frontend            │
└─────────────┬───────────────────────┘
              │ REST API
┌─────────────▼───────────────────────┐
│        Django Control Plane         │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │Services │ │ Routes  │ │ API    │ │
│  │  API    │ │  API    │ │ Keys   │ │
│  └─────────┘ └─────────┘ └────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  Logs   │ │ Metrics │ │Dashboard│ │
│  │  API    │ │  API    │ │  API   │ │
│  └─────────┘ └─────────┘ └────────┘ │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      PostgreSQL    │    Redis     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Gateway Runtime             │
│  JWT → API Key → Rate Limit → Route│
│  → Cache → Proxy → Metrics → Logs  │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      Upstream Services              │
│  User Service, Order Service, etc.  │
└─────────────────────────────────────┘
```

## Communication Diagram

1. Client → Gateway Runtime (HTTP)
2. Gateway Runtime → Redis (Cache/Rate Limit)
3. Gateway Runtime → PostgreSQL (Logs/Metrics)
4. Gateway Runtime → Upstream Service (HTTP)
5. React → Django API (REST/JSON)
6. Django API → PostgreSQL (SQL)

## Sequence Diagrams

### Request Flow
```
Client -> Gateway: HTTP Request
Gateway -> JWT Module: Validate Token
JWT Module --> Gateway: Valid/Invalid
Gateway -> API Key Module: Validate Key
API Key Module --> Gateway: Valid/Invalid
Gateway -> Rate Limit Module: Check Limit
Rate Limit Module -> Redis: INCR counter
Redis --> Rate Limit Module: Count
Rate Limit Module --> Gateway: Allowed/Denied
Gateway -> Route Resolver: Find Route
Route Resolver -> PostgreSQL: SELECT route
PostgreSQL --> Route Resolver: Route config
Route Resolver --> Gateway: Upstream URL
Gateway -> Cache Module: Check Cache
Cache Module -> Redis: GET cache_key
Redis --> Cache Module: Cached/None
Cache Module --> Gateway: Cached Response / None
Gateway -> Proxy Module: Forward Request
Proxy Module -> Upstream: HTTP Request
Upstream --> Proxy Module: HTTP Response
Proxy Module --> Gateway: Response
Gateway -> Metrics Module: Record Metrics
Gateway -> Logs Module: Write Log
Gateway -> Cache Module: Store Response (if cacheable)
Gateway --> Client: HTTP Response
```

### Cache Flow
```
Client -> Gateway: Request
Gateway -> Cache: Check
Cache -> Redis: GET
Redis --> Cache: Hit/Miss
Cache --> Gateway: Response/None
alt Cache Miss
    Gateway -> Upstream: Request
    Upstream --> Gateway: Response
    Gateway -> Cache: Store
    Cache -> Redis: SETEX
end
Gateway --> Client: Response
```

## Deployment Diagram

```
┌─────────────────────────────────────────┐
│              Docker Compose              │
│  ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
│  │  React  │ │ Django  │ │   Gateway   │ │
│  │  (80)   │ │ (8000)  │ │   (8080)    │ │
│  └─────────┘ └─────────┘ └─────────────┘ │
│  ┌─────────┐ ┌─────────┐               │
│  │Postgres │ │  Redis  │               │
│  │ (5432)  │ │ (6379)  │               │
│  └─────────┘ └─────────┘               │
└─────────────────────────────────────────┘
```
