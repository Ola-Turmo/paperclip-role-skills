---
name: paperclip-cloudflare-inbox-ops
description: Operate company mailboxes hosted in the shared Cloudflare agentic inbox service with strict company mailbox boundaries, careful reply discipline, and no mailbox cross-talk.
---

# Paperclip Cloudflare Inbox Ops

Use the shared Cloudflare inbox service as the mailbox surface for the companies that have been migrated off simple Gmail forwarding.

## Current live service

- Base URL: `https://portfolio-agentic-inbox.ola-turmo.workers.dev`
- Auth model: HTTP Basic Auth
- Shared service, but mailbox access must stay company-scoped

## Company mailbox map

- `Lovkode.no` -> `ola@lovkode.no`
- `TRT.ge` -> `ola@trt.ge`
- `Gatareba.ge` -> `ola@gatareba.ge`

Do not use another company mailbox just because it is available in the same service.

## Company secret names

Resolve these from the current company before use:

- `cloudflare_agentic_inbox_url`
- `cloudflare_agentic_inbox_basic_auth_username`
- `cloudflare_agentic_inbox_basic_auth_password`
- `cloudflare_agentic_inbox_mailbox`

## Core rule

- one company -> one mailbox
- no cross-company inbox search
- no cross-company replies
- no silent use of personal Gmail when the Cloudflare mailbox is the intended company surface

## Working method

1. Resolve the four company secrets.
2. Confirm the mailbox matches the current company.
3. Read/search/list messages only inside that mailbox.
4. Draft replies carefully and keep a traceable operator tone.
5. If outbound delivery is rejected by Cloudflare, record that precisely and escalate instead of pretending the reply was sent.

## HTTP patterns

Use Basic Auth with the company username/password secrets.

### Read mailbox

`GET /api/v1/mailboxes/<mailboxId>/emails`

### Read one email

`GET /api/v1/mailboxes/<mailboxId>/emails/<id>`

### Search mailbox

`GET /api/v1/mailboxes/<mailboxId>/search?...`

### Send / reply

`POST /api/v1/mailboxes/<mailboxId>/emails`

Required sender rule:

- `from` must equal the current mailbox exactly

## Current operational truth

The service is proven for:

- inbound delivery into the three live company mailboxes
- mailbox storage, search, and reading
- API acceptance for outbound send attempts

The service is not yet proven for unrestricted outbound delivery to arbitrary external recipients.

Cloudflare currently rejects some external recipients with:

- `destination address is not a verified address`

That means:

- reading and triage are live
- inbound support handling is live
- outbound must be treated as conditional until Cloudflare email sending is widened for the account

## Reply discipline

- Always state whether a reply was drafted only, accepted by the API, or actually delivered.
- Do not mark an issue as resolved if Cloudflare rejected the recipient.
- Prefer short, calm, factual responses.
- Do not answer regulated, legal, medical, tax, or otherwise high-stakes questions without the correct review path.

## Best uses by role

- `Operations Manager`: inbox ownership, routing, escalation, process follow-up
- `Customer Service Manager`: triage, response drafting, repeated-confusion capture
- `CEO`: priority/relationship-sensitive replies and escalations
- `Product & Tech Manager`: technical debugging of the mailbox service only when needed

## Escalation triggers

Escalate when:

- the mailbox secret mapping is wrong
- a message appears in the wrong company mailbox
- outbound delivery is rejected
- the service auth stops working
- a message needs legal, medical, finance, or public-risk review
