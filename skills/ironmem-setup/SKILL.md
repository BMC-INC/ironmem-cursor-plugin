---
name: ironmem-setup
description: Set up or diagnose IronMem's local MCP connection in Cursor when its tools are missing or unavailable.
---

# Connect IronMem

1. Check whether the IronMem MCP server and `get_status` tool are available.
   If they are, call `get_status` and report aggregate counts. Do not dump memories.
2. If unavailable, locate the installed executable. Standard locations are
   `$HOME/.ironmem/bin/ironmem` on macOS/Linux and
   `%USERPROFILE%\.ironmem\bin\ironmem.exe` on Windows. Verify it with `--version`.
   Do not download or execute an unrelated binary.
3. Set the plugin's `IRONMEM_BINARY` configuration to its absolute path, without
   shell quotes or extra arguments. The MCP definition already supplies `mcp`.
   For a local checkout, `scripts/install_plugin.py --binary PATH` creates a local
   copy with that default. Reload Cursor and enable the MCP server if prompted.
4. Avoid duplicate manual and plugin MCP entries. Preserve other servers and all
   existing memory data. No API key or public listener is needed for stdio.
5. Use IronMem's existing settings. Do not enable cloud features to repair an MCP
   connection. Explain optional provider data flows using the privacy disclosure.
6. Verify `get_status` through Cursor's actual MCP connection. Report a successful
   local command separately from an observed Cursor connection. If an admin
   policy blocks local imports, report that restriction rather than bypassing it.
