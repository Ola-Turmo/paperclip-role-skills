---
name: paperclip-stripe-governor
description: Govern Stripe usage inside Paperclip with strict company ownership, read-first access, and no shared-account misuse.
---

# Paperclip Stripe Governor

Use Stripe through the guarded Paperclip runtime path, not through arbitrary API calls.

## Runtime

- Preferred command on the VPS: `/home/.paperclip/provider-tooling/bin/paperclip-stripe`
- Policy file: `/home/.paperclip/provider-tooling/provider-governance.json`
- Current local source of truth: `references/provider-governance.json`

## Current tool analysis

Current local Stripe footprint discovered on this PC:

- Stripe CLI `1.37.4`
- Stripe Node SDK target version `16.0.0`
- One active configured Stripe profile for `kurs.ing`

That means the safe default is:

- only `KUR` gets live Stripe runtime access right now
- every other company is denied until it has its own real Stripe account/config

## Current company rules

- `KUR`: owner access, read-first operations
- `PER`, `GAT`, `LOV`, `PAR`, `EMD`, `TRT`, `AII`: denied until own account exists

## Allowed operations for `KUR`

- `whoami`
- `list-products`
- `list-prices`
- `list-customers`
- `list-payment-links`
- `list-subscriptions`
- `list-invoices`

## Future operations for `KUR`

These are reasonable later, but should still be issue-gated:

- `create-payment-link`
- `create-checkout-session`
- `create-customer-portal-session`

## Forbidden without approval

- refunds
- disputes
- payouts
- transfers
- subscription cancellations in live mode
- key rotation
- webhook endpoint mutation
- any use of the `Kurs.ing` Stripe account for another company

## Practical workflow

1. Confirm the company is `KUR`.
2. Use read-only inspection first.
3. If the task needs a write operation, use an issue or approval.
4. Do not let another company piggyback on the current Stripe account.

## Wrapper examples

```bash
/home/.paperclip/provider-tooling/bin/paperclip-stripe --company KUR whoami
/home/.paperclip/provider-tooling/bin/paperclip-stripe --company KUR list-products
/home/.paperclip/provider-tooling/bin/paperclip-stripe --company KUR list-subscriptions
```

## Commercial fit

Near-term best fits for future separate Stripe accounts:

- `KUR`: active now
- `EMD`: SaaS subscriptions and onboarding monetization
- `PAR`: client retainers and services
- `AII`: campaign retainers, licensing, delivery billing

Do not provision Stripe for `GAT`, `LOV`, `TRT`, or `PER` until there is a real product or billing need and a separate account/config.
