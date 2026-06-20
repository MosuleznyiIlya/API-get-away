# Security

## 1. Auth Layer Overview

Порядок middleware (единый pipeline):
```
Request → WAF/IP Allowlist → API Key Auth → JWT Validation → Rate Limit → Route Match → Proxy → Upstream
```

## 2. API Key Authentication

### 2.1 Generation Format

API Key генерируется в формате: `{prefix}_{random_base62}`

- **Prefix**: `ag_` (gateway)
- **Random**: 32 символа из `[a-zA-Z0-9]`
- **Пример**: `ag_abc123def456ghi789jkl012mno345pq`

Полный ключ показывается только при создании (one-time display).

### 2.2 Hashing & Storage

- Алгоритм: **bcrypt** с cost factor 12
- Хранится в БД: `bcrypt_hash(key)`
- Префикс хранится открытым текстом для идентификации
- Полный ключ никогда не логируется

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

### 2.3 Validation Flow

1. Извлечь `X-API-Key` из заголовка
2. Извлечь prefix (часть до `_`)
3. Найти запись в БД по `prefix` (быстрый lookup)
4. Сравнить `bcrypt` предоставленного ключа с `key_hash` (constant-time comparison)
5. Проверить `is_active = TRUE`
6. Привязать `api_key_id` к контексту запроса
7. Если невалиден — вернуть 401 Unauthorized

### 2.4 Revocation & Rotation

**Soft Delete (default):**
1. Установить `is_active = FALSE`
2. Ключ остаётся в БД для аудита
3. Все запросы с этим ключом отклоняются
4. Инвалидировать связанный кэш в Redis

**Hard Delete (future):**
1. Удалить запись из БД
2. Очистить связанные логи (анонимизировать `api_key_id`)
3. Инвалидировать кэш

**Rotation Flow:**
1. Создать новый ключ
2. Обновить конфигурацию клиента
3. Отозвать старый ключ (soft delete)
4. Grace period: 24 часа для миграции

### 2.5 Risks

- **Timing attacks** → использовать `bcrypt` с постоянным временем сравнения
- **Key enumeration** → префикс уникален, но не даёт инфо о полном ключе
- **Хранение в логах** → никогда не логировать полный ключ, только `prefix`
- **Key leakage** → one-time display при создании, нет возможности восстановить

---

## 3. JWT Validation

### 3.1 Supported Algorithms

| Algorithm | Type | Status |
|-----------|------|--------|
| HS256 | HMAC with SHA-256 | Default |
| HS384 | HMAC with SHA-384 | Supported |
| HS512 | HMAC with SHA-512 | Supported |
| RS256 | RSA with SHA-256 | Future |

### 3.2 Validation Rules

**1. Format Validation:**
- Токен должен состоять из 3 частей, разделённых точками: `header.payload.signature`
- Каждая часть — Base64Url encoded

**2. Header Validation:**
- `alg` — должен быть в списке supported algorithms (жёстко зафиксирован в конфиге, не доверять header)
- `typ` — должен быть `"JWT"`

**3. Payload Validation:**
- `exp` (Expiration) — токен не должен быть просрочен
- `iat` (Issued At) — должен быть в прошлом
- `iss` (Issuer) — должен совпадать с configured issuer
- `sub` (Subject) — обязательное поле, идентификатор пользователя
- `aud` — должен совпадать с `service_id` (если указан)
- Clock skew допуск: ±60 секунд

**4. Signature Validation:**
- Для HS256: `HMACSHA256(base64url(header) + "." + base64url(payload), secret_key)`
- Секретный ключ хранится в environment variable `JWT_SECRET_KEY`

**5. Custom Claims (Future):**
- `roles` — массив ролей для RBAC
- `permissions` — массив разрешений

### 3.3 Token Rules

- Access token TTL: **15 минут**
- Refresh token TTL: **7 дней** (хранится отдельно, не в Gateway)
- Нет blacklisting на уровне Gateway — это задача Identity Provider
- Алгоритм `alg` жёстко зафиксирован в конфигурации (защита от algorithm confusion)

### 3.4 Error Responses

**Invalid Token Format:**
```json
{
  "error": "invalid_token_format",
  "message": "Token must consist of 3 parts separated by dots"
}
```
Status: 401 Unauthorized

**Token Expired:**
```json
{
  "error": "token_expired",
  "message": "Token has expired",
  "exp": 1704067200
}
```
Status: 401 Unauthorized

**Invalid Signature:**
```json
{
  "error": "invalid_signature",
  "message": "Token signature is invalid"
}
```
Status: 401 Unauthorized

**Invalid Algorithm:**
```json
{
  "error": "invalid_algorithm",
  "message": "Algorithm not supported"
}
```
Status: 401 Unauthorized

### 3.5 Risks

- **Token leakage** → маскировать `Authorization` в логах (`Authorization: Bearer ****`)
- **Algorithm confusion** → жёстко зафиксировать `alg` в конфиге, не доверять `alg` из header
- **Clock skew** → допуск ±60 секунд
- **Replay attacks** → mitigated коротким TTL (15 min)

---

## 4. Middleware Order & Failures

| Порядок | Слой | Fail-Closed? | Описание |
|---------|------|--------------|----------|
| 1 | WAF / IP Allowlist | Да | Блокировка по IP/гео |
| 2 | API Key | Да | 401 при невалидном ключе |
| 3 | JWT | Да | 401 при невалидном токене |
| 4 | Rate Limit | Нет | Fail-open с алертом при недоступности Redis |
| 5 | Routing | Да | 404 при отсутствии маршрута |
| 6 | Proxy | Да | 502/504 при проблемах upstream |

---

## 5. SSRF Protection

- Upstream URL валидируется по allowlist схем (`http`, `https`)
- Запрещены internal IPs:
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
  - `127.0.0.0/8`
  - `169.254.0.0/16` (link-local)
  - `0.0.0.0/8`
- DNS rebinding защита — resolve + проверка IP перед запросом
- Запрещены loopback и multicast адреса

---

## 6. Security Logs

- Все auth failures логируются с `security=true` флагом
- Brute-force паттерны: >5 failed auth/minute с одного IP → алерт
- Security events:
  - Invalid API key attempts
  - Expired JWT usage
  - Invalid signature attempts
  - Rate limit bypass attempts
  - SSRF blocked attempts
