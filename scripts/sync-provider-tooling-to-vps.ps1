param(
  [string]$SshTarget = "lovkode-vps",
  [string]$RemoteRoot = "/var/lib/docker/volumes/compose_paperclip-data/_data/provider-tooling",
  [string]$CloudflareVersion = "4.83.0",
  [string]$ZapierVersion = "0.38.2",
  [string]$StripeSdkVersion = "16.0.0"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$policyPath = Join-Path $repoRoot "references\provider-governance.json"
$providerGatePath = Join-Path $repoRoot "scripts\provider_gate.py"
$stripeRunnerPath = Join-Path $repoRoot "scripts\stripe_runner.mjs"

$wranglerConfig = "C:\Users\heial\.wrangler\config\default.toml"
$zapierConfig = "C:\Users\heial\AppData\Roaming\zapier-sdk-cli-nodejs\Config\config.json"
$zapierPlatformConfig = "C:\Users\heial\.zapierrc"
$stripeConfig = "C:\Users\heial\.config\stripe\config.toml"

ssh $SshTarget "mkdir -p $RemoteRoot/cloudflare/home/.wrangler/config $RemoteRoot/zapier/home/.config/zapier-sdk-cli-nodejs/Config $RemoteRoot/stripe/home/.config/stripe $RemoteRoot/bin"

scp $policyPath "${SshTarget}:$RemoteRoot/provider-governance.json"
scp $providerGatePath "${SshTarget}:$RemoteRoot/provider_gate.py"
scp $stripeRunnerPath "${SshTarget}:$RemoteRoot/stripe_runner.mjs"
scp $wranglerConfig "${SshTarget}:$RemoteRoot/cloudflare/home/.wrangler/config/default.toml"
scp $zapierConfig "${SshTarget}:$RemoteRoot/zapier/home/.config/zapier-sdk-cli-nodejs/Config/config.json"
scp $stripeConfig "${SshTarget}:$RemoteRoot/stripe/home/.config/stripe/config.toml"
ssh $SshTarget "cp $RemoteRoot/zapier/home/.config/zapier-sdk-cli-nodejs/Config/config.json $RemoteRoot/zapier/home/.config/zapier-sdk-cli-nodejs/config.json"
scp $zapierPlatformConfig "${SshTarget}:$RemoteRoot/zapier/home/.zapierrc"

$tempScript = Join-Path $env:TEMP "paperclip-provider-tooling-sync.sh"
$scriptBody = @'
set -e
ROOT="__REMOTE_ROOT__"

mkdir -p "$ROOT/cloudflare" "$ROOT/zapier" "$ROOT/stripe" "$ROOT/bin"

if [ ! -f "$ROOT/cloudflare/package.json" ]; then
  (cd "$ROOT/cloudflare" && npm init -y >/dev/null 2>&1)
fi
if [ ! -f "$ROOT/zapier/package.json" ]; then
  (cd "$ROOT/zapier" && npm init -y >/dev/null 2>&1)
fi
if [ ! -f "$ROOT/stripe/package.json" ]; then
  (cd "$ROOT/stripe" && npm init -y >/dev/null 2>&1)
fi

(cd "$ROOT/cloudflare" && npm install --silent "wrangler@__CLOUDFLARE_VERSION__")
(cd "$ROOT/zapier" && npm install --silent "@zapier/zapier-sdk-cli@__ZAPIER_VERSION__")
(cd "$ROOT/stripe" && npm install --silent "stripe@__STRIPE_SDK_VERSION__")

cat > "$ROOT/bin/paperclip-cloudflare" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="${REMOTE_ROOT:-/home/.paperclip/provider-tooling}"
python3 "$ROOT/provider_gate.py" --provider cloudflare "$@"
EOF

cat > "$ROOT/bin/paperclip-zapier" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="${REMOTE_ROOT:-/home/.paperclip/provider-tooling}"
python3 "$ROOT/provider_gate.py" --provider zapier "$@"
EOF

cat > "$ROOT/bin/paperclip-stripe" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="${REMOTE_ROOT:-/home/.paperclip/provider-tooling}"
export PROVIDER_POLICY_PATH="$ROOT/provider-governance.json"
export STRIPE_HOME="$ROOT/stripe/home/.config/stripe"
export STRIPE_SDK_ROOT="$ROOT/stripe"
node "$ROOT/stripe_runner.mjs" "$@"
EOF

chmod +x "$ROOT/bin/paperclip-cloudflare" "$ROOT/bin/paperclip-zapier" "$ROOT/bin/paperclip-stripe"
mkdir -p /home/.paperclip
ln -sfn "$ROOT" /home/.paperclip/provider-tooling

/home/.paperclip/provider-tooling/cloudflare/node_modules/.bin/wrangler --version
/home/.paperclip/provider-tooling/zapier/node_modules/.bin/zapier-sdk --version
/home/.paperclip/provider-tooling/bin/paperclip-stripe --company KUR whoami >/dev/null
'@
$scriptBody = $scriptBody.Replace('__REMOTE_ROOT__', $RemoteRoot).Replace('__CLOUDFLARE_VERSION__', $CloudflareVersion).Replace('__ZAPIER_VERSION__', $ZapierVersion).Replace('__STRIPE_SDK_VERSION__', $StripeSdkVersion)

[System.IO.File]::WriteAllText($tempScript, $scriptBody, [System.Text.UTF8Encoding]::new($false))
scp $tempScript "${SshTarget}:/root/paperclip-provider-tooling-sync.sh"
ssh $SshTarget "bash /root/paperclip-provider-tooling-sync.sh"
Remove-Item -LiteralPath $tempScript -Force
