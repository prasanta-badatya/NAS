# Claude Code — Project Rules for Private NAS

## Before every commit

1. **Update `README.md`** — keep the feature list, API table, data models section, and tech stack accurate.
2. **Update any affected inline docs** — e.g. if a view changes, update the API endpoints table; if a model changes, update the Data models section.

Do this as part of the same commit (or a preceding doc commit in the same push) — never commit code without keeping docs in sync.

---

## Commit style

- Commit **separately by feature/layer**: one commit per distinct change (backend model, frontend component, migration, docs, etc.).
- Use conventional commits: `feat(scope):`, `fix(scope):`, `refactor(scope):`, `docs:` etc.
- Always append the co-author trailer:
  ```
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```

---

## Code conventions

- **Backend**: Django 5, DRF, Python 3.11. Soft-delete pattern (`is_deleted` + `deleted_at`).
- **Frontend**: Angular 16, no UI component libraries, pure SCSS, dark theme (`#0f0f0f` bg, `#4f8ef7` accent).
- No hardcoded IPs — always use the `environment.ts` placeholder.
- Security: validate file paths with `os.path.realpath()`, whitelist MIME types, rate-limit auth endpoints.
