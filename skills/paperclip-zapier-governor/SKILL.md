---
name: paperclip-zapier-governor
description: Govern Zapier SDK CLI usage inside Paperclip with company-scoped discovery, connection review, and no unsafe live automation by default.
---

# Paperclip Zapier Governor

Use Zapier as an integration catalog and controlled automation layer, not as a silent mutation engine.

## Runtime

- Preferred command on the VPS: `/home/.paperclip/provider-tooling/bin/paperclip-zapier`
- Policy file: `/home/.paperclip/provider-tooling/provider-governance.json`
- Current local source of truth: `references/provider-governance.json`

## Current tool analysis

The copied local Zapier SDK CLI is `@zapier/zapier-sdk-cli 0.38.2`.

Useful command families currently available:

- account/profile
- app catalog
- action inspection
- connection inspection
- client credential management
- tables
- manifest/build helpers
- MCP surface

That means the runtime is strong for:

- app discovery
- integration research
- connection inspection
- app scaffolding
- typed manifest/build workflows

It is also powerful enough to be dangerous if used loosely:

- `run-action`
- client credential creation/deletion
- table mutation

Those must stay restricted unless a company has a specific approved Zapier operating path.

## Current recommended Zapier apps

Confirmed or researched useful app categories for this portfolio:

- Gmail
- Google Sheets
- Stripe
- PostHog
- Slack
- Notion
- HubSpot
- Discord

Use the app directory links in `references/provider-governance.json` when planning company integrations.

## Company rules

Short version:

- `PAR`: admin-scoped discovery/build use
- `PER`, `KUR`, `GAT`, `LOV`, `EMD`, `TRT`, `AII`: discovery + connection-read only by default

## Allowed by default

- `get-profile`
- `list-apps`
- `get-app`
- `list-actions`
- `get-action`
- `list-input-fields`
- `list-input-field-choices`
- `get-input-fields-schema`
- `list-connections`
- `get-connection`
- `find-first-connection`
- `find-unique-connection`

## Allowed only for platform/admin work

- `build-manifest`
- `generate-app-types`
- `bundle-code`
- `mcp`

## Forbidden by default

- `run-action`
- `create-client-credentials`
- `delete-client-credentials`
- table create/update/delete commands

## Practical workflow

1. Start with catalog and connection-read commands.
2. Use Zapier to design the integration plan per company.
3. Open an issue before enabling any live mutation path.
4. Prefer company-specific connection issues over silently reusing a shared Zapier account.

## Wrapper examples

```bash
/home/.paperclip/provider-tooling/bin/paperclip-zapier --company PAR list-apps
/home/.paperclip/provider-tooling/bin/paperclip-zapier --company KUR list-connections gmail
/home/.paperclip/provider-tooling/bin/paperclip-zapier --company PAR build-manifest gmail stripe
```

## High-value company usecases

- `PER`: Gmail, Calendar, Sheets, Notion planning and personal ops research
- `KUR`: support routing, lead capture, Sheets, Stripe-triggered notifications
- `GAT`: intake, reminders, document routing, operator alerts
- `LOV`: CRM, intake, calendar, client communications
- `PAR`: integration R&D and app-build/admin
- `EMD`: onboarding, CRM, analytics handoffs
- `TRT`: clinic lead routing, education notifications, support handoffs
- `AII`: lead intake, campaign approvals, delivery notifications
