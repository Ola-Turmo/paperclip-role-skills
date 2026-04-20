import argparse
import json
import subprocess
import sys
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://100.80.50.111:13101"
DEFAULT_REFERER = f"{DEFAULT_BASE_URL}/PAR/settings/agents"
DEFAULT_REPO_URL = "https://github.com/Ola-Turmo/paperclip-role-skills"
DEFAULT_SSH_TARGET = "lovkode-vps"
DEFAULT_CONTAINER = "compose-paperclip-1"


ROLE_RUNTIME = {
    "CEO": {
        "adapterType": "codex_local",
        "adapterConfig": {
            "model": "gpt-5.4",
            "modelReasoningEffort": "high",
            "search": True,
            "dangerouslyBypassApprovalsAndSandbox": True,
            "extraArgs": ["--skip-git-repo-check"],
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-ceo-control-tower",
        ],
    },
    "Operations Manager": {
        "adapterType": "hermes_local",
        "adapterConfig": {
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-operations-delivery",
        ],
    },
    "Product & Tech Manager": {
        "adapterType": "opencode_local",
        "adapterConfig": {
            "model": "openai/gpt-5.4",
            "dangerouslySkipPermissions": True,
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-product-tech-builder",
        ],
    },
    "Growth & Revenue Manager": {
        "adapterType": "gemini_local",
        "adapterConfig": {
            "model": "gemini-2.5-pro",
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-growth-revenue-ops",
        ],
    },
    "Finance & Risk Manager": {
        "adapterType": "codex_local",
        "adapterConfig": {
            "model": "gpt-5.4",
            "modelReasoningEffort": "high",
            "dangerouslyBypassApprovalsAndSandbox": True,
            "extraArgs": ["--skip-git-repo-check"],
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-finance-risk-review",
        ],
    },
    "Customer Service Manager": {
        "adapterType": "pi_local",
        "adapterConfig": {
            "model": "minimax/MiniMax-M2.7",
            "thinking": "low",
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-customer-service-triage",
        ],
    },
    "People & Partners Manager": {
        "adapterType": "opencode_local",
        "adapterConfig": {
            "model": "openai/gpt-5.2",
            "dangerouslySkipPermissions": True,
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-people-partners-ops",
        ],
    },
    "Social & Media Manager": {
        "adapterType": "gemini_local",
        "adapterConfig": {
            "model": "gemini-2.5-pro",
            "env": {"HOME": "/home/.paperclip"},
        },
        "desiredSkills": [
            "ola-turmo/paperclip-role-skills/paperclip-operator-core",
            "ola-turmo/paperclip-role-skills/paperclip-social-media-command",
        ],
    },
}


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def create_workspace_dir(ssh_target: str, container: str, company_id: str) -> str:
    workspace_dir = f"/home/.paperclip/instances/default/company-workspaces/{company_id}"
    subprocess.run(
        [
            "ssh",
            ssh_target,
            f"docker exec {container} sh -lc 'mkdir -p {workspace_dir} && chmod 755 {workspace_dir}'",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--referer", default=DEFAULT_REFERER)
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--ssh-target", default=DEFAULT_SSH_TARGET)
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument(
        "--summary-path",
        default=str(Path(__file__).resolve().parents[1] / "apply-summary.json"),
    )
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(
        {
            "Origin": args.base_url,
            "Referer": args.referer,
            "Content-Type": "application/json",
        }
    )

    companies_resp = session.get(f"{args.base_url}/api/companies", timeout=60)
    companies_resp.raise_for_status()
    companies = companies_resp.json()
    if not isinstance(companies, list):
      companies = companies.get("items", [])

    summary: list[dict] = []

    for company in companies:
        company_id = company["id"]
        company_name = company["name"]
        workspace_dir = create_workspace_dir(args.ssh_target, args.container, company_id)

        import_resp = session.post(
            f"{args.base_url}/api/companies/{company_id}/skills/import",
            json={"source": args.repo_url},
            timeout=120,
        )
        import_resp.raise_for_status()
        imported = import_resp.json()

        agents_resp = session.get(
            f"{args.base_url}/api/companies/{company_id}/agents",
            timeout=60,
        )
        agents_resp.raise_for_status()
        agents = agents_resp.json()
        if not isinstance(agents, list):
            agents = agents.get("items", [])

        company_result = {
            "company": company_name,
            "companyId": company_id,
            "importedSkills": [item["key"] for item in imported.get("imported", [])],
            "agents": [],
        }

        for agent in agents:
            agent_name = agent["name"]
            role_config = ROLE_RUNTIME.get(agent_name)
            if not role_config:
                company_result["agents"].append(
                    {"name": agent_name, "status": "skipped", "reason": "no role mapping"}
                )
                continue

            patch_body = {
                "adapterType": role_config["adapterType"],
                "adapterConfig": {
                    **role_config["adapterConfig"],
                    "cwd": workspace_dir,
                },
            }
            patch_resp = session.patch(
                f"{args.base_url}/api/agents/{agent['id']}",
                json=patch_body,
                timeout=120,
            )
            patch_resp.raise_for_status()

            sync_resp = session.post(
                f"{args.base_url}/api/agents/{agent['id']}/skills/sync",
                json={"desiredSkills": role_config["desiredSkills"]},
                timeout=180,
            )
            sync_resp.raise_for_status()
            sync_result = sync_resp.json()

            snapshot_resp = session.get(
                f"{args.base_url}/api/agents/{agent['id']}/skills",
                timeout=120,
            )
            snapshot_resp.raise_for_status()
            snapshot = snapshot_resp.json()

            company_result["agents"].append(
                {
                    "name": agent_name,
                    "adapterType": patch_body["adapterType"],
                    "desiredSkills": sync_result.get("desiredSkills", []),
                    "supported": snapshot.get("supported"),
                    "mode": snapshot.get("mode"),
                    "warnings": snapshot.get("warnings", []),
                    "entryCount": len(snapshot.get("entries", [])),
                }
            )

        summary.append(company_result)

    summary_path = Path(args.summary_path)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
