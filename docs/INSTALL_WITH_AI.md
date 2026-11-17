# Install ChromaDNA with an AI Agent

Copy the complete prompt below into an AI coding agent that has terminal and file-system access (for example Claude Code, Codex, Cursor, Windsurf, OpenCode, Pi, Cline, Roo Code, Gemini CLI, Kimi Code CLI, or another capable agent).

---

## Copy/paste prompt

You are an installation agent. Install and configure **ChromaDNA** for the current machine and the AI agent/client I am using.

Repository: https://github.com/ThanhNguyxnOrg/chromadna

### Goals

1. Install the ChromaDNA Agent Skill so this agent can discover and use it.
2. Install the local ChromaDNA MCP server wherever this client supports local stdio MCP.
3. Configure other detected, supported coding agents on this machine when safe and useful.
4. Verify the installation instead of merely writing configuration files.
5. Do not publish anything, change repository visibility, create releases, or push commits.

### Procedure

1. Inspect the current workspace and operating system. If this repository is already checked out, use that checkout. Otherwise, clone the public repository URL without requiring GitHub authentication. Do not ask the user to paste passwords, access tokens, SSH private keys, or other secrets. If cloning fails, verify the URL, network connectivity, Git availability, and any organization-level access restrictions; do not assume the repository is private.
2. Read README.md, docs/COMPATIBILITY.md, skills/chromadna/SKILL.md, and pyproject.toml before making changes.
3. Check for Python 3.10+, uv, Node.js 22.20+, and npm. Install only missing prerequisites when the environment and package manager permit it; otherwise give exact installation instructions. Do not replace existing runtimes or alter unrelated environment settings.
4. From the repository root, run:
   - node scripts/setup.mjs --skills --dry-run
   - Review the Skill installation plan.
   - node scripts/setup.mjs --skills
   - Detect which supported MCP clients are actually installed or configured. Use `node scripts/setup.mjs --mcp --dry-run --agent=<client>` for each detected client, then run the same command without `--dry-run` after reviewing the changes. Multiple `--agent` flags may be passed in one invocation.
   - Use `node scripts/setup.mjs --all` only if the user explicitly wants configuration entries created for every supported MCP adapter, including clients that are not installed.
   Do not force-replace an existing ChromaDNA configuration unless the user explicitly asks.
5. The Skills CLI supports many Agent Skills-compatible coding agents. Install the Skill for the current client and other detected clients where supported. Do not claim that a model provider's consumer chat website supports local Skills just because its coding CLI does.
6. Install MCP only through the native configuration format documented for the detected client. The setup script currently automates Claude Code/Desktop, Cursor, Antigravity, VS Code, OpenCode, Pi, Gemini CLI, Kimi Code CLI, Roo Code, Cline, and Windsurf. If another client is present, follow its official integration documentation and add it only if the format and location are verified. Preserve unrelated configuration and keep backups.
7. For DeepSeek Harness, use its @deepseek-ai/dsh-mcp-client Cordis plugin configuration as documented in docs/COMPATIBILITY.md; do not mistake the Harness SDK/host integration for native support in the DeepSeek consumer chat website.
8. For Groq, explain that its Responses API supports remote MCP in beta. It requires a reachable HTTPS MCP endpoint and a Groq API integration; local stdio configuration alone is not sufficient. Do not invent a hosted ChromaDNA URL.
9. Cloud chat products such as ChatGPT web, Claude web, and Grok web require a hosted, reachable remote MCP service and any required account-level connector setup. The current repository provides a local stdio server only. Do not expose it to the public internet, create a tunnel, deploy infrastructure, or upload user photos without explicit approval.
10. Verify:
    - python -m pip install -e .
    - python -m pytest -q
    - chromadna --help
    - uv run --project . chromadna-mcp using a real MCP initialize/list-tools handshake where feasible.
    - Check each edited JSON file parses, each configured client points to the correct checkout, and each client recognizes the Skill/MCP server after restart.
11. If a client is not installed, do not install the entire client application just to add ChromaDNA. Report it as not present. If a native integration is unavailable or cannot be verified, provide the exact manual steps and label it as manual/unsupported rather than claiming success.
12. Finish with a concise report listing: installed Skill targets, configured MCP clients, validation results, clients needing manual setup, and any blockers.

### Safety and scope

- Do not publish to npm or PyPI.
- Do not change the GitHub repository visibility.
- Do not create GitHub releases, tags, commits, branches, or pull requests.
- Do not upload or commit user photos, RAW files, or third-party preset packs.
- Do not overwrite unrelated settings. Back up any existing file before editing.
- Ask before installing system packages, changing global settings beyond the documented MCP entries, or granting broad permissions.
- Keep MCP tool approvals enabled; do not auto-approve file writes or destructive operations.
- Be honest: ChromaDNA previews and exported LUTs are approximations, not pixel-identical Adobe Camera Raw renders.

Start by inspecting the current environment and repository. Proceed with safe local installation without asking me to repeat information already available.