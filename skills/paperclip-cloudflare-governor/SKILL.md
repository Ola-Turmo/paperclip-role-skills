---
name: paperclip-cloudflare-governor
description: Govern Cloudflare usage inside Paperclip with strict company boundaries, approved command classes, and no account-wide free-for-all.
---

# Paperclip Cloudflare Governor

Use Cloudflare through the guarded Paperclip runtime path, not through ad hoc global commands.

## Runtime

- Preferred command on the VPS: `/home/.paperclip/provider-tooling/bin/paperclip-cloudflare`
- Policy file: `/home/.paperclip/provider-tooling/provider-governance.json`
- Current local source of truth: `references/provider-governance.json`

## Core rule

- One company, one Cloudflare surface.
- No cross-company deploys.
- No account-wide cleanup.
- No DNS, zone, cert, or connectivity-admin changes without a dedicated approval issue.

## Current account analysis

The copied Wrangler auth currently supports:

- Workers write
- D1 write
- Pages write
- Workers KV write
- Queues write
- Pipelines write
- Secrets Store write
- AI and AI Search write/run
- Zone read

The copied auth does **not** currently include:

- `email_routing:write`
- `email_sending:write`
- `browser:write`
- `artifacts:write`
- `flagship:write`

Do not plan workflows that depend on those missing scopes until the token is refreshed and intentionally widened.

## Company rules

Read `references/provider-governance.json` before use. The short version:

- `PER`: no Cloudflare use
- `KUR`, `GAT`, `LOV`, `EMD`, `TRT`, `AII`: scoped deploy/read use only for that company's own Workers/Pages/D1/Queues/secrets
- `PAR`: shared platform admin scope, but still no destructive account-wide work without explicit approval

## Allowed command classes

- `identity`: safe identity/account inspection
- `read`: list, inspect, tail, status, deployments, non-mutating queries
- `write`: deploy/apply/put/create for the current company only

## Forbidden by default

- destructive delete/remove/purge commands
- zone mutation
- DNS mutation
- certificate mutation
- connectivity-admin use
- email-routing or browser features

## Practical workflow

1. Confirm the current company code.
2. Check the provider policy for that company.
3. Use the guarded wrapper with the company code.
4. If the task needs a forbidden class, stop and create or use an approval issue.

## Wrapper examples

```bash
/home/.paperclip/provider-tooling/bin/paperclip-cloudflare --company KUR whoami
/home/.paperclip/provider-tooling/bin/paperclip-cloudflare --company KUR pages project list
/home/.paperclip/provider-tooling/bin/paperclip-cloudflare --company PAR d1 list
```

## Approval triggers

Open or use an issue before:

- changing DNS
- deleting D1 data
- rotating secrets in production
- changing route bindings
- using AI/AI-search features outside the company's explicit product surface
