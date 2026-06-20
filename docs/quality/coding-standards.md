# Coding Standards

## Python Standards

### Style Guide
- **PEP 8** — стандартный стиль Python
- **Line Length**: 88 символов (Black formatter)
- **Quotes**: Double quotes для строк
- **Imports**: isort (stdlib, third-party, local)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `services.py` |
| Classes | PascalCase | `ServiceManager` |
| Functions | snake_case | `get_service_by_id` |
| Variables | snake_case | `service_name` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private | _leading_underscore | `_internal_method` |

### Type Hints
- Обязательны для всех функций и методов
- Используем `typing` module
- `Optional`, `List`, `Dict`, `Union` из `typing`

```python
from typing import Optional, List, Dict

def get_service(service_id: str) -> Optional[Service]:
    ...

def list_services(filters: Dict[str, str]) -> List[Service]:
    ...
```

## Django Standards

### App Structure
```
app_name/
├── __init__.py
├── models.py          # Только модели
├── views.py           # Только view functions/classes
├── serializers.py     # DRF serializers
├── urls.py            # URL patterns
├── services.py        # Business logic
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services.py
```

### Model Standards
- Всегда использовать `UUID` для primary keys
- `created_at` и `updated_at` для всех моделей
- `Meta.verbose_name` и `Meta.verbose_name_plural`
- `__str__` метод для всех моделей

```python
class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
```

### View Standards
- Использовать Class-Based Views (APIView, ViewSet)
- Тонкие views — бизнес-логика в services.py
- Всегда использовать serializers для валидации

## React Standards

### Component Structure
```typescript
// Imports
import React from 'react';
import { useQuery } from '@tanstack/react-query';

// Types
interface Props {
  serviceId: string;
  onUpdate?: () => void;
}

// Component
export const ServiceCard: React.FC<Props> = ({ serviceId, onUpdate }) => {
  // Hooks
  const { data, isLoading } = useService(serviceId);

  // Handlers
  const handleUpdate = () => {
    onUpdate?.();
  };

  // Render
  if (isLoading) return <ServiceCardSkeleton />;

  return (
    <div className="service-card">
      <h3>{data.name}</h3>
      <button onClick={handleUpdate}>Update</button>
    </div>
  );
};
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `ServiceCard.tsx` |
| Hooks | camelCase, use prefix | `useServices.ts` |
| Utils | camelCase | `formatDate.ts` |
| Types | PascalCase | `Service.ts` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL` |
| Styled | PascalCase, Styled prefix | `StyledButton` |

## TypeScript Standards

### Type Definitions
```typescript
// Interfaces для объектов
interface Service {
  id: string;
  name: string;
  upstreamUrl: string;
  isActive: boolean;
  createdAt: Date;
}

// Types для unions
type Status = 'active' | 'inactive' | 'pending';

// Enums для констант
enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
}
```

### Strict Mode
- `strict: true` в tsconfig.json
- `noImplicitAny: true`
- `strictNullChecks: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`

## Naming Rules

### General
- Имена должны быть описательными и понятными
- Избегать сокращений (кроме общепринятых: id, url, http)
- Использовать глаголы для функций (get, create, update, delete)
- Использовать существительные для переменных и классов

### Database
- Таблицы: snake_case, множественное число (`services`, `api_keys`)
- Колонки: snake_case (`created_at`, `upstream_url`)
- Индексы: `idx_{table}_{column}` (`idx_services_name`)
- Constraints: `fk_{table}_{ref_table}` (`fk_routes_services`)

## Folder Rules

### Backend
- Каждый app — отдельная директория в `apps/`
- Бизнес-логика — в `services.py`
- Тесты — в `tests/` внутри app
- Миграции — в `migrations/`, только через `makemigrations`

### Frontend
- `pages/` — страницы (routing)
- `features/` — feature-based модули
- `components/` — переиспользуемые компоненты
- `hooks/` — custom hooks
- `services/` — API clients
- `stores/` — state management
- `types/` — TypeScript types
- `utils/` — утилиты
