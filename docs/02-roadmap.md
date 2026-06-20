# Roadmap & Documentation Checklist

## Layer 1 — System Truth
- [ ] Models finalized (`docs/database.md`)
- [ ] Auth & security defined (`docs/security.md`)
- [ ] System design defined (`docs/architecture/system-design.md`)

## Layer 2 — Runtime Behavior (Backend Brain)
- [ ] CRUD API contract defined (`docs/backend/api.md`)
- [ ] Routing engine defined (`docs/backend/routing.md`)
- [ ] Reverse proxy defined (`docs/backend/gateway-runtime.md`)
- [ ] Cache layer defined (`docs/backend/caching.md`)
- [ ] Rate limiting defined (`docs/backend/rate-limiting.md`)
- [ ] Request logging defined (`docs/backend/logging.md`)
- [ ] Metrics defined (`docs/backend/metrics.md`)

## Layer 3 — Implementation
- [ ] Backend structure defined (`docs/backend/backend-structure.md`)
- [ ] DevOps defined (`docs/devops/`)
- [ ] Frontend defined (`docs/frontend/`)

## Cleanup Actions
- [ ] Duplicate `docs/backend/database.md` удалён
- [ ] `docs/backend/jwt.md` влит в `docs/security.md` и удалён
- [ ] `docs/backend/api-keys.md` влит в `docs/security.md` и удалён
- [ ] `docs/backend/redis.md` перенесён в `docs/devops/redis.md` (или влит в `caching.md` + `rate-limiting.md`)
- [ ] `docs/backend/backend-architecture.md` распилен: CRUD → `api.md`, runtime → Layer 2, структура → `backend-structure.md`
