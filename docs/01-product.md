# API Gateway Platform

## Product Vision

Централизованный API Gateway для управления доступом к микросервисам.

## Goals

- JWT Validation
- API Key Management
- Rate Limiting
- Response Caching
- Request Logging
- Metrics Dashboard

## MVP Scope

- Services CRUD
- Routes CRUD
- API Keys CRUD
- Reverse Proxy
- JWT Validation
- Redis Cache
- Rate Limiting
- Logs
- Metrics

## Out Of Scope

- OAuth2
- OIDC
- Service Discovery
- Circuit Breaker
- Multi-Tenant

## Users

- **Platform Administrator** — управляет сервисами, маршрутами и ключами API
- **API Consumer** — использует API через Gateway с JWT или API Key
- **Developer** — интегрирует новые сервисы в Gateway

## User Stories

- Как администратор, я хочу создавать сервисы, чтобы регистрировать upstream-сервисы
- Как администратор, я хочу настраивать маршруты, чтобы определять правила проксирования
- Как администратор, я хочу управлять API Keys, чтобы контролировать доступ
- Как API Consumer, я хочу проходить JWT валидацию, чтобы безопасно вызывать API
- Как администратор, я хочу видеть метрики и логи, чтобы мониторить трафик

## Success Metrics

- Время отклика Gateway < 50ms (без кэша)
- Пропускная способность > 1000 RPS
- Доступность 99.9%
- Время развертывания нового сервиса < 5 минут

## Definition Of MVP

MVP включает:
1. Управление сервисами и маршрутами через Django Admin API
2. JWT и API Key аутентификацию
3. Rate Limiting на основе Redis
4. Response Caching через Redis
5. Reverse Proxy до upstream-сервисов
6. Логирование всех запросов в PostgreSQL
7. Базовый Dashboard метрик
