#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const argv = process.argv.slice(2);
const has = (flag) => argv.includes(flag);
const all = has("--all");
const skills = all || has("--skills");
const mcp = all || has("--mcp");
const dryRun = has("--dry-run");
const force = has("--force");
const supported = ["claude-code", "cursor", "antigravity", "vscode"];
const requested = argv.filter((x) => x.startsWith("--agent=")).map((x) => x.slice(8));
const agents = requested.length ? requested : supported;

function usage() { console.log(["ChromaDNA setup", "Usage: node scripts/setup.mjs --all [--dry-run]", "       node scripts/setup.mjs --skills", "       node scripts/setup.mjs --mcp --agent=cursor", "Options: --all --skills --mcp --agent=NAME --dry-run --force --help", "Supported MCP adapters: " + supported.join(", "), "Run from an authenticated checkout. This tool never publishes packages or changes repository visibility."].join("\n")); }
if (has("--help") || has("-h")) { usage(); process.exit(0); }
if (!skills && !mcp) { usage(); process.exit(2); }
if (agents.some((a) => !supported.includes(a))) { console.error("Unsupported agent. Supported: " + supported.join(", ")); process.exit(2); }

function readJson(file) { if (!fs.existsSync(file)) return {}; try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch (error) { throw new Error("Cannot parse " + path.relative(root, file) + ": " + error.message); } }
function writeJson(file, value) { if (dryRun) { console.log("[dry-run] write " + path.relative(root, file)); return; } fs.mkdirSync(path.dirname(file), { recursive: true }); if (fs.existsSync(file)) { const backup = file + ".chromadna.bak"; if (!fs.existsSync(backup)) fs.copyFileSync(file, backup); } fs.writeFileSync(file, JSON.stringify(value, null, 2) + "\n", "utf8"); console.log("Configured " + path.relative(root, file)); }
const rootPath = root.replaceAll("\\", "/");
const server = { command: "uv", args: ["run", "--project", rootPath, "chromadna-mcp"], env: { CHROMADNA_CATALOG: path.join(rootPath, "data", "color_dna_catalog.json").replaceAll("\\", "/") } };
const targets = { "claude-code": [".mcp.json", "mcpServers", server], "cursor": [".cursor/mcp.json", "mcpServers", server], "antigravity": [".agents/mcp_config.json", "mcpServers", server], "vscode": [".vscode/mcp.json", "servers", { type: "stdio", ...server }] };
if (mcp) { for (const agent of agents) { const [relative, key, entry] = targets[agent]; const file = path.join(root, relative); const config = readJson(file); config[key] ??= {}; if (config[key].chromadna && !force) { console.log("Preserved existing ChromaDNA entry in " + relative); continue; } config[key].chromadna = entry; writeJson(file, config); } }
if (skills) { if (!fs.existsSync(path.join(root, "SKILL.md"))) { console.error("Missing root SKILL.md"); process.exit(1); } if (dryRun) console.log("[dry-run] install the ChromaDNA Skill to all detected agents"); else { const command = process.platform === "win32" ? "npx.cmd" : "npx"; const result = spawnSync(command, ["--yes", "skills", "add", root, "--skill", "chromadna", "--agent", "*", "--yes", "--copy"], { cwd: root, stdio: "inherit", shell: process.platform === "win32" }); if (result.error) throw result.error; if (result.status !== 0) process.exit(result.status || 1); } }
console.log("Setup complete. Install Python dependencies, ensure uv is available, restart clients, and verify MCP tools.");
