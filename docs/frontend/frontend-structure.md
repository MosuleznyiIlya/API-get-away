# Frontend Structure

## Feature Based Architecture

```
src/
├── pages/
│   ├── DashboardPage.tsx
│   ├── ServicesPage.tsx
│   ├── RoutesPage.tsx
│   ├── ApiKeysPage.tsx
│   └── LogsPage.tsx
├── features/
│   ├── services/
│   │   ├── ServiceList.tsx
│   │   ├── ServiceForm.tsx
│   │   ├── ServiceCard.tsx
│   │   └── useServices.ts
│   ├── routes/
│   │   ├── RouteList.tsx
│   │   ├── RouteForm.tsx
│   │   └── useRoutes.ts
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── useAuth.ts
│   ├── apiKeys/
│   │   ├── ApiKeyList.tsx
│   │   ├── ApiKeyForm.tsx
│   │   └── useApiKeys.ts
│   ├── logs/
│   │   ├── LogTable.tsx
│   │   ├── LogFilter.tsx
│   │   └── useLogs.ts
│   └── metrics/
│       ├── MetricsChart.tsx
│       ├── MetricsCards.tsx
│       └── useMetrics.ts
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   └── LoadingSpinner.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Layout.tsx
│   └── forms/
│       ├── FormField.tsx
│       └── FormError.tsx
├── hooks/
│   ├── useApi.ts
│   ├── useQueryParams.ts
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
├── services/
│   ├── apiClient.ts
│   ├── servicesApi.ts
│   ├── routesApi.ts
│   ├── apiKeysApi.ts
│   ├── logsApi.ts
│   └── metricsApi.ts
├── stores/
│   ├── authStore.ts
│   ├── uiStore.ts
│   └── notificationStore.ts
├── types/
│   ├── service.ts
│   ├── route.ts
│   ├── apiKey.ts
│   ├── log.ts
│   ├── metric.ts
│   └── common.ts
└── utils/
    ├── formatters.ts
    ├── validators.ts
    └── constants.ts
```

## Pages

- **DashboardPage** — главная страница с метриками
- **ServicesPage** — управление сервисами
- **RoutesPage** — управление маршрутами
- **ApiKeysPage** — управление API ключами
- **LogsPage** — просмотр логов

## Components

- **Common** — переиспользуемые UI компоненты
- **Layout** — структурные компоненты (sidebar, header)
- **Forms** — формовые компоненты

## Hooks

- **useApi** — обертка над API клиентом с обработкой ошибок
- **useQueryParams** — работа с URL query параметрами
- **useDebounce** — debounce для поиска
- **useLocalStorage** — синхронизация с localStorage

## Services

- **apiClient.ts** — базовый HTTP клиент (axios/fetch)
- **servicesApi.ts** — API для сервисов
- **routesApi.ts** — API для маршрутов
- **apiKeysApi.ts** — API для API ключей
- **logsApi.ts** — API для логов
- **metricsApi.ts** — API для метрик

## Stores

- **authStore.ts** — состояние аутентификации (Zustand)
- **uiStore.ts** — UI состояние (sidebar, theme)
- **notificationStore.ts** — уведомления (toast)

## Types

- TypeScript interfaces для всех сущностей
- Common types для pagination, API responses
