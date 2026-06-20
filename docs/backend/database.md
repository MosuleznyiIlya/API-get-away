# Database

## Entities

### services
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Идентификатор сервиса |
| name | VARCHAR(255) | Уникальное имя |
| upstream_url | VARCHAR(500) | URL upstream-сервиса |
| health_check_url | VARCHAR(500) | URL проверки здоровья |
| is_active | BOOLEAN | Активен ли сервис |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### routes
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Идентификатор маршрута |
| service_id | UUID FK | Ссылка на сервис |
| path | VARCHAR(500) | Путь маршрута |
| method | VARCHAR(10) | HTTP метод |
| priority | INTEGER | Приоритет (чем меньше, тем выше) |
| is_active | BOOLEAN | Активен ли маршрут |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### api_keys
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Идентификатор ключа |
| name | VARCHAR(255) | Название ключа |
| key_hash | VARCHAR(255) | Хэш ключа (bcrypt) |
| prefix | VARCHAR(10) | Префикс для идентификации |
| is_active | BOOLEAN | Активен ли ключ |
| rate_limit | INTEGER | Лимит запросов в минуту |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### request_logs
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Идентификатор лога |
| request_id | VARCHAR(255) | Correlation ID |
| method | VARCHAR(10) | HTTP метод |
| path | VARCHAR(500) | Путь запроса |
| status_code | INTEGER | HTTP статус |
| latency_ms | INTEGER | Задержка в мс |
| client_ip | VARCHAR(45) | IP клиента |
| api_key_id | UUID FK | Ссылка на API Key (nullable) |
| user_id | VARCHAR(255) | JWT sub (nullable) |
| service_id | UUID FK | Ссылка на сервис (nullable) |
| route_id | UUID FK | Ссылка на маршрут (nullable) |
| created_at | TIMESTAMP | Дата создания |

### metrics
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Идентификатор метрики |
| name | VARCHAR(255) | Название метрики |
| value | FLOAT | Значение |
| labels | JSONB | Метки (service, route, status) |
| timestamp | TIMESTAMP | Время сбора |

## Relationships

- `routes.service_id` → `services.id` (Many-to-One)
- `request_logs.api_key_id` → `api_keys.id` (Many-to-One, nullable)
- `request_logs.service_id` → `services.id` (Many-to-One, nullable)
- `request_logs.route_id` → `routes.id` (Many-to-One, nullable)

## Indexes

- `services(name)` — UNIQUE
- `routes(service_id, path, method)` — UNIQUE
- `api_keys(prefix)` — UNIQUE
- `api_keys(key_hash)` — INDEX
- `request_logs(created_at)` — INDEX (для retention)
- `request_logs(request_id)` — INDEX
- `metrics(timestamp, name)` — INDEX

## Constraints

- `routes.path` — NOT NULL
- `routes.method` — CHECK IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')
- `api_keys.rate_limit` — CHECK > 0
- `request_logs.status_code` — CHECK BETWEEN 100 AND 599
- `request_logs.latency_ms` — CHECK >= 0

## Migration Rules

- Все миграции через Django migrations
- Именование: `0001_initial.py`, `0002_add_field.py`
- Запрещены необратимые операции в production без бэкапа
- Добавление новых полей — только nullable или с default
- Индексы создаются отдельно от изменения схемы (CONCURRENTLY)
