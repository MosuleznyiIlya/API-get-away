# Routing

## Route Resolution

Route Resolver определяет upstream-сервис для входящего запроса на основе path и HTTP метода.

## Path Matching

### Exact Match
```
Path: /api/v1/users
Request: GET /api/v1/users
Result: MATCH
```

### Prefix Match
```
Path: /api/v1/users/*
Request: GET /api/v1/users/123
Result: MATCH
```

### Wildcard Match
```
Path: /api/v1/*
Request: GET /api/v1/orders/456
Result: MATCH
```

### Regex Match (Future)
```
Path: /api/v1/users/\d+
Request: GET /api/v1/users/123
Result: MATCH
```

## Method Matching

Маршрут может поддерживать:
- Один метод: `GET`
- Несколько методов: `GET, POST`
- Все методы: `*` или `ANY`

Приоритет: Exact method > ANY

## Priority Rules

Маршруты оцениваются в порядке приоритета (priority — чем меньше число, тем выше приоритет):

1. **Exact Path + Exact Method** (priority = 1)
2. **Exact Path + ANY Method** (priority = 2)
3. **Prefix Match + Exact Method** (priority = 10)
4. **Prefix Match + ANY Method** (priority = 11)
5. **Wildcard Match + Exact Method** (priority = 20)
6. **Wildcard Match + ANY Method** (priority = 21)

### Resolution Algorithm

```python
def resolve_route(request_path, request_method):
    candidates = routes.filter(
        path_matches(request_path),
        method_matches(request_method),
        is_active=True
    ).order_by('priority')

    return candidates.first()
```

### Conflict Resolution

Если два маршрута имеют одинаковый priority:
- Выбирается тот, что был создан раньше (created_at)
- В админке отображается WARNING

### Cache Invalidation

При изменении маршрутов:
- Очистка route cache в Redis
- Перезагрузка конфигурации в Gateway Runtime
- Graceful reload без потери активных соединений
