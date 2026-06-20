# Security Architecture Overview

The API Gateway is the first line of defense for all downstream services.

The primary tasks of the security layer:

- Authenticate
- Authorize
- Validate
- Protect
- Observe

All incoming requests pass through the Security Pipeline before reaching the Proxy Layer.

## Security Pipeline

```
Request
  ↓
Request ID
  ↓
Header Validation
  ↓
JWT Validation
  ↓
API Key Validation
  ↓
Replay Protection
  ↓
Rate Limiting
  ↓
Route Resolution
  ↓
Proxy
  ↓
Logging
  ↓
Response
```

---

## 1. Threat Model (STRIDE)

### S — Spoofing Identity

**Risks**

Client impersonation.

**Examples:**

- Fake JWT
- Stolen API Key
- Fake X-Forwarded-* headers

**Protection**

- JWT Signature Validation
- API Key Hash Verification
- Trusted Proxy Configuration
- Request Identity Tracking

### T — Tampering

**Risks**

Modification of request content.

**Examples:**

- Header Manipulation
- JWT Payload Modification
- Request Rewriting

**Protection**

- JWT Signature Verification
- Header Validation
- Strict Route Matching

### R — Repudiation

**Risks**

User denies performing actions.

**Protection**

- Request ID
- Audit Logs
- Immutable Request Logs
- Timestamp Tracking

### I — Information Disclosure

**Risks**

Data leakage.

**Examples:**

- JWT Leakage
- API Key Leakage
- Internal Headers Exposure
- Stack Traces

**Protection**

- Secrets Redaction
- Structured Logging
- Sanitized Error Responses
- Header Filtering

### D — Denial of Service

**Risks**

Gateway overload.

**Examples:**

- Request Flooding
- Credential Stuffing
- Cache Exhaustion
- Large Payload Abuse

**Protection**

- Rate Limiting
- Body Size Limits
- Connection Limits
- Redis-backed Counters

### E — Elevation of Privilege

**Risks**

Gaining access above the authorized level.

**Protection**

- JWT Claim Validation
- Role Validation
- Scope Validation
- Route-Level Authorization

---

## 2. JWT Validation Flow (Detailed)

### Supported Algorithms

**MVP:**

- RS256
- ES256

**Not supported:**

- `none`

### Validation Flow

```
Authorization Header
  ↓
Extract Token
  ↓
Decode Header
  ↓
Validate Algorithm
  ↓
Validate Signature
  ↓
Validate Issuer
  ↓
Validate Audience
  ↓
Validate Expiration
  ↓
Validate Not Before
  ↓
Validate Claims
  ↓
Authenticated
```

### Required Claims

```json
{
  "sub": "...",
  "iss": "...",
  "aud": "...",
  "exp": "...",
  "iat": "..."
}
```

### Optional Claims

```json
{
  "roles": [],
  "permissions": [],
  "scope": []
}
```

### Validation Rules

| Claim | Rule |
|-------|------|
| `exp` | Current Time < exp |
| `nbf` | Current Time >= nbf |
| `iat` | Cannot be too far in the future. Maximum: +5 minutes |
| `aud` | Must match Gateway Audience |
| `iss` | Must be in the list of trusted Issuers |

### Failure Responses

- INVALID_TOKEN
- TOKEN_EXPIRED
- INVALID_SIGNATURE
- INVALID_AUDIENCE
- INVALID_ISSUER

**HTTP:** 401

---

## 3. API Key Security Model

### Storage Model

Never store API Keys in plain text.

### Lifecycle

```
Generate
  ↓
Display Once
  ↓
Hash
  ↓
Store Hash
  ↓
Validate Hash
```

### Database Storage

**Store:**

- `key_hash`
- `key_prefix`

**Do not store:**

- `full_api_key`

### Key Format

Example:

```
agw_live_xxxxxxxxxxxxxxxxxxxxx
```

### Rotation

**Supported:**

- Create New Key
- Deactivate Old Key

### Revocation

After deletion:

- DB revoke
- Redis invalidate
- Immediate rejection

---

## 4. Signature Validation (Optional)

Not required for MVP.

For Enterprise version, the following may be supported:

- HMAC Signatures

Example:

- `X-Signature`
- `X-Timestamp`

Flow:

```
Request
  ↓
Canonical Payload
  ↓
HMAC Verification
  ↓
Accept / Reject
```

**Application:**

- Webhooks
- Machine-to-Machine APIs

---

## 5. Rate Limit Abuse Prevention

### Primary Defense

Redis Token Bucket.

### Threats

| Threat | Description |
|--------|-------------|
| Flooding | 10,000 req/sec |
| Distributed Abuse | Multiple Clients |
| Credential Stuffing | Many API Keys |

### Mitigation

| Measure | Limit |
|---------|-------|
| Per API Key Limit | 100 rpm |
| Per IP Limit | Additional limit. 1000 rpm |
| Burst Protection | Token Bucket Capacity |
| Progressive Penalties | Future: Temporary Block, Exponential Backoff |

