# Metrics

## Metrics Model

### Request Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `gateway_requests_total` | Counter | service, route, method, status | Общее количество запросов |
| `gateway_request_duration_ms` | Histogram | service, route | Время обработки запроса |
| `gateway_request_size_bytes` | Histogram | service | Размер входящего запроса |
| `gateway_response_size_bytes` | Histogram | service | Размер ответа |

### Cache Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `gateway_cache_hits_total` | Counter | route | Количество cache hits |
| `gateway_cache_misses_total` | Counter | route | Количество cache misses |
| `gateway_cache_size_bytes` | Gauge | route | Размер кэша |

### Rate Limit Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `gateway_rate_limit_hits_total` | Counter | route, client | Количество срабатываний rate limit |
| `gateway_rate_limit_allowed_total` | Counter | route, client | Количество разрешенных запросов |

### Error Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `gateway_errors_total` | Counter | service, error_type | Количество ошибок |
| `gateway_upstream_errors_total` | Counter | service, error_type | Ошибки upstream |

## Aggregation

### Real-time Aggregation

Агрегация в течение 1 минутного окна:
- SUM(requests_total)
- AVG(request_duration_ms)
- PERCENTILE(request_duration_ms, 95)
- SUM(errors_total) / SUM(requests_total) = error_rate

### Historical Aggregation

Ежечасная агрегация:
- Сохранение в таблицу `metrics_aggregated`
- Поля: hour, service_id, total_requests, avg_latency, error_rate

## Dashboard Metrics

### Key Metrics for Dashboard

1. **Total Requests (Last 24h)**
   - Query: SUM(requests_total) WHERE timestamp > NOW() - 24h

2. **Average Latency (Last 1h)**
   - Query: AVG(request_duration_ms) WHERE timestamp > NOW() - 1h

3. **Error Rate (Last 1h)**
   - Query: SUM(errors_total) / SUM(requests_total) WHERE timestamp > NOW() - 1h

4. **Top 5 Slowest Routes**
   - Query: AVG(request_duration_ms) GROUP BY route ORDER BY avg DESC LIMIT 5

5. **Cache Hit Ratio**
   - Query: SUM(cache_hits) / (SUM(cache_hits) + SUM(cache_misses))

6. **Rate Limit Events**
   - Query: SUM(rate_limit_hits) WHERE timestamp > NOW() - 1h

### API Endpoints

```
GET /api/v1/metrics/dashboard
Response:
{
  "total_requests_24h": 150000,
  "avg_latency_1h_ms": 45.2,
  "error_rate_1h": 0.01,
  "cache_hit_ratio": 0.75,
  "top_slowest_routes": [
    {"route": "/api/v1/orders", "avg_latency_ms": 120.5}
  ],
  "rate_limit_events_1h": 45
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
