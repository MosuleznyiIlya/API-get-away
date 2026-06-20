# API Keys

## Generation

API Key генерируется в формате: `{prefix}_{random_base62}`

- **Prefix**: `ag_` (gateway)
- **Random**: 32 символа из [a-zA-Z0-9]
- **Пример**: `ag_abc123def456ghi789jkl012mno345pq`

## Hashing

- Алгоритм: bcrypt с cost factor 12
- Хранится в БД: `bcrypt_hash(key)`
- Префикс хранится открытым текстом для идентификации
- Полный ключ показывается только при создании (one-time display)

## Storage

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    prefix VARCHAR(10) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Validation Flow

1. Извлечь ключ из заголовка `X-API-Key`
2. Извлечь prefix (первые 3 символа после `_`)
3. Найти запись в БД по prefix
4. Сравнить bcrypt hash предоставленного ключа с key_hash
5. Проверить `is_active = TRUE`
6. Если валиден — добавить `api_key_id` в request context
7. Если невалиден — вернуть 401 Unauthorized

## Revocation Flow

### Soft Delete
1. Установить `is_active = FALSE`
2. Ключ остается в БД для аудита
3. Все запросы с этим ключом отклоняются

### Hard Delete (Future)
1. Удалить запись из БД
2. Очистить связанные логи (анонимизировать api_key_id)
3. Инвалидировать кэш

### Rotation
1. Создать новый ключ
2. Обновить конфигурацию клиента
3. Отозвать старый ключ (soft delete)
4. Grace period: 24 часа для миграции
