import argparse
import json
from collections import OrderedDict

import requests


DEFAULT_BASE_URL = "http://vps-apimcp-site.tail928971.ts.net:13101"
DEFAULT_REFERER = f"{DEFAULT_BASE_URL}/PAR/settings/agents"


ROLE_SKILL_ASSIGNMENTS = {
    "Personal": {
        "CEO": [
            "personal-admin-ops",
            "private-life-household-ops",
            "personal-health-decisions",
            "relationships-ops",
            "paperclip-zapier-governor",
        ],
        "Operations Manager": [
            "personal-admin-ops",
            "private-life-household-ops",
            "personal-health-decisions",
            "paperclip-zapier-governor",
        ],
        "People & Partners Manager": [
            "relationships-ops",
        ],
        "Growth & Revenue Manager": [
            "growth-revenue-experiments",
        ],
    },
    "Kurs.ing": {
        "CEO": [
            "kurs-ing-support-ops",
            "kurs-ing-customer-communication",
            "autonomous-host-operator",
            "host-sidecar-rollout",
            "quality-gates",
            "paperclip-stripe-governor",
        ],
        "Operations Manager": [
            "kurs-ing-support-ops",
            "autonomous-host-operator",
            "host-sidecar-rollout",
            "quality-gates",
            "paperclip-cloudflare-governor",
            "paperclip-zapier-governor",
            "paperclip-stripe-governor",
        ],
        "Customer Service Manager": [
            "kurs-ing-support-ops",
            "kurs-ing-customer-communication",
            "paperclip-zapier-governor",
        ],
        "Product & Tech Manager": [
            "cleanup-backend-worker",
            "cleanup-frontend-worker",
            "cleanup-repo-worker",
            "host-sidecar-rollout",
            "quality-gates",
            "paperclip-cloudflare-governor",
        ],
        "Growth & Revenue Manager": [
            "growth-revenue-experiments",
            "kurs-ing-customer-communication",
            "autonomous-host-operator",
            "publishing",
            "draft-gen",
            "deployed-url-audit",
            "paperclip-zapier-governor",
        ],
        "Social & Media Manager": [
            "kurs-ing-customer-communication",
            "publishing",
            "draft-gen",
            "quality-gates",
        ],
        "Finance & Risk Manager": [
            "quality-gates",
            "paperclip-stripe-governor",
        ],
    },
    "Gatareba.ge": {
        "CEO": ["gatareba-compliance-ops"],
        "Operations Manager": ["gatareba-compliance-ops", "devops", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Finance & Risk Manager": ["gatareba-compliance-ops", "reviewer"],
        "Product & Tech Manager": ["gatareba-compliance-ops", "backend-developer", "fullstack-developer", "reviewer", "paperclip-cloudflare-governor"],
        "Customer Service Manager": ["gatareba-compliance-ops", "paperclip-zapier-governor"],
        "Growth & Revenue Manager": ["growth-revenue-experiments", "gatareba-compliance-ops"],
    },
    "Lovkode.no": {
        "CEO": ["lovkode-matter-platform", "scrutiny-feature-reviewer"],
        "Operations Manager": ["lovkode-matter-platform", "infra-worker", "corpus-worker", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Finance & Risk Manager": ["lovkode-matter-platform", "scrutiny-feature-reviewer"],
        "Product & Tech Manager": ["lovkode-matter-platform", "ai-workflow-worker", "backend-worker", "fullstack-worker", "screen-fidelity-worker", "paperclip-cloudflare-governor"],
        "Customer Service Manager": ["lovkode-matter-platform", "humanize-klarsprak", "scrutiny-feature-reviewer"],
    },
    "Parallel Company AI": {
        "CEO": ["portfolio-repo-universe", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Operations Manager": ["portfolio-repo-universe", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Product & Tech Manager": ["portfolio-repo-universe", "paperclip-cloudflare-governor"],
        "Growth & Revenue Manager": ["portfolio-repo-universe"],
        "Finance & Risk Manager": ["paperclip-stripe-governor"],
    },
    "EmDash Sidecar SaaS": {
        "CEO": ["autonomous-host-operator", "host-sidecar-rollout", "quality-gates", "deployed-url-audit", "paperclip-cloudflare-governor"],
        "Operations Manager": ["autonomous-host-operator", "host-sidecar-rollout", "quality-gates", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Product & Tech Manager": ["design-clone", "design-import", "host-sidecar-rollout", "quality-gates", "paperclip-cloudflare-governor"],
        "Growth & Revenue Manager": ["autonomous-host-operator", "publishing", "draft-gen", "deployed-url-audit", "paperclip-zapier-governor"],
        "Social & Media Manager": ["publishing", "draft-gen"],
        "Finance & Risk Manager": ["paperclip-stripe-governor"],
    },
    "TRT.ge": {
        "CEO": ["trt-ge-authority-growth"],
        "Operations Manager": ["trt-ge-authority-growth", "paperclip-cloudflare-governor", "paperclip-zapier-governor"],
        "Product & Tech Manager": ["trt-ge-authority-growth", "paperclip-cloudflare-governor"],
        "Growth & Revenue Manager": ["growth-revenue-experiments", "trt-ge-authority-growth", "paperclip-zapier-governor"],
        "Social & Media Manager": ["trt-ge-authority-growth"],
        "Customer Service Manager": ["trt-ge-authority-growth", "paperclip-zapier-governor"],
    },
    "AI Influencer & Spokesperson Company": {
        "Agency CEO": ["agency-service-ops", "paperclip-finance-risk-review", "paperclip-cloudflare-governor", "paperclip-stripe-governor"],
        "Service Operations Lead": ["agency-service-ops", "paperclip-zapier-governor"],
        "Client Success Lead": ["agency-service-ops", "paperclip-customer-service-triage", "paperclip-people-partners-ops", "paperclip-zapier-governor"],
        "Growth Distribution Lead": ["agency-service-ops", "paperclip-social-media-command", "paperclip-zapier-governor"],
        "Media Systems Lead": ["agency-service-ops", "paperclip-cloudflare-governor"],
        "Talent Studio Lead": ["agency-service-ops"],
    },
}


def uniq(values):
    return list(OrderedDict.fromkeys(values))


def slug_from_key(key: str) -> str | None:
    parts = key.split("/")
    return parts[-1] if len(parts) >= 3 else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--referer", default=DEFAULT_REFERER)
    parser.add_argument(
        "--summary-path",
        default=r"C:\Users\heial\Documents\Codex\2026-04-20-company-repo-skills-sync\agent-repo-skill-assignment-summary.json",
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

    summary = []

    for company in companies:
        company_name = company["name"]
        company_id = company["id"]
        role_map = ROLE_SKILL_ASSIGNMENTS.get(company_name)
        if not role_map:
            continue

        skills_resp = session.get(f"{args.base_url}/api/companies/{company_id}/skills", timeout=60)
        skills_resp.raise_for_status()
        company_skills = skills_resp.json()
        slug_to_key = {}
        for skill in company_skills:
            slug = skill["slug"]
            key = skill["key"]
            if skill["sourceType"] == "github":
                slug_to_key[slug] = key
            elif slug not in slug_to_key:
                slug_to_key[slug] = key

        agents_resp = session.get(f"{args.base_url}/api/companies/{company_id}/agents", timeout=60)
        agents_resp.raise_for_status()
        agents = agents_resp.json()
        if not isinstance(agents, list):
            agents = agents.get("items", [])

        company_result = {"company": company_name, "updated": []}

        for agent in agents:
            desired_slugs = role_map.get(agent["name"])
            if not desired_slugs:
                continue

            extras = [slug_to_key[slug] for slug in desired_slugs if slug in slug_to_key]
            if not extras:
                company_result["updated"].append(
                    {"agent": agent["name"], "status": "skipped", "reason": "no matching company skills"}
                )
                continue

            skill_state_resp = session.get(f"{args.base_url}/api/agents/{agent['id']}/skills", timeout=60)
            skill_state_resp.raise_for_status()
            skill_state = skill_state_resp.json()
            current_desired = skill_state.get("desiredSkills", [])
            canonical_current = []
            for key in current_desired:
                slug = slug_from_key(key)
                if key.startswith("local/") and slug and slug in slug_to_key:
                    canonical_current.append(slug_to_key[slug])
                else:
                    canonical_current.append(key)
            merged = uniq(canonical_current + extras)

            sync_resp = session.post(
                f"{args.base_url}/api/agents/{agent['id']}/skills/sync?companyId={company_id}",
                json={"desiredSkills": merged},
                timeout=120,
            )
            sync_resp.raise_for_status()
            sync_result = sync_resp.json()

            company_result["updated"].append(
                {
                    "agent": agent["name"],
                    "addedSkills": [key for key in extras if key not in canonical_current],
                    "replacedLocalKeys": [key for key in current_desired if key.startswith("local/") and slug_from_key(key) in slug_to_key],
                    "desiredSkills": sync_result.get("desiredSkills", merged),
                }
            )

        summary.append(company_result)

    with open(args.summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
