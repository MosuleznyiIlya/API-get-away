# Metrics

## Counters

### Request Counters

| Counter | Redis Key | Description |
|---------|-----------|-------------|
| Total Requests | `metrics:requests:minute:{timestamp}` | Запросы в минуту |
| Errors | `metrics:errors:minute:{timestamp}` | Ошибки в минуту |
| Cache Hits | `metrics:cache_hit:minute:{timestamp}` | Cache HIT в минуту |
| Cache Misses | `metrics:cache_miss:minute:{timestamp}` | Cache MISS в минуту |
| Rate Limit Hits | `metrics:rate_limit:minute:{timestamp}` | 429 ответы в минуту |

### Latency Aggregation

Redis Keys:
- `metrics:latency_sum:minute:{timestamp}` — сумма latency
- `metrics:latency_count:minute:{timestamp}` — количество запросов

Average latency вычисляется:
```
avg_latency = latency_sum / latency_count
```

### Example

```
metrics:latency_sum:minute:202606201830 = 85000
metrics:latency_count:minute:202606201830 = 2000

avg_latency = 85000 / 2000 = 42.5ms
```

## Latency Tracking

### Histogram Buckets

| Bucket | Range |
|--------|-------|
| lt_10ms | < 10ms |
| lt_50ms | < 50ms |
| lt_100ms | < 100ms |
| lt_200ms | < 200ms |
| lt_500ms | < 500ms |
| lt_1000ms | < 1000ms |
| gt_1000ms | > 1000ms |

### Percentiles

- p50 — медиана
- p95 — 95-й перцентиль
- p99 — 99-й перцентиль

## Cache Hit Rate

```
cache_hit_rate = cache_hits / (cache_hits + cache_misses)
```

## Rate Limit Hits

- Counter: `metrics:rate_limit:minute:{timestamp}`
- Alert threshold: > 100/min для одного клиента

## Redis Aggregation Model

### Per-Minute Aggregation

- Ключи хранятся с TTL = 24 часа (для Dashboard MVP)
- Production: TTL = 7 дней
- Ежечасная агрегация в PostgreSQL:
  - Таблица: `metrics_aggregated`
  - Поля: `hour`, `service_id`, `total_requests`, `avg_latency`, `error_rate`, `cache_hit_rate`

### Historical Aggregation

```sql
-- Ежечасная агрегация
INSERT INTO metrics_aggregated (hour, service_id, total_requests, avg_latency, error_rate)
SELECT 
  date_trunc('hour', timestamp) as hour,
  service_id,
  SUM(requests_total) as total_requests,
  AVG(request_duration_ms) as avg_latency,
  SUM(errors_total)::float / NULLIF(SUM(requests_total), 0) as error_rate
FROM metrics
WHERE timestamp > NOW() - INTERVAL '1 day'
GROUP BY hour, service_id;
```

## Dashboard API

### GET /api/v1/dashboard/metrics

Response:
```json
{
  "total_requests": 100000,
  "success_rate": 99.8,
  "error_rate": 0.2,
  "cache_hit_rate": 85.4,
  "average_latency_ms": 34
}
```

### GET /api/v1/dashboard/metrics/timeseries

Query Parameters:
```text
?period=1h
?period=24h
?period=7d
```

Response:
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

## Performance Metrics

### Target SLIs

| SLI | Target | Measurement |
|-----|--------|-------------|
| Availability | 99.9% | uptime / total_time |
| Latency (p50) | < 50ms | request_duration_ms |
| Latency (p95) | < 200ms | request_duration_ms |
| Error Rate | < 0.1% | errors / total_requests |
| Throughput | > 1000 RPS | requests / second |

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | > 1% | > 5% |
| Latency p95 | > 500ms | > 1000ms |
| Upstream Errors | > 10/min | > 50/min |
| Redis Latency | > 10ms | > 50ms |

## Redis Fallback Behavior

Если Redis недоступен:
- Метрики не агрегируются в real-time
- Логируется warning: `metrics_redis_unavailable`
- Gateway продолжает работу (fail-open)
- Метрики записываются напрямую в PostgreSQL (sync fallback, снижает throughput)
