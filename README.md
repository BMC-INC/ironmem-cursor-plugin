# IronMem for Cursor

<img src="assets/ironmem.png" alt="IronMem" width="240">

Local-first project memory for Cursor. Recall relevant project decisions, keep
user-approved facts, and expand remembered evidence through IronMem's MCP tools.

[![Package checks](https://github.com/BMC-INC/ironmem-cursor-plugin/actions/workflows/validate.yml/badge.svg)](https://github.com/BMC-INC/ironmem-cursor-plugin/actions/workflows/validate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

[Install locally](#install-the-plugin-locally) · [Use it](#use-it) · [Validation](docs/VALIDATION.md) · [Privacy](PRIVACY.md)

## At a glance

| | |
| --- | --- |
| Purpose | Bring project decisions and source-backed recall into Cursor. |
| Package | Version 0.1.1; skills, commands, a rule, and a stdio MCP definition. |
| Runtime | IronMem is installed separately; this plugin ships no executable. |
| Availability | Local installation is supported. Marketplace approval is not claimed. |
| Capture | Explicit recall and user-requested saving; no automatic conversation capture. |

This is the Cursor plugin repository. The Rust runtime lives in
[BMC-INC/Iron-mem](https://github.com/BMC-INC/Iron-mem) and continues to support
Claude Code, Claude Desktop, and other MCP clients independently.

The plugin is free and Apache-2.0 licensed. It includes a stdio MCP definition,
three skills, one context rule, and three commands. The plugin itself has no
network client, analytics, automatic transcript recording, or runtime binaries.
IronMem's independently configured features and Cursor's model requests have
their own data flows, described in [PRIVACY.md](PRIVACY.md).

## Prerequisite: install IronMem

Use the IronMem 0.4.1 release or a 0.4.0 build from commit
[`56c39ce`](https://github.com/BMC-INC/Iron-mem/commit/56c39ce4fccc7cbba2ffb603de6cb648048a3e41)
or later. The version number alone does not distinguish older 0.4.0 builds.
Follow the core project's
[installation instructions](https://github.com/BMC-INC/Iron-mem#install).
Source installation currently needs Rust/Cargo, Python 3.9+, and Git. Use
`--no-hooks` with the core installer for a Cursor-only setup; Claude Code's
lifecycle hooks are independent of this plugin.

The standard installed executable is:

| Platform | Executable |
| --- | --- |
| macOS / Linux | `$HOME/.ironmem/bin/ironmem` |
| Windows | `%USERPROFILE%\.ironmem\bin\ironmem.exe` |

Verify it with `--version`. Local memory storage does not require a cloud API
key. The plugin does not install or upgrade the runtime, download executables,
or start an HTTP listener.

## Install the plugin locally

From a checkout of this repository, run one of these commands. Python 3.9+ is
needed for this development installer, not for the plugin's normal MCP operation.

```sh
git clone https://github.com/BMC-INC/ironmem-cursor-plugin.git
cd ironmem-cursor-plugin
```

macOS / Linux:

```sh
python3 scripts/install_plugin.py --binary "$HOME/.ironmem/bin/ironmem"
```

Windows PowerShell:

```powershell
py -3 scripts/install_plugin.py --binary "$env:USERPROFILE\.ironmem\bin\ironmem.exe"
```

This copies the plugin into `~/.cursor/plugins/local/ironmem` and puts the
absolute executable path directly into the local copy's MCP configuration. It preserves
Cursor's other MCP servers and settings. An existing different plugin copy is
retained in a backup before replacement; identical reinstalls write nothing.
The source repository and installed runtime are unchanged by this command.
Local copies contain a resolved command, since Cursor's local loader does not
substitute Marketplace variable defaults. Rerun this installer if the binary moves.

Restart Cursor or run **Developer: Reload Window**, then open **Customize** and
check that IronMem's skills, rule, commands, and MCP server are present. Enable
the MCP server if Cursor prompts. Team policies can block local plugin imports.
Cursor ignores local plugin symlinks pointing outside its local plugin folder,
so use the copy installer rather than a symlink.

If IronMem is already configured manually in Cursor, use one IronMem server
entry to avoid duplicate connections. The installer leaves existing entries
alone so you can choose which one to keep.

## Marketplace configuration

This repository is prepared for review; it is not an approved Marketplace
listing. After installing through a marketplace, set `IRONMEM_BINARY` in the
plugin's **Configure** settings to the absolute executable path. This is a
required configuration value. Enter the path alone, without quotes or `mcp`
arguments. A bare `ironmem` command works only when it is visible on Cursor's
PATH; GUI applications may have a different PATH from your terminal.

No token, hosted account, public endpoint, or HTTP bearer credential is required
for the stdio integration. The plugin inherits the runtime's existing settings;
review optional cloud features before enabling them.

## Use it

- **ironmem-setup** checks installation, connection, and storage configuration.
- **ironmem-recall** finds project evidence and expands exact originals when needed.
- **ironmem-remember** saves a fact the user has asked to keep.
- **/ironmem-status** checks the connection and reports aggregate store counts.
- **/ironmem-recall** recalls evidence for the current task.
- **/ironmem-remember** records an approved fact for the current project.

The rule keeps recall scoped to the current project and treats remembered
content as evidence to verify. Saving information requires user intent. This
plugin does not add Cursor lifecycle hooks or automatically capture tool input,
tool output, or whole conversations.

For a first check in Cursor, run **/ironmem-status**, then ask it to remember a
harmless project fact and recall that fact in the same project. A connected
server plus a successful save-and-recall is the acceptance check; simply seeing
the plugin's name in Customize is not enough. Review the recalled source before
using memory to make a consequential change.

## Verify the package

```sh
python3 scripts/check_plugin.py
python3 -m unittest discover -s tests -v
python3 scripts/smoke_mcp.py --binary "$HOME/.ironmem/bin/ironmem"
```

On Windows, substitute `py -3` and the `.exe` path. The smoke test launches the
actual stdio MCP command from `mcp.json` with a temporary database and explicit
local-only settings. It initializes MCP, checks the tools, saves and retrieves a
synthetic fact, and verifies malformed wipe confirmations are refused. It never
opens your personal memory database. See [validation](docs/VALIDATION.md).

## Uninstall

Remove this plugin through Cursor, or move its local copy out of
`~/.cursor/plugins/local/ironmem`, and reload the window. Disable any separately
configured IronMem MCP entry if you also want to disconnect it. This leaves
IronMem's runtime, memory database, other assistants, and plugin backups intact.

## Support and terms

Use this repository's [issues](https://github.com/BMC-INC/ironmem-cursor-plugin/issues)
for plugin problems. Report sensitive vulnerabilities through
[SECURITY.md](SECURITY.md). See [privacy](PRIVACY.md), [terms](TERMS.md), and
[Apache-2.0 license](LICENSE).

Authoring references: [Cursor plugins](https://cursor.com/docs/plugins),
[plugin reference](https://cursor.com/docs/reference/plugins), and
[Marketplace security](https://cursor.com/help/security-and-privacy/marketplace-security).
