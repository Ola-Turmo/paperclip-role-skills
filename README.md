# Paperclip Role Skills

Reusable Paperclip company skills for portfolio companies that run the same CEO + department-manager org pattern.

This repo provides:

- a shared `paperclip-operator-core` skill for every company manager
- role-specific skills for CEO, operations, product & tech, growth & revenue, finance & risk, customer service, people & partners, and social & media
- a reusable migration script that imports the skill pack into Paperclip companies, upgrades placeholder agents onto real local adapters, and syncs desired skills

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

## Intended runtime mapping

- CEO -> `codex_local`
- Operations Manager -> `hermes_local`
- Product & Tech Manager -> `opencode_local`
- Growth & Revenue Manager -> `gemini_local`
- Finance & Risk Manager -> `codex_local`
- Customer Service Manager -> `pi_local`
- People & Partners Manager -> `opencode_local`
- Social & Media Manager -> `gemini_local`
- Agency CEO -> `codex_local`
- Talent Studio Lead -> `gemini_local`
- Media Systems Lead -> `opencode_local`
- Service Operations Lead -> `hermes_local`
- Disclosure & Rights Lead -> `codex_local`
- Client Success Lead -> `pi_local`
- Growth Distribution Lead -> `gemini_local`
- Performance Intelligence Lead -> `opencode_local`

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
3. upgrade paused org-skeleton agents from `process` placeholders to real local AI adapters
4. sync role-specific desired skills onto each agent
5. verify the resulting skill snapshots and write a JSON summary

## Design goals

- preserve company boundaries
- keep account usage company-scoped
- make local adapters discover the right skills at runtime
- give each department manager a role-appropriate operating playbook instead of only generic Paperclip bundle skills
