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

- **services** — CRUD upstream-сервисов
- **routes** — CRUD маршрутов проксирования
- **auth** — JWT и API Key валидация
- **ratelimit** — алгоритмы ограничения частоты
- **cache** — стратегии кэширования
- **proxy** — HTTP клиент для upstream
- **logs** — структурированное логирование
- **metrics** — сбор и агрегация метрик
- **dashboard** — API для админ-панели

## Module Boundaries

Каждый app имеет четкие границы:
- Модели только внутри своего app
- Сервисный слой для бизнес-логики
- Views только для HTTP адаптации
- Middleware для cross-cutting concerns

## Import Rules

- Внутри app: свободные импорты
- Между apps: только через service layer
- Gateway Runtime импортирует middleware из apps в строгом порядке
- Запрещены циклические зависимости между apps
