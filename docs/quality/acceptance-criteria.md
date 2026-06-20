# Acceptance Criteria

## Services Module

### Create Service
- [ ] Администратор может создать сервис с именем и upstream URL
- [ ] Имя сервиса должно быть уникальным (alphanumeric + hyphens)
- [ ] Upstream URL должен быть валидным HTTP/HTTPS URL
- [ ] При успешном создании возвращается 201 с объектом сервиса
- [ ] При дублировании имени возвращается 409 Conflict
- [ ] При невалидных данных возвращается 400 Bad Request

### Update Service
- [ ] Администратор может обновить имя и upstream URL
- [ ] Валидация такая же, как при создании
- [ ] При несуществующем ID возвращается 404 Not Found
- [ ] При успешном обновлении возвращается 200 с обновленным объектом

### Delete Service
- [ ] Администратор может удалить сервис
- [ ] При удалении инвалидируются связанные маршруты и кэш
- [ ] При несуществующем ID возвращается 404 Not Found
- [ ] При успешном удалении возвращается 204 No Content

### List Services
- [ ] Пользователь может получить список сервисов с пагинацией
- [ ] Поддерживается фильтрация по is_active
- [ ] Поддерживается сортировка по created_at
- [ ] Максимальный page_size = 100

## Routes Module

### Create Route
- [ ] Администратор может создать маршрут с path, method, priority
- [ ] Path должен быть непустым строкой
- [ ] Method должен быть валидным HTTP методом
- [ ] Priority должен быть целым числом >= 0
- [ ] Route должен ссылаться на существующий сервис
- [ ] При успешном создании возвращается 201

### Route Resolution
- [ ] Gateway корректно определяет маршрут по path и method
- [ ] Приоритеты применяются в правильном порядке
- [ ] При отсутствии маршрута возвращается 404
- [ ] Неактивные маршруты игнорируются

## JWT Module

### Token Validation
- [ ] Gateway принимает валидный JWT токен
- [ ] Gateway отклоняет просроченный токен (401)
- [ ] Gateway отклоняет токен с невалидной подписью (401)
- [ ] Gateway отклоняет токен с невалидным issuer (401)
- [ ] Gateway отклоняет запрос без токена (401)
- [ ] Валидный токен добавляет user_id в request context

### Supported Algorithms
- [ ] HS256 поддерживается
- [ ] HS384 поддерживается (future)
- [ ] HS512 поддерживается (future)
- [ ] RS256 поддерживается (future)

## Rate Limiting Module

### Rate Limit Enforcement
- [ ] Gateway ограничивает запросы по API Key
- [ ] Gateway ограничивает запросы по JWT sub
- [ ] При превышении лимита возвращается 429
- [ ] Заголовки X-RateLimit-* добавляются в ответ
- [ ] Счетчик сбрасывается каждую минуту

### Redis Integration
- [ ] Rate limiting работает через Redis
- [ ] При недоступности Redis — fail open (пропускать)
- [ ] Счетчики корректно инкрементируются

## Caching Module

### Cache Storage
- [ ] Gateway кэширует GET ответы в Redis
- [ ] Cache key формируется корректно (method + path + query)
- [ ] TTL применяется согласно конфигурации маршрута
- [ ] POST/PUT/DELETE не кэшируются

### Cache Retrieval
- [ ] При cache hit Gateway возвращает кэшированный ответ
- [ ] При cache miss Gateway проксирует к upstream
- [ ] Заголовок X-Cache-Status добавляется (HIT/MISS)

### Cache Invalidation
- [ ] При обновлении сервиса инвалидируется связанный кэш
- [ ] При обновлении маршрута инвалидируется связанный кэш
- [ ] При отзыве API Key инвалидируется связанный кэш

## Logs Module

### Request Logging
- [ ] Каждый запрос логируется в PostgreSQL
- [ ] Лог содержит: request_id, method, path, status_code, latency_ms
- [ ] Лог содержит: client_ip, api_key_id, user_id, service_id, route_id
- [ ] Логи доступны через API с фильтрацией
- [ ] Логи хранятся 30 дней (retention)

### Audit Logging
- [ ] Создание/обновление/удаление сервиса логируется
- [ ] Создание/обновление/удаление маршрута логируется
- [ ] Создание/отзыв API Key логируется
- [ ] Audit logs хранятся 1 год

## Dashboard Module

### Metrics Display
- [ ] Dashboard отображает total requests (24h)
- [ ] Dashboard отображает average latency (1h)
- [ ] Dashboard отображает error rate (1h)
- [ ] Dashboard отображает cache hit ratio
- [ ] Dashboard отображает top 5 slowest routes
- [ ] Dashboard отображает rate limit events (1h)

### Real-time Updates
- [ ] Метрики обновляются каждые 30 секунд
- [ ] Данные кэшируются на 30 секунд
- [ ] При ошибке API отображается error state
- [ ] При загрузке отображается skeleton

### Navigation
- [ ] Sidebar содержит ссылки на все разделы
- [ ] Активный раздел подсвечивается
- [ ] Мобильная версия: hamburger menu
- [ ] Breadcrumbs на детальных страницах
