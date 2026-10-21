# Privacy

The plugin contains configuration and agent instructions. It has no telemetry
client, hosted backend, automatic event recorder, or cloud credentials. Its MCP
configuration starts the separately installed `ironmem mcp` process using stdio.
It does not expose a network listener or change IronMem's settings.

## Memory and recall

IronMem normally stores memories, observations, embeddings, and governance
records in `~/.ironmem/mem.db`. A configured database URL can move that storage
to another machine. This plugin's remember skill passes user-approved facts to
IronMem; its recall skill passes a project path and query, then brings returned
evidence into Cursor's context. Project paths, saved text, and queries therefore
reach the local runtime. Retrieved memory can also reach Cursor's selected model
provider as part of the assistant's context. Cursor's own processing and privacy
settings are outside this plugin.

IronMem's runtime can independently call external services. Session compression
defaults to local, and automatic cloud embedding fallback defaults to off.
These settings are not a global network switch. Explicit cloud embeddings,
profile refresh, enabled LLM
reranking, Observer, synthesis, scored benchmarks, custom remote Ollama URLs,
remote storage, model downloads, and public HTTP/tunnel operation each have
separate behavior. This plugin does not enable any of them. Existing settings
and credentials still apply. Read the core
[privacy disclosure](https://github.com/BMC-INC/Iron-mem/blob/main/PRIVACY.md)
before using those features.

## Development installer and checks

`scripts/install_plugin.py` copies this repository's plugin files to Cursor's
local plugin folder, records the selected executable path in that copy, and
backs up a previous differing copy. It reads the executable's `--version` output.
It does not read the memory database or alter assistant settings.

The optional MCP smoke test uses a temporary directory, a synthetic fact, a
restricted environment, and explicit settings with local compression, no
embeddings, no reranking, no Observer, and no automatic synthesis. Its report
contains aggregate results and the tested executable's SHA-256, not personal
memories. CI package checks do not connect to a personal database.

## Removal and support

Removing the plugin disconnects its components; it does not erase runtime data.
IronMem's backups, SQLite sidecars, snapshots, and generated context files may
retain copies after application-level deletion. Never attach your database,
credentials, personal context files, or complete conversation logs to a public
issue. Use the private reporting process in [SECURITY.md](SECURITY.md).
