# Redis Infrastructure

## Redis Architecture

Redis является runtime storage для API Gateway. PostgreSQL хранит конфигурацию.

### High Level Architecture

```
                   Gateway Runtime
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
      Cache          Rate Limiter        Metrics
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                        Redis
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
      Strings            Hashes            Counters
```

### Redis Responsibilities

- **Cache Layer** — хранение API responses
- **Rate Limiting** — хранение Token Buckets
- **Metrics** — хранение агрегированных метрик
- **Runtime Optimization** — кэширование API Keys

### What Redis MUST NOT Store

- `services` — PostgreSQL only
- `routes` — PostgreSQL only
- `request_logs` — PostgreSQL only
- `audit_logs` — PostgreSQL only

Redis is an accelerator, not source of truth.

## Memory Usage Estimation

### MVP

| Component | Objects | Avg Size | Memory |
|-----------|---------|----------|--------|
| Cache | 10 000 | 5 KB | ≈ 50 MB |
| Rate Limiting | 10 000 | 200 B | ≈ 2 MB |
| Metrics | 1 440/min | 100 B | < 1 MB |
| API Key Cache | 10 000 | 300 B | ≈ 3 MB |
| **Total** | | | **≈ 60 MB** |

Even Redis with 256 MB RAM will have a large margin.

## Failure Recovery Strategy

### Scenario 1: Redis Down

**Consequences:**
- Cache unavailable
- Rate limiting unavailable
- Metrics unavailable

**Gateway behavior:**
- Fail Open
- Continue serving requests
- Better to lose cache and metrics than to stop the entire API Gateway

### Scenario 2: Redis Restart

**Lost after restart:**
- Cache
- Rate limits
- Metrics

**Recovery:**
- Automatic Rebuild
- No manual actions required

### Scenario 3: Memory Full

**Policy:** `allkeys-lru`

**First removed:**
- Old cache entries

**High priority (not evicted first):**
- Rate Limiter buckets
- Metrics counters

### Scenario 4: Network Partition

**Behavior:**
- Cache Bypass
- Rate Limit Bypass
- Metrics Skip

**Log event:** `redis_unavailable`

## Production Evolution

### V2: Redis Persistence

- AOF (Append Only File)
- RDB snapshots

### V3: Redis Sentinel

- High availability
- Automatic failover

### V4: Redis Cluster

- Horizontal scaling
- Sharding

## Redis Design Decisions

| ID | Decision |
|----|----------|
| RD-001 | Redis is used only as runtime storage |
| RD-002 | Cache is the largest memory consumer |
| RD-003 | Rate Limiting is stored centrally in Redis |
| RD-004 | Metrics are aggregated in Redis, not computed from request_logs |
| RD-005 | If Redis fails, the Gateway operates in Fail Open mode |
