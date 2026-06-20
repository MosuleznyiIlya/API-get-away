# JWT

## JWT Strategy

Gateway использует JWT (JSON Web Tokens) для stateless аутентификации.

## Supported Algorithms

- **HS256** — HMAC with SHA-256 (симметричный, default)
- **HS384** — HMAC with SHA-384
- **HS512** — HMAC with SHA-512
- **RS256** — RSA with SHA-256 (асимметричный, future)

## Validation Rules

### 1. Format Validation
- Токен должен состоять из 3 частей, разделенных точками: `header.payload.signature`
- Каждая часть — Base64Url encoded

### 2. Header Validation
- `alg` — должен быть в списке supported algorithms
- `typ` — должен быть "JWT"

### 3. Payload Validation
- `exp` (Expiration) — токен не должен быть просрочен
- `iat` (Issued At) — должен быть в прошлом
- `iss` (Issuer) — должен совпадать с configured issuer
- `sub` (Subject) — обязательное поле, идентификатор пользователя

### 4. Signature Validation
- Для HS256: HMACSHA256(base64url(header) + "." + base64url(payload), secret_key)
- Секретный ключ хранится в environment variable `JWT_SECRET_KEY`

### 5. Custom Claims (Future)
- `roles` — массив ролей для RBAC
- `permissions` — массив разрешений

## Error Responses

### Invalid Token Format
```json
{
  "error": "invalid_token_format",
  "message": "Token must consist of 3 parts separated by dots"
}
```
Status: 401 Unauthorized

### Token Expired
```json
{
  "error": "token_expired",
  "message": "Token has expired",
  "exp": 1704067200
}
```
Status: 401 Unauthorized

### Invalid Signature
```json
{
  "error": "invalid_signature",
  "message": "Token signature verification failed"
}
```
Status: 401 Unauthorized

### Invalid Issuer
```json
{
  "error": "invalid_issuer",
  "message": "Token issuer does not match configured issuer",
  "expected": "gateway-platform",
  "received": "other-issuer"
}
```
Status: 401 Unauthorized

### Missing Token
```json
{
  "error": "missing_token",
  "message": "Authorization header is required"
}
```
Status: 401 Unauthorized
