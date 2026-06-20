# State Management

## React Query Responsibilities

React Query (TanStack Query) используется для:

### Server State
- **Кэширование API данных** — автоматическое кэширование запросов
- **Background Refetching** — обновление данных при фокусе окна
- **Pagination** — управление страницами (infinite query)
- **Optimistic Updates** — оптимистичные обновления при mutations
- **Error Handling** — автоматическая обработка ошибок и retry

### Query Keys
```typescript
// Services
['services', { page, pageSize, isActive }]
['services', id] // single service

// Routes
['routes', { page, pageSize, serviceId }]
['routes', id]

// API Keys
['apiKeys', { page, pageSize }]

// Logs
['logs', { page, pageSize, filters }]

// Metrics
['metrics', { period, name }]
['dashboardMetrics']
```

## Zustand Responsibilities

Zustand используется для:

### Client State
- **Auth State** — текущий пользователь, JWT токен, статус аутентификации
- **UI State** — открытие/закрытие sidebar, модальные окна, theme
- **Notification State** — toast уведомления (success, error, warning)
- **Form State** — draft форм, валидация

### Stores

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

// uiStore.ts
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

// notificationStore.ts
interface NotificationState {
  notifications: Notification[];
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
}
```

## Caching Strategy

### Server Cache (React Query)
- **Stale Time**: 5 минут для списков, 1 минута для деталей
- **Cache Time**: 10 минут
- **Refetch Interval**: Dashboard — 30 секунд, остальные — при фокусе
- **Retry**: 3 попытки с exponential backoff

### Client Cache (Zustand + localStorage)
- **Auth Token**: localStorage с автоматическим обновлением
- **Theme**: localStorage
- **Sidebar State**: localStorage
- **Form Drafts**: sessionStorage

## Global State Rules

1. **Server State** — только через React Query
2. **Client State** — только через Zustand
3. **Никакого prop drilling** — используем hooks и stores
4. **Immutable Updates** — всегда создаем новые объекты
5. **Selectors** — используем мемоизированные селекторы для производительности
6. **Async Actions** — в React Query (mutations), не в Zustand
