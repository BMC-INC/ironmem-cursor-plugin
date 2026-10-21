# Validation and release boundary

The package validator checks Cursor manifest fields, portable component paths,
frontmatter, every MCP variable declaration, a direct stdio command, and the
absence of shipped runtime binaries or personal data files. The installer tests
cover path quoting, backups, idempotence, and refusal of unsafe destinations.

`scripts/smoke_mcp.py --binary PATH` exercises the MCP configuration against a
real executable. It initializes the protocol, lists the tools, checks status,
saves a synthetic project fact, retrieves it, and rejects malformed destructive
confirmations. Settings and SQLite data live in a temporary directory. No
personal store, provider credentials, or remote MCP endpoint are used.

CI runs package validation and installer tests on Linux, macOS, and Windows.
It does not rebuild IronMem's Rust runtime or claim a Cursor GUI observation.
Run the smoke test against a built runtime when changing MCP configuration or
instructions that depend on its tool contract.

Local Cursor acceptance requires copying the plugin to
`~/.cursor/plugins/local/ironmem`, reloading Cursor, checking the components in
Customize, and calling `get_status` from Cursor. A successful standalone MCP
smoke test verifies transport compatibility; it does not establish that a
specific Cursor window loaded the package. Record those outcomes separately.

Cursor 3.26.13 was observed loading this plugin from the local plugin directory.
Its local loader passed an unsubstituted `${IRONMEM_BINARY}` to process spawning
when only a variable default was present. The local installer therefore renders
an absolute MCP command and removes configuration variables from that local
copy. The published package keeps the variable and requires explicit Marketplace
configuration. Installer tests assert that local MCP commands contain no
unresolved variable tokens.

## Recorded local acceptance: 2026-10-21

- Cursor 3.26.13 on macOS loaded the installed local plugin. After rendering its
  executable path, Cursor's own MCP registry reported
  `plugin-ironmem-ironmem`, `tools=27`, `status=connected`.
- The real stdio smoke test saved and retrieved a synthetic fact in a disposable
  store, rejected six malformed wipe confirmations, preserved the store during
  preview, and deleted its fixture only on Boolean confirmation.
- The five plugin installer tests passed, including backup retention,
  idempotence, literal executable paths, and rollback after replacement failure.
- The separately installed runtime was built from IronMem commit
  `56c39ce4fccc7cbba2ffb603de6cb648048a3e41`, using `cargo build --release --locked`
  with no extra features. Its SHA-256 was
  `f92d2ab05d7d6898bf773d601359e4436730b1f6912b5dd5df2904f693f84c7c`.
  Its seven installation/reliability checks passed. A fresh stdio connection
  using the configured Claude command and the running REST/HTTP MCP services
  also passed status checks after installation.

These are recorded results for that build and machine. Current package CI is
reported by this repository's GitHub Actions runs. An approved Marketplace
listing and an end-to-end AI coding evaluation are separate evidence.

Marketplace publication also requires Cursor's manual review. This repository
does not submit itself, cut an IronMem release, or imply an approved listing.
Before submission, verify the current repository URL, package checks, privacy
and license links, installation instructions, and locally observed behavior.

To roll back a local plugin update, move the current local copy aside and restore
the previous plugin directory from the backup path printed by the installer,
then reload Cursor. Do not restore an old IronMem runtime over a migrated memory
store; runtime rollback has its own database backup procedure in the core repo.
