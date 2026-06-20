# UI Guidelines

## Design Rules

### Color Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--color-primary` | #2563EB | #3B82F6 | Primary buttons, links |
| `--color-secondary` | #64748B | #94A3B8 | Secondary elements |
| `--color-success` | #16A34A | #22C55E | Success states |
| `--color-warning` | #CA8A04 | #EAB308 | Warning states |
| `--color-error` | #DC2626 | #EF4444 | Error states |
| `--color-background` | #FFFFFF | #0F172A | Page background |
| `--color-surface` | #F8FAFC | #1E293B | Cards, panels |
| `--color-border` | #E2E8F0 | #334155 | Borders, dividers |
| `--color-text` | #0F172A | #F8FAFC | Primary text |
| `--color-text-secondary` | #64748B | #94A3B8 | Secondary text |

### Typography

- **Font**: Inter, system-ui, sans-serif
- **Base Size**: 16px
- **Scale**: 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px
- **Line Height**: 1.5 для body, 1.2 для headings

### Spacing

- **Base Unit**: 4px
- **Scale**: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- **Border Radius**: 4px (small), 8px (medium), 12px (large), 16px (xl)

## Forms

### Form Layout

```
┌─────────────────────────────────────┐
│ Form Title                          │
├─────────────────────────────────────┤
│ Label                               │
│ ┌─────────────────────────────────┐ │
│ │ Input                           │ │
│ └─────────────────────────────────┘ │
│ Helper text / Error message         │
├─────────────────────────────────────┤
│ Label *                             │
│ ┌─────────────────────────────────┐ │
│ │ Select                          │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ [Cancel]        [Save]              │
└─────────────────────────────────────┘
```

### Validation Rules

- Валидация на blur для полей
- Валидация на submit для всей формы
- Ошибки отображаются под полем красным цветом
- Обязательные поля помечаются *
- Disabled submit при наличии ошибок

### Form States

- **Default** — стандартное состояние
- **Focus** — синий border
- **Error** — красный border + иконка + сообщение
- **Success** — зеленый border + иконка (после submit)
- **Disabled** — серый фон, cursor not-allowed
- **Loading** — spinner на кнопке submit

## Tables

### Table Layout

```
┌──────┬──────────────┬────────┬──────────┬────────────┐
│ Name │ Upstream URL │ Status │ Priority │ Actions    │
├──────┼──────────────┼────────┼──────────┼────────────┤
│ svc1 │ http://...   │ ● On   │ 10       │ [Edit][Del]│
│ svc2 │ http://...   │ ● Off  │ 20       │ [Edit][Del]│
└──────┴──────────────┴────────┴──────────┴────────────┘
Page 1 of 10    [Previous] [1] [2] ... [10] [Next]
```

### Table Features

- Sortable columns (click header)
- Filterable columns (dropdown)
- Pagination (10, 25, 50, 100 per page)
- Row actions (edit, delete, view)
- Bulk actions (select multiple rows)
- Empty state — иллюстрация + текст "No data found"
- Loading state — skeleton rows

## Loading States

### Global Loading
- Full page spinner при первой загрузке
- Центрированный spinner с затемнением фона

### Local Loading
- Skeleton screens для списков и карточек
- Inline spinner для кнопок
- Shimmer effect для таблиц

### Loading Patterns

```typescript
// Page loading
if (isLoading) return <PageSkeleton />;
if (isError) return <ErrorState error={error} />;
return <PageContent data={data} />;

// Button loading
<Button disabled={isPending}>
  {isPending ? <Spinner size="sm" /> : 'Save'}
</Button>

// Table loading
<Table>
  {isLoading ? (
    Array(5).fill(null).map((_, i) => <TableRowSkeleton key={i} />)
  ) : (
    data.map(item => <TableRow key={item.id} data={item} />)
  )}
</Table>
```

## Error States

### Error Types

1. **404 Not Found**
   - Иллюстрация
   - Текст: "Page not found"
   - Кнопка: "Go to Dashboard"

2. **500 Server Error**
   - Иллюстрация
   - Текст: "Something went wrong"
   - Кнопка: "Retry" + "Contact Support"

3. **Network Error**
   - Иконка WiFi с крестиком
   - Текст: "Connection lost"
   - Кнопка: "Retry"

4. **Empty State**
   - Иллюстрация
   - Текст: "No services yet"
   - Кнопка: "Create Service"

### Error Component

```typescript
interface ErrorStateProps {
  type: '404' | '500' | 'network' | 'empty';
  title?: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

## Notifications

### Toast Notifications

| Type | Icon | Duration | Position |
|------|------|----------|----------|
| Success | Checkmark | 3s | Top-right |
| Error | X | 5s | Top-right |
| Warning | Triangle | 4s | Top-right |
| Info | Info | 3s | Top-right |

### Notification Rules

- Максимум 5 уведомлений на экране
- Новые уведомления появляются сверху
- Автоматическое исчезновение через duration
- Ручное закрытие по клику на X
- Анимация: slide-in from right, fade-out

### Usage

```typescript
// Success
notificationStore.getState().addNotification({
  type: 'success',
  message: 'Service created successfully',
});

// Error
notificationStore.getState().addNotification({
  type: 'error',
  message: 'Failed to create service: ' + error.message,
});
```
