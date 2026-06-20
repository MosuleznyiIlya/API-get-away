# System Design

## Request Lifecycle

1. Client отправляет запрос на Gateway Runtime
2. Gateway извлекает credentials из заголовков (API Key / JWT)
3. Происходит аутентификация и авторизация
4. Traffic Control проверяет лимиты запросов
5. Route Resolver определяет upstream-сервис
6. Cache проверяет наличие ответа в кэше
7. Proxy перенаправляет запрос к upstream
8. Metrics фиксирует метрики запроса
9. Logs записывает структурированный лог

## Gateway Runtime

Gateway Runtime — это middleware pipeline, который обрабатывает каждый входящий запрос через упорядоченную цепочку слоёв.

## Component Overview

### Authentication Layer
- API Key Validation: проверка ключа по префиксу и bcrypt hash
- JWT Validation: проверка подписи, срока действия, issuer

### Traffic Control Layer
- Rate Limiting: ограничение частоты запросов на основе Redis

### Routing Layer
- Path Matching: определение маршрута по path и HTTP методу
- Priority Rules: разрешение конфликтов маршрутов

### Proxy Layer
- Upstream communication: HTTP/HTTPS проксирование
- Header forwarding: служебные заголовки
- Timeout handling: управление таймаутами
- Retry logic: повторные попытки при ошибках upstream

### Observability Layer
- Structured Logs: единый формат логов с correlation ID
- Metrics: сбор счётчиков, latency, error rate
- Dashboard: визуализация метрик
