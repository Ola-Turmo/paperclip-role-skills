import argparse
import json
from typing import Any

import requests


DEFAULT_BASE_URL = "http://176.118.198.76:13100"
DEFAULT_ROLE_SKILL_REPO = "https://github.com/Ola-Turmo/paperclip-role-skills"

COMPANY_MAILBOXES = {
    "Lovkode.no": "ola@lovkode.no",
    "TRT.ge": "ola@trt.ge",
    "Gatareba.ge": "ola@gatareba.ge",
}


def api(session: requests.Session, base_url: str, method: str, path: str, *, json_body: dict[str, Any] | None = None):
    headers = {
        "Origin": base_url,
        "Referer": f"{base_url}/",
    }
    response = session.request(
        method,
        f"{base_url}{path}",
        json=json_body,
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    if not response.text.strip():
        return None
    return response.json()


def ensure_secret(
    session: requests.Session,
    base_url: str,
    company_id: str,
    *,
    name: str,
    value: str,
    description: str,
) -> str:
    secrets = api(session, base_url, "GET", f"/api/companies/{company_id}/secrets")
    for secret in secrets:
        if secret["name"] == name:
            return secret["id"]

    created = api(
        session,
        base_url,
        "POST",
        f"/api/companies/{company_id}/secrets",
        json_body={
            "name": name,
            "provider": "local_encrypted",
            "value": value,
            "description": description,
        },
    )
    return created["id"]


def get_connectors_plugin(session: requests.Session, base_url: str) -> dict[str, Any]:
    plugins = api(session, base_url, "GET", "/api/plugins")
    plugin = next(
        (item for item in plugins if item["pluginKey"] == "uos.plugin-connectors" and item["status"] == "ready"),
        None,
    )
    if not plugin:
        raise RuntimeError("uos.plugin-connectors is not ready")
    return plugin


def get_company_connections(session: requests.Session, base_url: str, plugin_id: str, company_id: str) -> list[dict[str, Any]]:
    response = api(
        session,
        base_url,
        "POST",
        f"/api/plugins/{plugin_id}/data/companyConnections",
        json_body={
            "companyId": company_id,
            "params": {"companyId": company_id},
        },
    )
    return response["data"]["connections"]


def upsert_company_connection(
    session: requests.Session,
    base_url: str,
    plugin_id: str,
    company_id: str,
    connection: dict[str, Any],
) -> dict[str, Any]:
    response = api(
        session,
        base_url,
        "POST",
        f"/api/plugins/{plugin_id}/actions/upsertCompanyConnection",
        json_body={
            "companyId": company_id,
            "params": {
                "companyId": company_id,
                "connection": connection,
            },
        },
    )
    return response["data"]["connection"]


def import_role_skills(session: requests.Session, base_url: str, company_id: str, repo_url: str) -> Any:
    return api(
        session,
        base_url,
        "POST",
        f"/api/companies/{company_id}/skills/import",
        json_body={"source": repo_url},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--service-url", default="https://portfolio-agentic-inbox.ola-turmo.workers.dev")
    parser.add_argument("--basic-auth-username", default="ola")
    parser.add_argument("--basic-auth-password", required=True)
    parser.add_argument("--repo-url", default=DEFAULT_ROLE_SKILL_REPO)
    parser.add_argument("--summary-path", default=r"C:\Users\heial\Documents\Codex\2026-04-22-agentic-inbox\paperclip-company-sync-summary.json")
    args = parser.parse_args()

    session = requests.Session()
    api(
        session,
        args.base_url,
        "POST",
        "/api/auth/sign-in/email",
        json_body={
            "email": args.email,
            "password": args.password,
            "rememberMe": True,
        },
    )

    connectors_plugin = get_connectors_plugin(session, args.base_url)
    companies = api(session, args.base_url, "GET", "/api/companies")
    companies_by_name = {company["name"]: company for company in companies}
    summary: list[dict[str, Any]] = []

    for company_name, mailbox in COMPANY_MAILBOXES.items():
        company = companies_by_name[company_name]
        company_id = company["id"]
        import_role_skills(session, args.base_url, company_id, args.repo_url)

        url_secret_id = ensure_secret(
            session,
            args.base_url,
            company_id,
            name="cloudflare_agentic_inbox_url",
            value=args.service_url,
            description="Base URL for the shared Cloudflare-hosted agentic inbox service used by this company.",
        )
        username_secret_id = ensure_secret(
            session,
            args.base_url,
            company_id,
            name="cloudflare_agentic_inbox_basic_auth_username",
            value=args.basic_auth_username,
            description="Basic auth username for the shared Cloudflare agentic inbox service.",
        )
        password_secret_id = ensure_secret(
            session,
            args.base_url,
            company_id,
            name="cloudflare_agentic_inbox_basic_auth_password",
            value=args.basic_auth_password,
            description="Basic auth password for the shared Cloudflare agentic inbox service.",
        )
        mailbox_secret_id = ensure_secret(
            session,
            args.base_url,
            company_id,
            name="cloudflare_agentic_inbox_mailbox",
            value=mailbox,
            description="The company-scoped mailbox id inside the shared Cloudflare agentic inbox service.",
        )

        existing_connections = get_company_connections(session, args.base_url, connectors_plugin["id"], company_id)
        existing = next(
            (
                item
                for item in existing_connections
                if item["providerId"] == "cloudflare"
                and item["label"] == "Cloudflare Agentic Inbox"
            ),
            None,
        )

        connection = {
            "id": existing["id"] if existing else None,
            "providerId": "cloudflare",
            "label": "Cloudflare Agentic Inbox",
            "accountIdentifier": mailbox,
            "usage": "support",
            "status": "connected",
            "scopes": ["inbound-mail", "mailbox-read", "draft-reply", "mailbox-search"],
            "channels": ["email", "inbox", "cloudflare"],
            "secretRefs": {
                "primary": password_secret_id,
            },
            "notes": (
                f"Cloudflare-hosted mailbox service for {company_name}. "
                f"Base URL: {args.service_url}. "
                f"Mailbox: {mailbox}. "
                f"Username secret: cloudflare_agentic_inbox_basic_auth_username. "
                f"Password secret ref stored here. "
                f"Inbound delivery is verified. Outbound to arbitrary external recipients is not yet fully proven."
            ),
            "lastValidationMessage": "Inbound mailbox delivery verified through portfolio-agentic-inbox.",
        }

        saved = upsert_company_connection(session, args.base_url, connectors_plugin["id"], company_id, connection)
        summary.append(
            {
                "company": company_name,
                "companyId": company_id,
                "mailbox": mailbox,
                "serviceUrlSecretId": url_secret_id,
                "usernameSecretId": username_secret_id,
                "passwordSecretId": password_secret_id,
                "mailboxSecretId": mailbox_secret_id,
                "connectionId": saved["id"],
            }
        )

    with open(args.summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
