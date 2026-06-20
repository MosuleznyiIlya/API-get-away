# API Client

## HTTP Layer

Базовый HTTP клиент на основе Axios.

### Configuration

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## Error Handling

### Global Error Handler

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Redirect to login
          authStore.getState().logout();
          window.location.href = '/login';
          break;
        case 403:
          notificationStore.getState().addNotification({
            type: 'error',
            message: 'Access denied',
          });
          break;
        case 429:
          notificationStore.getState().addNotification({
            type: 'warning',
            message: 'Too many requests. Please wait.',
          });
          break;
        case 500:
          notificationStore.getState().addNotification({
            type: 'error',
            message: 'Server error. Please try again later.',
          });
          break;
        default:
          notificationStore.getState().addNotification({
            type: 'error',
            message: error.response.data?.message || 'An error occurred',
          });
      }
    }
    return Promise.reject(error);
  }
);
```

### Request Interceptors

```typescript
apiClient.interceptors.request.use(
  (config) => {
    const token = authStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

## Query Keys

### Convention

```typescript
// Format: [entity, params]
const queryKeys = {
  services: {
    all: ['services'] as const,
    lists: (params: ServiceListParams) => ['services', 'list', params] as const,
    detail: (id: string) => ['services', 'detail', id] as const,
  },
  routes: {
    all: ['routes'] as const,
    lists: (params: RouteListParams) => ['routes', 'list', params] as const,
    detail: (id: string) => ['routes', 'detail', id] as const,
  },
  apiKeys: {
    all: ['apiKeys'] as const,
    lists: (params: ApiKeyListParams) => ['apiKeys', 'list', params] as const,
  },
  logs: {
    all: ['logs'] as const,
    lists: (params: LogListParams) => ['logs', 'list', params] as const,
  },
  metrics: {
    all: ['metrics'] as const,
    dashboard: ['metrics', 'dashboard'] as const,
  },
};
```

### Usage with React Query

```typescript
// Service list
const useServices = (params: ServiceListParams) => {
  return useQuery({
    queryKey: queryKeys.services.lists(params),
    queryFn: () => servicesApi.getList(params),
  });
};

// Service detail
const useService = (id: string) => {
  return useQuery({
    queryKey: queryKeys.services.detail(id),
    queryFn: () => servicesApi.getById(id),
    enabled: !!id,
  });
};

// Create service
const useCreateService = () => {
  return useMutation({
    mutationFn: servicesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.services.all });
    },
  });
};
```

## API Services

```typescript
// servicesApi.ts
export const servicesApi = {
  getList: (params: ServiceListParams) => 
    apiClient.get<PaginatedResponse<Service>>('/services/', { params }),

  getById: (id: string) => 
    apiClient.get<Service>(`/services/${id}/`),

  create: (data: CreateServiceDto) => 
    apiClient.post<Service>('/services/', data),

  update: (id: string, data: UpdateServiceDto) => 
    apiClient.put<Service>(`/services/${id}/`, data),

  delete: (id: string) => 
    apiClient.delete(`/services/${id}/`),
};
```
