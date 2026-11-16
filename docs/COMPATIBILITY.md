# Agent and Client Compatibility

ChromaDNA has two independent integration surfaces:

- **Agent Skill:** instructions and workflow knowledge installed through the Agent Skills ecosystem.
- **MCP server:** executable tools exposed through a local stdio process.

A client supporting one surface does not automatically support the other.

## Setup from an authenticated checkout

The repository is private and is not published to npm or PyPI. Clone it using an account with repository access, then run:

```bash
node scripts/setup.mjs --all
```

The setup command delegates Skill installation to the Vercel Skills CLI and writes project-local MCP entries for Claude Code, Cursor, Antigravity, and VS Code / GitHub Copilot. It preserves unrelated JSON keys, backs up existing configuration files, and leaves an existing ChromaDNA entry untouched unless --force is supplied.

Preview changes with --dry-run. Install only one surface with --skills or --mcp. Limit MCP setup with --agent=cursor, --agent=claude-code, --agent=antigravity, or --agent=vscode.

## Integration matrix

| Client / family | Agent Skill | Local MCP | Setup notes |
|---|---:|---:|---|
| Claude Code | Yes | Yes | Skills CLI and project .mcp.json |
| Cursor | Yes | Yes | Skills CLI and .cursor/mcp.json |
| Antigravity | Yes | Yes | Skills CLI and .agents/mcp_config.json |
| VS Code / GitHub Copilot | Supported where Skills are enabled | Yes | Skills CLI and .vscode/mcp.json |
| Windsurf | Skills CLI where supported | Manual | Add local stdio server in MCP settings |
| OpenCode | Skills CLI | Manual | Configure local stdio in OpenCode config |
| Gemini CLI | Skills CLI | Manual | Configure MCP using Gemini CLI settings |
| Codex | Skills CLI / bundled plugin | Manual | Install the local plugin or run `codex mcp add chromadna -- uv run --project /absolute/path/to/chromadna chromadna-mcp` |
| Cline / Roo Code | Skills CLI where supported | Manual | Configure stdio in extension MCP settings |
| Kimi Code CLI | Skills CLI where supported | Manual | Follow the installed client MCP schema |
| ChatGPT web | Product-surface dependent | Remote MCP only | A local stdio process is not reachable from ChatGPT web |
| Claude web / Cowork | Product-surface dependent | Remote MCP only | Connect a reachable remote MCP server |
| Grok web | No universal local install | Remote MCP connector | Configure a reachable remote MCP endpoint |
| DeepSeek Chat | Not verified | Not verified | Do not confuse Harness / SDK support with native consumer-chat support |
| Muse | Release dependent | Release dependent | Treat preview plugin surfaces as experimental |

## Cloud assistants and remote MCP

The current ChromaDNA server is local stdio only and accepts filesystem paths visible to its process. It is not a remote service. ChatGPT web, Claude web, and Grok web cannot access a local path merely because a user attached an image to a conversation.

Do not expose this stdio server to the public internet or accept arbitrary remote filesystem paths. A future remote integration needs authenticated uploads, per-user isolation, bounded file sizes, temporary storage with expiry, and downloadable artifacts. This setup does not deploy such a service.

## Privacy and limitations

- This installer does not publish packages or make the repository public.
- The repository remains private; users must already have GitHub access.
- MCP configuration files are project-local; global user configuration is not modified.
- Only four project MCP adapters are written automatically. Other clients are documented as manual integrations rather than receiving potentially incompatible config.
- Restart each client after configuration and verify its MCP tool list.
