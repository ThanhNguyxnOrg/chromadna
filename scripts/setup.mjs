#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const home = os.homedir();
const argv = process.argv.slice(2);
const has = (flag) => argv.includes(flag);
const all = has("--all");
const installSkills = all || has("--skills");
const installMcp = all || has("--mcp");
const dryRun = has("--dry-run");
const force = has("--force");
const requested = argv.filter((arg) => arg.startsWith("--agent=")).map((arg) => arg.slice(8));
const skillAgent = requested.length ? requested : ["*"];
const knownAgents = ["claude-code","claude-desktop","cursor","antigravity","vscode","opencode","pi","gemini-cli","kimi-code-cli","cline","roo","windsurf","codex"];
const mcpTargets = ["claude-code","claude-desktop","cursor","antigravity","vscode","opencode","pi","gemini-cli","kimi-code-cli","roo","cline","windsurf"];
const agents = requested.length ? requested : mcpTargets;

function usage() {
  console.log([
    "ChromaDNA multi-agent setup",
    "Usage: node scripts/setup.mjs --all [--dry-run]",
    "       node scripts/setup.mjs --skills [--agent=pi]",
    "       node scripts/setup.mjs --mcp [--agent=opencode]",
    "Options: --all --skills --mcp --agent=NAME --dry-run --force --help",
    "Skill targets: " + knownAgents.join(", ") + " (or * for all Skills CLI targets)",
    "MCP adapters: " + mcpTargets.join(", "),
    "DeepSeek Harness and Groq API require their documented integration paths; see docs/COMPATIBILITY.md.",
    "Run from an authenticated checkout. No package publishing or repository visibility changes are performed."
  ].join("\n"));
}
if (has("--help") || has("-h")) { usage(); process.exit(0); }
if (!installSkills && !installMcp) { usage(); process.exit(2); }
if (requested.some((agent) => !knownAgents.includes(agent))) {
  console.error("Unknown agent. Supported names: " + knownAgents.join(", "));
  process.exit(2);
}

const rootPath = root.split(path.sep).join("/");
const catalogPath = path.join(rootPath, "data", "color_dna_catalog.json").split(path.sep).join("/");
const localServer = { command: "uv", args: ["run", "--project", rootPath, "chromadna-mcp"], env: { CHROMADNA_CATALOG: catalogPath } };

function readJson(file) {
  if (!fs.existsSync(file)) return {};
  try { return JSON.parse(fs.readFileSync(file, "utf8")); }
  catch (error) { throw new Error("Cannot parse " + file + ": " + error.message); }
}
function writeJson(file, value) {
  if (dryRun) { console.log("[dry-run] write " + file); return; }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  if (fs.existsSync(file)) {
    const backup = file + ".chromadna.bak";
    if (!fs.existsSync(backup)) fs.copyFileSync(file, backup);
  }
  const temp = file + ".chromadna.tmp";
  fs.writeFileSync(temp, JSON.stringify(value, null, 2) + "\n", "utf8");
  fs.renameSync(temp, file);
  console.log("Configured " + file);
}
function mergeEntry(file, keyPath, entry) {
  const config = readJson(file);
  let target = config;
  for (const key of keyPath.slice(0, -1)) {
    if (target[key] === undefined) target[key] = {};
    if (!target[key] || typeof target[key] !== "object" || Array.isArray(target[key])) {
      throw new Error("Cannot safely merge " + file + ": " + key + " is not an object.");
    }
    target = target[key];
  }
  const finalKey = keyPath.at(-1);
  if (target[finalKey] && !force) {
    console.log("Preserved existing entry " + keyPath.join(".") + " in " + file + " (use --force to replace).");
    return;
  }
  target[finalKey] = entry;
  writeJson(file, config);
}
function addTarget(agent) {
  const project = (relative) => path.join(root, relative);
  const stdio = { ...localServer };
  switch (agent) {
    case "claude-code": mergeEntry(project(".mcp.json"), ["mcpServers","chromadna"], stdio); break;
    case "claude-desktop": {
      const file = process.platform === "win32"
        ? path.join(process.env.APPDATA || path.join(home,"AppData","Roaming"),"Claude","claude_desktop_config.json")
        : process.platform === "darwin"
          ? path.join(home,"Library","Application Support","Claude","claude_desktop_config.json")
          : path.join(home,".config","Claude","claude_desktop_config.json");
      mergeEntry(file, ["mcpServers","chromadna"], stdio); break;
    }
    case "cursor": mergeEntry(project(".cursor/mcp.json"), ["mcpServers","chromadna"], stdio); break;
    case "antigravity": mergeEntry(project(".agents/mcp_config.json"), ["mcpServers","chromadna"], stdio); break;
    case "vscode": mergeEntry(project(".vscode/mcp.json"), ["servers","chromadna"], { type:"stdio", ...stdio }); break;
    case "opencode": mergeEntry(project("opencode.json"), ["mcp","servers","chromadna"], { type:"local", command:["uv", ...stdio.args], environment:stdio.env, enabled:true }); break;
    case "pi": mergeEntry(project(".pi/mcp.json"), ["mcpServers","chromadna"], stdio); break;
    case "gemini-cli": mergeEntry(project(".gemini/settings.json"), ["mcpServers","chromadna"], stdio); break;
    case "kimi-code-cli": mergeEntry(project(".kimi-code/mcp.json"), ["mcpServers","chromadna"], stdio); break;
    case "roo": mergeEntry(project(".roo/mcp.json"), ["mcpServers","chromadna"], stdio); break;
    case "cline": {
      const candidates = [
        process.env.CLINE_MCP_SETTINGS_PATH,
        path.join(home,".cline","data","settings","cline_mcp_settings.json"),
        path.join(home,".cline","mcp.json")
      ].filter(Boolean);
      const file = candidates.find((candidate) => fs.existsSync(candidate)) || candidates[1];
      mergeEntry(file, ["mcpServers","chromadna"], stdio); break;
    }
    case "windsurf": mergeEntry(path.join(home,".codeium","windsurf","mcp_config.json"), ["mcpServers","chromadna"], stdio); break;
    default: throw new Error("No MCP adapter for " + agent);
  }
}

if (installMcp) {
  for (const agent of agents) {
    if (!mcpTargets.includes(agent)) {
      console.log("Skipped " + agent + ": no safe automatic MCP adapter; see docs/COMPATIBILITY.md.");
      continue;
    }
    addTarget(agent);
  }
}
if (installSkills) {
  const skillDir = path.join(root,"skills","chromadna");
  if (!fs.existsSync(path.join(skillDir,"SKILL.md"))) throw new Error("Missing canonical skills/chromadna/SKILL.md");
  if (dryRun) {
    console.log("[dry-run] install ChromaDNA Skill via Vercel Skills CLI for: " + skillAgent.join(", "));
  } else {
    const command = process.platform === "win32" ? "npx.cmd" : "npx";
    const args = ["--yes","skills","add",root,"--skill","chromadna","--yes","--copy"];
    for (const agent of skillAgent) args.push("--agent",agent);
    const result = spawnSync(command,args,{cwd:root,stdio:"inherit",shell:process.platform==="win32"});
    if (result.error) throw result.error;
    if (result.status !== 0) process.exit(result.status || 1);
  }
}
console.log("Setup finished. Restart configured clients and verify their MCP server/tool status.");
console.log("Cloud APIs (ChatGPT web, Claude web, Grok web, and Groq API) need a hosted remote MCP endpoint; local stdio is not reachable by those services.");
