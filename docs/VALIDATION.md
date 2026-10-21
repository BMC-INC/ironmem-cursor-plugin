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

Marketplace publication also requires Cursor's manual review. This repository
does not submit itself, cut an IronMem release, or imply an approved listing.
Before submission, verify the current repository URL, package checks, privacy
and license links, installation instructions, and locally observed behavior.

To roll back a local plugin update, move the current local copy aside and restore
the previous plugin directory from the backup path printed by the installer,
then reload Cursor. Do not restore an old IronMem runtime over a migrated memory
store; runtime rollback has its own database backup procedure in the core repo.
