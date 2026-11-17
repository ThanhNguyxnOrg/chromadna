# Security Policy

## Supported versions

Security fixes are made against the latest version on the `main` branch. Older GitHub Releases may not receive backported fixes.

## Reporting a vulnerability

Please do **not** report exploitable vulnerabilities in a public issue or pull request.

Use GitHub's private vulnerability reporting for this repository:

[Report a vulnerability privately](https://github.com/ThanhNguyxnOrg/chromadna/security/advisories/new)

Include the affected version or commit, the impact, reproducible steps, and a suggested mitigation when available. Do not include private photographs, RAW files, API keys, or unrelated personal data.

If GitHub private vulnerability reporting is unavailable, contact the repository maintainers through the GitHub organization or maintainer profile contact channel. Avoid publishing exploit details until maintainers have had an opportunity to investigate.

## Scope notes

The local MCP server operates with the permissions of the user running it and accepts filesystem paths visible to that process. Do not expose the stdio server directly to the public internet. Report path-boundary, unsafe file-write, dependency, or credential-exposure vulnerabilities privately.
