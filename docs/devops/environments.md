# Environments

## Development

- **URL**: http://localhost:8000 (backend), http://localhost:3000 (frontend)
- **Database**: Local PostgreSQL или Docker
- **Redis**: Local или Docker
- **Debug**: True
- **Logs**: Console, DEBUG level
- **Features**: Hot reload, debug toolbar

## Staging

- **URL**: https://staging.gateway.example.com
- **Database**: Staging PostgreSQL (managed)
- **Redis**: Staging Redis (managed)
- **Debug**: False
- **Logs**: Structured JSON, INFO level
- **Features**: Same as production, limited data

## Production

- **URL**: https://gateway.example.com
- **Database**: Production PostgreSQL (managed, HA)
- **Redis**: Production Redis (managed, cluster)
- **Debug**: False
- **Logs**: Structured JSON, WARN level
- **Features**: Full monitoring, alerting, backups

## Environment Configuration

| Parameter | Development | Staging | Production |
|-----------|-------------|---------|------------|
| DEBUG | True | False | False |
| LOG_LEVEL | DEBUG | INFO | WARN |
| RATE_LIMIT | 10000/min | 1000/min | 1000/min |
| CACHE_TTL | 60s | 300s | 300s |
| DB_POOL_SIZE | 5 | 20 | 50 |
| WORKERS | 1 | 4 | 8 |
