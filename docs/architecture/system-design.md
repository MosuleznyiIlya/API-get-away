# System Design

## Request Lifecycle

1. Client отправляет запрос на Gateway Runtime
2. Gateway извлекает JWT/API Key из заголовков
3. Происходит аутентификация и авторизация
4. Rate Limit проверяет лимиты запросов
5. Route Resolver определяет upstream-сервис
6. Cache проверяет наличие ответа в кэше
7. Proxy перенаправляет запрос к upstream
8. Metrics фиксирует метрики запроса
9. Logs записывает структурированный лог

## Gateway Runtime

Gateway Runtime — это WSGI/ASGI middleware pipeline, который обрабатывает каждый входящий запрос через серию слоев.

## Authentication Layer

- JWT Validation: проверка подписи, срока действия, issuer
- API Key Validation: поиск хэша ключа в БД, проверка статуса

## Traffic Control Layer

- Rate Limiting: алгоритм Token Bucket или Fixed Window на основе Redis
- Priority Rules: приоритет маршрутов по exact match > prefix match > wildcard

## Routing Layer

- Path Matching: точное совпадение, префикс, регулярные выражения
- Method Matching: HTTP методы (GET, POST, PUT, DELETE, PATCH)
- Priority Rules: порядок применения маршрутов

## Proxy Layer

- Upstream communication: HTTP/HTTPS проксирование
- Header forwarding: X-Forwarded-For, X-Request-ID
- Timeout handling: connect timeout, read timeout
- Retry logic: базовая логика повторных попыток

## Observability Layer

- Structured Logs: JSON формат, correlation ID
- Metrics: request count, latency, error rate, throughput
- Dashboard: визуализация метрик в React
