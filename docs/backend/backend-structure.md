# Backend Structure

## Repository Structure

```
gateway/
├── apps/
│   ├── services/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── routes/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── auth/
│   │   ├── jwt.py
│   │   ├── api_keys.py
│   │   └── middleware.py
│   ├── ratelimit/
│   │   ├── models.py
│   │   ├── algorithms.py
│   │   └── middleware.py
│   ├── cache/
│   │   ├── models.py
│   │   ├── strategies.py
│   │   └── middleware.py
│   ├── proxy/
│   │   ├── client.py
│   │   └── middleware.py
│   ├── logs/
│   │   ├── models.py
│   │   ├── middleware.py
│   │   └── tasks.py
│   ├── metrics/
│   │   ├── models.py
│   │   ├── aggregators.py
│   │   └── middleware.py
│   └── dashboard/
│       ├── views.py
│       └── urls.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── Dockerfile
```

## Django Apps

| App | Responsibility | Allowed | Forbidden |
|-----|---------------|---------|-----------|
| **services** | Service Registry | CRUD Services | Routing, Cache, JWT, Rate Limiting |
| **routes** | Route Configuration | Route CRUD, Route Resolution Rules | Proxy Execution |
| **api_keys** | API Key Management | Generate, Rotate, Revoke, Validate Metadata | Rate Limiting logic |
| **auth** | Authentication | JWT Validation, API Key Validation | Cache, Proxy, Metrics |
| **ratelimit** | Traffic Control | Token Bucket algorithms | Business logic |
| **cache** | Response Cache | Cache strategies, invalidation | Upstream communication |
| **proxy** | Reverse Proxy | HTTP client, header forwarding, timeouts | Route resolution |
| **logs** | Structured Logging | JSON logs, async write, retention | Log analysis |
| **metrics** | Metrics Collection | Counters, latency, aggregation | Dashboard rendering |
| **dashboard** | Admin Dashboard API | Read-only metrics aggregation | Direct DB queries |

## Module Boundaries

Каждый app имеет чёткие границы:
- Модели только внутри своего app
- Сервисный слой для бизнес-логики
- Views только для HTTP адаптации
- Middleware для cross-cutting concerns

## Import Rules

- Внутри app: свободные импорты
- Между apps: только через service layer
- Gateway Runtime импортирует middleware из apps в строгом порядке
- Запрещены циклические зависимости между apps
