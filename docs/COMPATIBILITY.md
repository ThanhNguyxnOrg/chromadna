# Agent and Client Compatibility

ChromaDNA exposes two separate local integration surfaces:

- **Agent Skill:** reusable instructions and workflows in the Agent Skills format.
- **MCP server:** local Python tools exposed over stdio.

A client may support Skills, MCP, both, or neither. Support in a coding CLI does not imply support in its consumer chat website.

## One-prompt installation

For users who prefer an AI to perform setup, copy the prompt in [Install ChromaDNA with an AI Agent](INSTALL_WITH_AI.md) into an agent with terminal and filesystem access. The prompt instructs the agent to inspect the environment, install the Skill, configure native MCP adapters, verify the result, and report unsupported clients. It explicitly prohibits publishing or changing repository visibility.

## One-command local setup

The GitHub repository is public and can be cloned without authentication. The package is not currently published to npm or PyPI. Clone it, then run:

\`\`\`bash
node scripts/setup.mjs --all
\`\`\`

Preview first with \`--dry-run\`. Select one adapter with \`--agent=pi\`, \`--agent=opencode\`, \`--agent=cline\`, etc. The script installs the Skill through the Vercel Skills CLI and writes only the selected native MCP configuration. Existing ChromaDNA entries are preserved unless \`--force\` is supplied. Existing JSON files are backed up before modification.

## Integration matrix

| Client / family | Agent Skill | Local MCP | Setup / notes |
|---|---:|---:|---|
| Claude Code | Yes | Yes | Skills CLI; project \`.mcp.json\` |
| Claude Desktop | N/A | Yes | User-level Claude Desktop MCP config |
| Cursor | Yes | Yes | Skills CLI; project \`.cursor/mcp.json\` |
| Windsurf | Yes | Yes | Skills CLI; user-level \`~/.codeium/windsurf/mcp_config.json\` |
| OpenCode | Yes | Yes | Skills CLI; project \`opencode.json\` using local MCP server config |
| Pi coding agent | Yes | Yes | Skills CLI; project \`.pi/mcp.json\`; project trust is required |
| Cline | Yes | Yes | Skills CLI; Cline MCP settings; path may be overridden by \`CLINE_MCP_SETTINGS_PATH\` |
| Roo Code | Yes | Yes | Skills CLI; project \`.roo/mcp.json\` |
| Gemini CLI | Yes | Yes | Skills CLI; project \`.gemini/settings.json\` |
| Antigravity | Yes | Yes | Skills CLI; project \`.agents/mcp_config.json\` |
| Kimi Code CLI / Desktop | Yes | Yes | Skills CLI; project \`.kimi-code/mcp.json\` |
| VS Code / GitHub Copilot | Supported where enabled | Yes | Skills CLI; project \`.vscode/mcp.json\` |
| Codex CLI | Yes | Manual | Skills CLI; use \`codex mcp add\` for local MCP |
| DeepSeek Harness (DSH) | Host-dependent | Yes, via Harness plugin | Configure \`@deepseek-ai/dsh-mcp-client\` in a Cordis profile; not the consumer DeepSeek chat website |
| Groq API | No general local Skill target | Remote MCP only | Groq Responses API remote MCP is beta and requires an HTTPS endpoint |
| ChatGPT web | Product-surface dependent | Remote MCP only | Local stdio is not reachable from ChatGPT web; account/workspace connector availability applies |
| Claude web / Cowork | Product-surface dependent | Remote MCP only | Requires a reachable remote MCP server and connector setup |
| Grok web | No universal local install | Remote MCP connector | Requires a reachable remote MCP server |
| DeepSeek consumer chat | Not verified | Not verified | Do not infer Harness capabilities apply to the consumer chat product |
| Muse | Release-dependent | Release-dependent | Treat preview plugin surfaces as experimental |

The Vercel Skills CLI supports a broad and growing set of coding agents, including OpenCode, Pi, Cline, Roo Code, Windsurf, Kimi Code CLI, Codex, Cursor, Claude Code, and Antigravity. Its compatibility list is the source of truth for current Skills targets: https://github.com/vercel-labs/skills/blob/main/docs/agents.md.

## Native MCP configuration details

The setup script automates project or user-level MCP configuration for these clients:

- Claude Code: \`.mcp.json\`
- Claude Desktop: platform-specific user configuration file
- Cursor: \`.cursor/mcp.json\`
- Windsurf: \`~/.codeium/windsurf/mcp_config.json\`
- OpenCode: \`opencode.json\`, \`mcp.servers.chromadna\`
- Pi: \`.pi/mcp.json\`
- Gemini CLI: \`.gemini/settings.json\`
- Kimi Code: \`.kimi-code/mcp.json\`
- Roo Code: \`.roo/mcp.json\`
- Cline: user-level Cline MCP settings (honors \`CLINE_MCP_SETTINGS_PATH\`)
- Antigravity: \`.agents/mcp_config.json\`
- VS Code / Copilot: \`.vscode/mcp.json\`

Codex CLI can be configured with:

\`\`\`bash
codex mcp add chromadna -- uv run --project /absolute/path/to/chromadna chromadna-mcp
\`\`\`

Restart or reload the client after configuration. Project-local MCP entries may require trusting the workspace before they are started.

## DeepSeek Harness (DSH)

DeepSeek Harness is a host/plugin integration, not a generic local desktop MCP config file. Its documented bridge is \`@deepseek-ai/dsh-mcp-client\`. Add an entry like this to the Cordis overlay/profile used by the Harness deployment:

\`\`\`yaml
- insert:
    - id: mcp-chromadna
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: chromadna
        transport: stdio
        command: uv
        args:
          - run
          - --project
          - /absolute/path/to/chromadna
          - chromadna-mcp
        cwd: /absolute/path/to/chromadna
        env:
          CHROMADNA_CATALOG: /absolute/path/to/chromadna/data/color_dna_catalog.json
\`\`\`

Replace the absolute paths with the actual checkout path. The Harness host must have Python dependencies and \`uv\` available in its runtime. A new Harness session may be required before the tools appear. The bridge exposes MCP tools under names such as \`mcp__chromadna__list_color_dna\`.

## Groq API

Groq documents remote MCP support in its Responses API (currently beta). This is an API integration, not a local IDE client adapter. It requires an HTTPS MCP endpoint reachable by Groq's servers and a Groq API request that declares the MCP tool. ChromaDNA currently ships only a local stdio server, so there is no hosted ChromaDNA URL to paste into Groq. Do not create a public unauthenticated endpoint.

Official guide: https://console.groq.com/docs/tool-use/remote-mcp.

## Cloud chat products and remote MCP

ChatGPT web, Claude web / Cowork, and Grok web cannot access a local filesystem path merely because a user attached an image to a conversation. The current ChromaDNA server is local stdio only and is not a hosted remote service.

A future cloud service needs authenticated users, upload handling, per-user isolation, file-size limits, temporary storage with expiry, and downloadable artifacts. Do not expose the local stdio server directly to the public internet, use an unauthenticated tunnel, or accept arbitrary remote filesystem paths.

## Installation and verification requirements

- Python 3.10+, \`uv\`, Node.js 22.20+, and npm.
- The GitHub repository is private. Users need existing GitHub access to clone it.
- The setup script does not publish packages, create releases, make the repository public, or change Git history.
- It does not install client applications that are missing.
- JSON settings are merged and backed up. Existing ChromaDNA entries are preserved unless \`--force\` is supplied.
- After setup, restart each configured client and verify the MCP server status and tool list.
- Validate XMP and LUT files in their target applications. ChromaDNA's preview renderer and LUT exporter are approximations, not exact Adobe Camera Raw rendering.
