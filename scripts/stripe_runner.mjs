import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import Stripe from "stripe";

function parseTomlConfig(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  const lines = raw.split(/\r?\n/);
  let section = null;
  const out = {};
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const sectionMatch = /^\[(.+)\]$/.exec(trimmed);
    if (sectionMatch) {
      section = sectionMatch[1];
      out[section] = out[section] || {};
      continue;
    }
    const match = /^([^=]+)=(.+)$/.exec(trimmed);
    if (!match || !section) continue;
    const key = match[1].trim();
    const value = match[2].trim().replace(/^'/, "").replace(/'$/, "");
    out[section][key] = value;
  }
  return out;
}

function loadPolicy() {
  const file = process.env.PROVIDER_POLICY_PATH;
  if (!file) throw new Error("PROVIDER_POLICY_PATH is required");
  return JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/, ""));
}

async function main() {
  const args = process.argv.slice(2);
  const companyIndex = args.indexOf("--company");
  if (companyIndex === -1 || !args[companyIndex + 1]) {
    throw new Error("--company is required");
  }
  const company = args[companyIndex + 1];
  args.splice(companyIndex, 2);
  const command = args[0];
  if (!command) throw new Error("command is required");

  const policy = loadPolicy();
  const companyPolicy = policy.providers.stripe.companies[company];
  if (!companyPolicy) throw new Error(`No stripe policy for ${company}`);
  if (String(companyPolicy.mode).startsWith("deny")) {
    throw new Error(companyPolicy.forbiddenUsecases[0] || `Stripe denied for ${company}`);
  }

  const home = process.env.STRIPE_HOME || path.join(os.homedir(), ".config", "stripe");
  const configPath = path.join(home, "config.toml");
  const parsed = parseTomlConfig(configPath);
  const projectName = process.env.STRIPE_PROJECT || "default";
  const profile = parsed[projectName];
  if (!profile) throw new Error(`Stripe profile '${projectName}' not found`);

  const secretKey = process.env.STRIPE_LIVE_MODE === "1" ? profile.live_mode_api_key : profile.test_mode_api_key;
  if (!secretKey) throw new Error("Stripe API key missing from profile");

  const allowed = new Set(companyPolicy.allowedOperations || []);
  if (!allowed.has(command)) {
    throw new Error(`Stripe operation '${command}' is not allowed for ${company}`);
  }

  if (command === "whoami") {
    console.log(JSON.stringify({
      company,
      projectName,
      accountId: profile.account_id || null,
      displayName: profile.display_name || null,
      liveModeConfigured: Boolean(profile.live_mode_api_key),
      testModeConfigured: Boolean(profile.test_mode_api_key),
    }, null, 2));
    return;
  }

  const stripe = new Stripe(secretKey);
  let data;
  switch (command) {
    case "list-products":
      data = await stripe.products.list({ limit: 20 });
      break;
    case "list-prices":
      data = await stripe.prices.list({ limit: 20 });
      break;
    case "list-customers":
      data = await stripe.customers.list({ limit: 20 });
      break;
    case "list-payment-links":
      data = await stripe.paymentLinks.list({ limit: 20 });
      break;
    case "list-subscriptions":
      data = await stripe.subscriptions.list({ limit: 20, status: "all" });
      break;
    case "list-invoices":
      data = await stripe.invoices.list({ limit: 20 });
      break;
    default:
      throw new Error(`Unsupported Stripe command '${command}'`);
  }
  console.log(JSON.stringify(data, null, 2));
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
