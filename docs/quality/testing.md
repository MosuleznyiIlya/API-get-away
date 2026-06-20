# Testing

## Unit Tests

### Backend (Python/Django)

#### Test Structure
```
gateway/
├── apps/
│   ├── services/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   ├── test_serializers.py
│   │   │   └── test_services.py
```

#### Model Tests
```python
import pytest
from django.test import TestCase
from apps.services.models import Service

class ServiceModelTests(TestCase):
    def test_service_creation(self):
        service = Service.objects.create(
            name='test-service',
            upstream_url='http://localhost:8080'
        )
        self.assertEqual(service.name, 'test-service')
        self.assertTrue(service.is_active)
        self.assertIsNotNone(service.created_at)

    def test_service_unique_name(self):
        Service.objects.create(name='test', upstream_url='http://localhost:8080')
        with self.assertRaises(IntegrityError):
            Service.objects.create(name='test', upstream_url='http://localhost:8081')
```

#### Service Tests
```python
class ServiceServiceTests(TestCase):
    def test_get_service_by_id(self):
        service = ServiceFactory()
        result = ServiceService.get_by_id(service.id)
        self.assertEqual(result, service)

    def test_get_service_not_found(self):
        with self.assertRaises(ServiceNotFoundError):
            ServiceService.get_by_id('non-existent-uuid')
```

#### View Tests
```python
class ServiceViewTests(APITestCase):
    def test_list_services(self):
        ServiceFactory.create_batch(5)
        response = self.client.get('/api/v1/services/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)

    def test_create_service_unauthorized(self):
        response = self.client.post('/api/v1/services/', {
            'name': 'test',
            'upstream_url': 'http://localhost:8080'
        })
        self.assertEqual(response.status_code, 401)
```

### Frontend (React/TypeScript)

#### Component Tests
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ServiceCard } from './ServiceCard';

describe('ServiceCard', () => {
  const mockService = {
    id: '1',
    name: 'Test Service',
    upstreamUrl: 'http://localhost:8080',
    isActive: true,
  };

  it('renders service name', () => {
    render(<ServiceCard service={mockService} />);
    expect(screen.getByText('Test Service')).toBeInTheDocument();
  });

  it('calls onUpdate when clicked', () => {
    const onUpdate = jest.fn();
    render(<ServiceCard service={mockService} onUpdate={onUpdate} />);
    fireEvent.click(screen.getByText('Update'));
    expect(onUpdate).toHaveBeenCalled();
  });
});
```

#### Hook Tests
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useServices } from './useServices';

describe('useServices', () => {
  it('returns services list', async () => {
    const { result } = renderHook(() => useServices());
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(5);
  });
});
```

## Integration Tests

### API Integration Tests

```python
import pytest
from django.test import TestCase
from rest_framework.test import APITestCase

class GatewayIntegrationTests(APITestCase):
    def test_full_request_flow(self):
        # Setup
        service = ServiceFactory(upstream_url='http://mock-server:8080')
        route = RouteFactory(service=service, path='/api/v1/users', method='GET')
        api_key = ApiKeyFactory()

        # Execute
        response = self.client.get(
            '/api/v1/users',
            HTTP_X_API_KEY=api_key.key
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Request-ID', response.headers)

        # Verify log was created
        self.assertEqual(RequestLog.objects.count(), 1)
        log = RequestLog.objects.first()
        self.assertEqual(log.status_code, 200)
```

### Gateway Runtime Integration Tests

```python
class GatewayRuntimeTests(TestCase):
    def test_jwt_validation_flow(self):
        token = generate_test_token(user_id='user_123')
        response = self.client.get(
            '/api/v1/users',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)

    def test_rate_limiting_flow(self):
        api_key = ApiKeyFactory(rate_limit=5)

        # 5 requests should pass
        for _ in range(5):
            response = self.client.get(
                '/api/v1/users',
                HTTP_X_API_KEY=api_key.key
            )
            self.assertEqual(response.status_code, 200)

        # 6th request should be rate limited
        response = self.client.get(
            '/api/v1/users',
            HTTP_X_API_KEY=api_key.key
        )
        self.assertEqual(response.status_code, 429)
```

## Coverage Rules

### Minimum Coverage

| Module | Minimum Coverage |
|--------|-----------------|
| Models | 95% |
| Services | 90% |
| Views/API | 85% |
| Serializers | 90% |
| Middleware | 80% |
| Frontend Components | 80% |
| Frontend Hooks | 85% |

### Coverage Exclusions

- Миграции
- Фабрики (test fixtures)
- Конфигурация (settings, urls)
- Сгенерированный код

### Coverage Report

```bash
# Backend
pytest --cov=gateway --cov-report=html --cov-report=term-missing

# Frontend
npm run test -- --coverage --watchAll=false
```

## Test Structure

### Test Naming

```python
# Format: test_{action}_{expected_result}
def test_create_service_with_valid_data_returns_201():
    ...

def test_create_service_with_duplicate_name_returns_409():
    ...

def test_get_service_with_nonexistent_id_returns_404():
    ...
```

### Test Data

- Использовать factories (factory_boy, faker)
- Не использовать production data
- Очищать данные после каждого теста (transactions)

### Test Isolation

- Каждый тест должен быть независимым
- Не полагаться на порядок выполнения
- Использовать setUp/tearDown для инициализации

### Test Performance

- Unit tests < 100ms
- Integration tests < 1s
- Использовать pytest-xdist для параллельного выполнения
