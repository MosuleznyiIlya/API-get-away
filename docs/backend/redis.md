1. Redis Architecture
Purpose

Redis is the primary runtime storage system for the API Gateway.

PostgreSQL stores the configuration.

Redis handles hot operations:

Response Cache
Rate Limiting
Metrics Aggregation
API Key Runtime Cache
Route Configuration Cache (optional)
High Level Architecture
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
Redis Responsibilities
Cache Layer

Storing API responses.

Rate Limiting

Storing Token Buckets.

Metrics

Storing aggregated metrics.

Runtime Optimization

Caching API Keys.

What Redis MUST NOT Store

Must NOT store:

services
routes
request_logs
audit_logs

The single source of truth is PostgreSQL only.

Redis is an accelerator.

2. Key Naming Convention

General rule:

<namespace>:<entity>:<identifier>
Cache
cache:response:{hash}

Example:

cache:response:f48d67aa8b
Rate Limiting
rl:apikey:{api_key_id}

Example:

rl:apikey:4d9a7f
Metrics
metrics:requests:minute:{timestamp}
metrics:errors:minute:{timestamp}
metrics:latency:minute:{timestamp}
metrics:cache_hit:minute:{timestamp}
API Key Cache
apikey:{hash}
Future
health:service:{service_id}

circuit_breaker:{service_id}

discovery:{service_name}
3. Cache Strategy
Goal

Reduce load on backend services.

What is cached

Only:

GET

Not cached:

POST
PUT
PATCH
DELETE
Cache Key

Base:

method
path
querystring

Formation:

SHA256(
GET +
/api/users +
?page=1
)

Resulting key:

cache:response:8a7f6e4d
Cache Value

Structure:

{
  "status_code": 200,
  "headers": {},
  "body": "...",
  "created_at": 1710000000
}
TTL Strategy

Configured per route.

Examples:

Endpoint	TTL
/users	60s
/products	300s
/settings	30s
Cache Flow
Request

 ↓

Cache Lookup

 ↓

Hit ?
 │
 ├── YES → Return
 │
 └── NO
       ↓
   Proxy Request
       ↓
   Store Cache
       ↓
   Return Response
4. Rate Limiter Strategy
Algorithm

For MVP:

Token Bucket

Reasons:

supports bursts
predictable behavior
scales well
Key
rl:apikey:{id}

Example

rl:apikey:8f47d2
Value Structure
{
  "tokens": 84,
  "capacity": 100,
  "last_refill": 1710000000
}
Runtime Flow
Request

 ↓

Load Bucket

 ↓

Refill Tokens

 ↓

Token Available?

 ↓

YES → Consume Token

NO → 429
Why Redis

All Gateway instances use a shared bucket.

Gateway-1
Gateway-2
Gateway-3
Gateway-4

      ↓

    Redis

Rate limiting remains consistent.

5. Metrics Strategy
Goal

Avoid heavy aggregations over request_logs.

Instead, use realtime counters.

Requests Counter

Key:

metrics:requests:minute:202606201830

Value:

523
Errors Counter
metrics:errors:minute:202606201830

Value:

17
Cache Hits
metrics:cache_hit:minute:202606201830

Value:

421
Rate Limit Hits
metrics:rate_limit:minute:202606201830

Value:

12
Latency Aggregation

Store:

metrics:latency_sum:minute:{timestamp}

metrics:latency_count:minute:{timestamp}

Example

latency_sum = 85000

latency_count = 2000

Average is computed:

85000 / 2000

= 42.5ms
6. Expiration Policies
Cache

TTL depends on the route.

Range:

30s - 3600s

After expiration:

Automatic Eviction
Rate Limiter

TTL:

2 × refill window

Example:

100 rpm

Window:

60 seconds

TTL:

120 seconds

Inactive users are automatically cleaned up.

Metrics

TTL:

24 hours

For Dashboard MVP.

Production:

7 days
API Key Cache

TTL:

300 seconds

After key deactivation:

Forced Invalidation
7. Memory Usage Estimation
Cache

Assumptions:

10000 objects

average response 5 KB

Memory:

≈ 50 MB
Rate Limiting
10000 API Keys

Bucket size:

≈ 200 bytes

Memory:

≈ 2 MB
Metrics

1 day.

Per-minute metrics.

1440 buckets/day

Per metric:

~100 bytes

Memory:

< 1 MB
API Key Cache
10000 keys

Size:

~300 bytes

Memory:

≈ 3 MB
Total MVP
Cache          50 MB
Rate Limiting   2 MB
Metrics         1 MB
API Keys        3 MB
≈ 60 MB

Even Redis with:

256 MB RAM

will have a large margin.

8. Failure Recovery Strategy
Scenario 1
Redis Down

Consequences:

Cache unavailable

Rate limiting unavailable

Metrics unavailable

Gateway behavior:

Fail Open

Continue serving requests.

Reason:

Better to lose cache and metrics
than to stop the entire API Gateway.

Scenario 2
Redis Restart

After restart, the following are lost:

cache
rate limits
metrics

Recovery:

Automatic Rebuild

No manual actions required.

Scenario 3
Memory Full

Policy:

allkeys-lru

First removed:

old cache entries

Rate Limiter and Metrics must have high storage priority.

Scenario 4
Network Partition

Gateway temporarily loses Redis.

Behavior:

Cache Bypass

Rate Limit Bypass

Metrics Skip

Log event:

redis_unavailable
Cleanup Scenarios
Cache

Automatically removed by TTL.

Additionally:

route update
route delete
service disable

→ forced cleanup of related cache keys.

Rate Limiter

Automatically removed after TTL expiration.

Metrics

Automatically removed by TTL.

API Key Cache

Removed on:

api key revoke
api key delete
api key deactivate
Production Evolution
V2
Redis Persistence

AOF
V3
Redis Sentinel

High availability.
V4
Redis Cluster

Horizontal scaling.
Redis Design Decisions
RD-001

Redis is used only as runtime storage.

RD-002

Cache is the largest memory consumer.

RD-003

Rate Limiting is stored centrally in Redis.

RD-004

Metrics are aggregated in Redis, not computed from request_logs.

RD-005

If Redis fails, the Gateway operates in Fail Open mode to avoid blocking client traffic.
