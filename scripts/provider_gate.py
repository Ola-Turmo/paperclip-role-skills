import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = Path("/home/.paperclip/provider-tooling/provider-governance.json")
if not DEFAULT_POLICY_PATH.exists():
    DEFAULT_POLICY_PATH = ROOT / "references" / "provider-governance.json"


def load_policy(path: Path):
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def company_policy(policy: dict, provider: str, company: str):
    provider_policy = policy["providers"][provider]
    if company not in provider_policy["companies"]:
        raise SystemExit(f"No {provider} policy for company {company}")
    return provider_policy["companies"][company]


def classify_cloudflare(args: list[str]) -> str:
    joined = " ".join(args).lower()
    if any(token in joined for token in [" browser", " flagship", " artifact"]):
        return "unsupported"
    if any(token in joined for token in [" delete", " remove", " purge", " rollback", " teardown"]):
        return "destructive"
    if args[:1] == ["email"]:
        if any(token in joined for token in [" create", " put", " add", " enable", " disable", " update", " set", " issue", " configure"]):
            return "write"
        return "read"
    if args[:1] == ["whoami"]:
        return "identity"
    if any(token in joined for token in [" deploy", " publish", " apply", " create", " put", " secret", " migrate", " upload"]):
        return "write"
    return "read"


def classify_zapier(args: list[str]) -> str:
    if not args:
        return "catalog"
    command = args[0]
    if command in {"get-profile", "login", "logout"}:
        return "identity"
    if command in {"apps", "integrations", "describe", "history", "versions", "version", "logs"}:
        return "catalog"
    if command in {"env", "users", "team", "analytics", "jobs"}:
        return "connection-read"
    if command in {"build", "validate", "init", "scaffold", "convert", "link", "pull"}:
        return "build"
    if command in {"invoke"}:
        return "action-run"
    if command in {"push", "upload", "register", "promote", "migrate", "deprecate", "legacy", "canary", "delete"}:
        return "credentials-mutate"
    if command in {
        "list-apps",
        "get-app",
        "list-actions",
        "get-action",
        "list-input-fields",
        "list-input-field-choices",
        "get-input-fields-schema",
    }:
        return "catalog"
    if command in {"list-connections", "get-connection", "find-first-connection", "find-unique-connection"}:
        return "connection-read"
    if command in {"init", "add", "build-manifest", "generate-app-types", "bundle-code", "mcp"}:
        return "build"
    if command in {"run-action"}:
        return "action-run"
    if command in {"create-client-credentials", "delete-client-credentials"}:
        return "credentials-mutate"
    if command in {
        "create-table",
        "create-table-fields",
        "create-table-records",
        "delete-table",
        "delete-table-fields",
        "delete-table-records",
        "update-table-records",
    }:
        return "table-mutate"
    return "catalog"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=["cloudflare", "zapier"])
    parser.add_argument("--company", required=True)
    parser.add_argument("--policy-path", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    policy = load_policy(Path(args.policy_path))
    cp = company_policy(policy, args.provider, args.company)

    if cp["mode"].startswith("deny"):
        raise SystemExit(f"{args.provider} access denied for {args.company}: {cp['forbiddenUsecases'][0]}")

    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise SystemExit("No command provided")

    cmd_class = classify_cloudflare(command) if args.provider == "cloudflare" else classify_zapier(command)
    allowed = set(cp.get("allowedCommandClasses", []))
    if cmd_class not in allowed:
        raise SystemExit(f"{args.provider} command class '{cmd_class}' is not allowed for {args.company}")

    if args.provider == "cloudflare":
        tool_root = Path("/home/.paperclip/provider-tooling/cloudflare")
        env = os.environ.copy()
        env["HOME"] = str(tool_root / "home")
        cli = tool_root / "node_modules" / ".bin" / "wrangler"
        result = subprocess.run([str(cli), *command], env=env)
        return result.returncode

    tool_root = Path("/home/.paperclip/provider-tooling/zapier")
    env = os.environ.copy()
    env["HOME"] = str(tool_root / "home")
    env["XDG_CONFIG_HOME"] = str(tool_root / "home" / ".config")
    env["APPDATA"] = str(tool_root / "home" / ".config")
    env["ZAPIER_SUPPRESS_DEPRECATION_WARNING"] = "1"
    cli = tool_root / "node_modules" / ".bin" / "zapier-platform"
    result = subprocess.run([str(cli), *command], env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
