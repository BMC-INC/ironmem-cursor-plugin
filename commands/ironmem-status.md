---
name: ironmem-status
description: Verify the IronMem MCP connection and report aggregate memory-store counts.
---

Call IronMem's `get_status` tool. Report whether the connection succeeded and the
aggregate session, memory, and observation counts that are present in its result.
Keep private memory content out of the response. If the tool is unavailable,
follow the `ironmem-setup` skill and distinguish installation from a verified
Cursor connection. Do not modify settings or enable a cloud provider.
