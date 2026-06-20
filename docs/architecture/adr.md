# Architecture Decision Records

## ADR-001: Django для Control Plane

**Status**: Accepted

**Context**: Необходим быстрый backend для CRUD операций с встроенной админкой.

**Decision**: Используем Django + Django REST Framework.

**Consequences**:
- (+) Быстрая разработка, встроенный ORM, админка
- (+) Зрелая экосистема, хорошая документация
- (-) Синхронный по умолчанию (используем gunicorn + gevent для async)

## ADR-002: PostgreSQL как основная БД

**Status**: Accepted

**Context**: Нужна надежная реляционная БД для структурированных данных.

**Decision**: PostgreSQL 14+.

**Consequences**:
- (+) ACID, сложные запросы, JSONB для гибких полей
- (+) Отличная интеграция с Django ORM
- (-) Требует миграций при изменении схемы

## ADR-003: Redis для Cache и Rate Limiting

**Status**: Accepted

**Context**: Нужен высокопроизводительный in-memory store для кэша и счетчиков.

**Decision**: Redis 7+.

**Consequences**:
- (+) SUB-millisecond latency
- (+) Встроенные структуры данных (strings, hashes, sorted sets)
- (+) TTL из коробки
- (-) Требует отдельного мониторинга и persistence

## ADR-004: React + TypeScript для Frontend

**Status**: Accepted

**Context**: Нужен современный типобезопасный фронтенд.

**Decision**: React 18 + TypeScript + Vite.

**Consequences**:
- (+) Компонентный подход, богатая экосистема
- (+) TypeScript предотвращает runtime ошибки
- (-) Требует настройки build pipeline

## ADR-005: Gateway Runtime как WSGI Middleware

**Status**: Accepted

**Context**: Нужен runtime прокси с middleware pipeline.

**Decision**: Django middleware + custom proxy handler.

**Consequences**:
- (+) Единый кодовый баз с Control Plane
- (+) Простота деплоя
- (-) Может потребоваться вынос в отдельный сервис при высоких нагрузках
