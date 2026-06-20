# Monitoring

## Logging

### Centralized Logging

- **Stack**: ELK (Elasticsearch, Logstash, Kibana) или Loki + Grafana
- **Format**: Structured JSON
- **Shipping**: Filebeat или Fluentd
- **Retention**: 30 days hot, 90 days warm, 1 year cold

### Log Levels by Environment

| Environment | Level | Destination |
|-------------|-------|-------------|
| Development | DEBUG | Console |
| Staging | INFO | File + ELK |
| Production | WARN | File + ELK |

## Metrics

### Current Metrics

- Request count, latency, error rate (внутренние)
- Cache hit/miss ratio
- Rate limit events
- Upstream health status

### Future Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Metrics to Export

| Metric | Type | Labels |
|--------|------|--------|
| `gateway_requests_total` | Counter | method, path, status |
| `gateway_request_duration_seconds` | Histogram | method, path |
| `gateway_cache_hits_total` | Counter | route |
| `gateway_cache_misses_total` | Counter | route |
| `gateway_rate_limit_hits_total` | Counter | route |
| `gateway_upstream_errors_total` | Counter | service, error_type |
| `gateway_db_connections_active` | Gauge | — |
| `gateway_redis_connections_active` | Gauge | — |

## Future Prometheus

### Architecture

```
Prometheus -> Scrapes -> Gateway /metrics
         -> Scrapes -> Backend /metrics
         -> Scrapes -> Postgres Exporter
         -> Scrapes -> Redis Exporter

Prometheus -> Stores -> TSDB

Grafana -> Queries -> Prometheus
        -> Displays -> Dashboards
```

### Alerting Rules

```yaml
# alerts.yml
groups:
  - name: gateway
    rules:
      - alert: HighErrorRate
        expr: rate(gateway_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(gateway_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"
```

## Future Grafana

### Dashboards

1. **Gateway Overview**
   - Requests per second
   - Error rate
   - Latency (p50, p95, p99)
   - Active connections

2. **Cache Performance**
   - Hit ratio
   - Miss ratio
   - Cache size
   - Eviction rate

3. **Rate Limiting**
   - Limited requests per minute
   - Allowed vs denied ratio
   - Top limited clients

4. **Upstream Health**
   - Upstream response time
   - Upstream error rate
   - Upstream availability

5. **Database Performance**
   - Query duration
   - Active connections
   - Lock waits
   - Transaction rate

### Panels

| Panel | Query | Visualization |
|-------|-------|---------------|
| RPS | `rate(gateway_requests_total[1m])` | Graph |
| Error Rate | `rate(gateway_requests_total{status=~"5.."}[5m])` | Graph |
| P95 Latency | `histogram_quantile(0.95, rate(gateway_request_duration_seconds_bucket[5m]))` | Graph |
| Cache Hit Ratio | `gateway_cache_hits_total / (gateway_cache_hits_total + gateway_cache_misses_total)` | Gauge |
| Upstream Errors | `rate(gateway_upstream_errors_total[5m])` | Graph |
