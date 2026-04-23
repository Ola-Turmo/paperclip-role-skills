# Paperclip Role Skills

Reusable Paperclip company skills for portfolio companies that run the same CEO + department-manager org pattern.

This repo provides:

- a shared `paperclip-operator-core` skill for every company manager
- role-specific skills for CEO, operations, product & tech, growth & revenue, finance & risk, customer service, people & partners, and social & media
- a reusable migration script that imports the skill pack into Paperclip companies, upgrades placeholder agents onto Hermes, pins every role to `MiniMax-M2.7` on the `custom:minimax-token-plan` provider, and syncs desired skills

## Included skills

- `paperclip-operator-core`
- `paperclip-ceo-control-tower`
- `paperclip-operations-delivery`
- `paperclip-product-tech-builder`
- `paperclip-growth-revenue-ops`
- `paperclip-finance-risk-review`
- `paperclip-customer-service-triage`
- `paperclip-people-partners-ops`
- `paperclip-social-media-command`
- `paperclip-talent-studio-design`
- `paperclip-disclosure-rights-guard`
- `paperclip-client-success-delivery`
- `paperclip-performance-intelligence`
- `paperclip-cloudflare-governor`
- `paperclip-cloudflare-inbox-ops`
- `paperclip-zapier-governor`
- `paperclip-stripe-governor`

## Intended runtime mapping

All managed company roles run on:

- adapter: `hermes_local`
- provider: `custom:minimax-token-plan`
- model: `MiniMax-M2.7`
- session mode: `persistSession: true`

## Apply to a live Paperclip instance

Run:

```bash
python scripts/apply_paperclip_role_runtime.py
```

Optional arguments:

```bash
python scripts/apply_paperclip_role_runtime.py \
  --base-url http://100.80.50.111:13101 \
  --referer http://100.80.50.111:13101/PAR/settings/agents \
  --ssh-target lovkode-vps \
  --container compose-paperclip-1 \
  --repo-url https://github.com/Ola-Turmo/paperclip-role-skills
```

The script will:

1. import all role skills into every company
2. create safe company workspace directories inside the live Paperclip container
3. upgrade paused org-skeleton agents from placeholders or mixed local adapters onto Hermes
4. explicitly pin every managed role to `MiniMax-M2.7` on the `custom:minimax-token-plan` provider
5. sync role-specific desired skills onto each agent
6. verify the resulting skill snapshots and write a JSON summary

## Provider governance

This repo also includes provider-governance assets for Cloudflare, Zapier, and Stripe:

- policy map: `references/provider-governance.json`
- skills:
  - `paperclip-cloudflare-governor`
  - `paperclip-zapier-governor`
  - `paperclip-stripe-governor`
- VPS sync helper:

```powershell
pwsh scripts/sync-provider-tooling-to-vps.ps1
```

That sync helper:

1. pins the provider runtimes to the local inspected versions
2. copies the local auth/config footprints from this PC where practical
3. installs guarded wrapper commands on the VPS under `/home/.paperclip/provider-tooling/bin`
4. exposes:
   - `paperclip-cloudflare`
   - `paperclip-zapier`
   - `paperclip-stripe`

Current Cloudflare note:

- the synced Wrangler auth now includes `email_routing:write`, `email_sending:write`, and `browser:write`
- that makes Cloudflare Email features available in the governed Paperclip runtime, but they still need company-scoped setup and issue-backed use

## Design goals

- preserve company boundaries
- keep account usage company-scoped
- make local adapters discover the right skills at runtime
- give each department manager a role-appropriate operating playbook instead of only generic Paperclip bundle skills