---

## 6. Replay Attack Prevention

### JWT Replay

JWT by itself does not protect against replay.

### MVP Protection

Use:

- Short Token Lifetime
- HTTPS Only

**Recommended duration:** 5–15 minutes

### Future Protection

Use claim:

- `jti`

Store:

- `jwt:jti:{id}` in Redis.

Reuse:

- Reject

### Signature Replay

If HMAC is used:

Check:

- Timestamp
- Nonce

**Acceptable window:** ±5 minutes

---

## 7. Header Injection Protection

### Threats

Examples:

- CRLF Injection
- Header Smuggling
- Host Header Attacks

### Protection

**Normalize Headers**

Remove:

- ``
- `
`

**Host Validation**

Allowed hosts:

- Allowed Hosts List

**Header Whitelist**

Allowed:

- Authorization
- Content-Type
- Accept
- X-Request-ID
- X-Correlation-ID

**Strip Dangerous Headers**

Remove:

- X-Original-URL
- X-Rewrite-URL
- Forwarded (if coming from client)

---

## 8. CORS + CSRF Strategy

### CORS

For React Admin.

**Allowed Origins**

```
https://admin.company.com
```

Do not use:

- `*`

**Allowed Methods**

- GET
- POST
- PATCH
- DELETE
- OPTIONS

**Allowed Headers**

- Authorization
- Content-Type
- X-Request-ID

### CSRF

**Admin API**

If using JWT Bearer:

- CSRF is not required

If Cookie Sessions appear:

- CSRF is mandatory

---

## 9. Secrets Management Strategy

### Secrets

The following are considered secrets:

- JWT Public Keys
- JWT Private Keys
- Database Credentials
- Redis Credentials
- Encryption Keys
- API Secrets

### Storage

**Development:**

- `.env`

**Production:**

- Docker Secrets
- Vault
- Cloud Secret Manager

### Rules

**Never:**

- Git
- Logs
- Database

### Rotation

**Support:**

- Key Rotation
- Credential Rotation

without downtime.

---

## 10. OWASP Top 10 Mapping

| OWASP | Mitigation |
|-------|------------|
| A01 Broken Access Control | JWT + RBAC |
| A02 Cryptographic Failures | TLS + RS256 |
| A03 Injection | Validation + ORM |
| A04 Insecure Design | Threat Modeling |
| A05 Security Misconfiguration | Hardened Defaults |
| A06 Vulnerable Components | Dependency Scanning |
| A07 Authentication Failures | JWT Validation |
| A08 Software Integrity Failures | Signed Builds |
| A09 Logging Failures | Structured Logging |
| A10 SSRF | Upstream Allowlist |

---

## Attack Scenarios

### Scenario 1 — Stolen API Key

**Attack**

Attacker obtains API Key

**Mitigation**

- Rate Limiting
- Revocation
- Rotation
- Monitoring

### Scenario 2 — Forged JWT

**Attack**

Modified JWT Payload

**Mitigation**

- Signature Validation
- Issuer Validation
- Audience Validation

### Scenario 3 — Route Enumeration

**Attack**

Bruteforce API Paths

**Mitigation**

- Rate Limiting
- 404 Normalization
- Monitoring

### Scenario 4 — Redis Exhaustion

**Attack**

Cache Key Explosion

**Mitigation**

- TTL
- Memory Limits
- Key Size Limits
- Eviction Policy

### Scenario 5 — Log Injection

**Attack**

Malicious Characters In Headers

**Mitigation**

- Structured Logging
- Header Sanitization
- Escaping

### Scenario 6 — SSRF Through Route Configuration

**Attack**

Administrator or attacker creates a route to:

- `169.254.169.254`
- `localhost`
- internal services

**Mitigation**

- Upstream Allowlist
- CIDR Restrictions
- Private Network Validation
- DNS Re-Validation

### Scenario 7 — Upstream DoS Amplification

**Attack**

Large Number Of Expensive Requests

**Mitigation**

- Rate Limiting
- Caching
- Circuit Breakers (Future)
- Timeouts

---

## Security Architecture Decisions (SAD)

| ID | Decision |
|----|----------|
| SAD-001 | JWT Validation is performed before Route Resolution. |
| SAD-002 | API Keys are stored only as a hash. |
| SAD-003 | All requests receive a Request ID. |
| SAD-004 | Redis failure must not lead to complete Gateway unavailability. |
| SAD-005 | All security errors are logged as Security Events. |
| SAD-006 | Gateway trusts only explicitly allowed upstream services. |
| SAD-007 | CORS operates on an allowlist model. |
| SAD-008 | All external connections operate only through TLS. |
| SAD-009 | JWT algorithm `none` is completely forbidden. |
| SAD-010 | Any authentication passes before the Cache Layer and Reverse Proxy Layer. |
