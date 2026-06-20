# Architecture

## High Level Architecture

```
React
  |
Django API
  |
Postgres
Redis
Gateway Runtime
```

## Control Plane

Services CRUD, Routes CRUD, API Keys, Metrics API.

## Data Plane

JWT, API Key Validation, Rate Limiting, Cache, Proxy.

## Component Overview

- **React Admin** — фронтенд панель управления
- **Django Control Plane** — REST API для управления конфигурацией
- **PostgreSQL** — хранение сервисов, маршрутов, ключей, логов, метрик
- **Redis** — кэш, rate limiting counters, сессии
- **Gateway Runtime** — runtime прокси с middleware pipeline

## Technology Decisions

- **Django** — быстрая разработка, встроенный ORM, админка
- **PostgreSQL** — надежная реляционная БД для структурированных данных
- **Redis** — высокопроизводительный кэш и хранилище счетчиков
- **React** — современный UI с TypeScript
- **TypeScript** — типобезопасность на фронтенде

## System Boundaries

Внутри: Gateway Platform.

Снаружи: User Service, Order Service, Billing Service.
