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
- Artifacts write
- Flagship write
- Email Routing write
- Email Sending write
- Browser write

This means Cloudflare Email features are technically available in the governed runtime now. Treat that as capability, not blanket permission: email setup must still stay company-scoped and issue-backed.

## Company rules

Read `references/provider-governance.json` before use. The short version:

- `PER`: no Cloudflare use
- `KUR`: scoped deploy/read use only for Kurs infrastructure
- `GAT`, `LOV`, `EMD`, `TRT`, `AII`: scoped deploy/read use for their own Workers/Pages/D1/Queues/secrets and company-owned Cloudflare email surfaces
- `PAR`: shared platform admin scope, and the only company that should coordinate portfolio-level Cloudflare email setup work

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
- account-wide email-routing experiments
- browser features without an explicit operator issue

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
/home/.paperclip/provider-tooling/bin/paperclip-cloudflare --company PAR email --help
```

## Approval triggers

Open or use an issue before:

- changing DNS
- deleting D1 data
- rotating secrets in production
- changing route bindings
- enabling or changing Cloudflare Email Routing for a live company domain
- using AI/AI-search features outside the company's explicit product surface
