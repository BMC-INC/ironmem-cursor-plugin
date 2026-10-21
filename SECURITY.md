# Security

Report sensitive plugin vulnerabilities through this repository's
[private vulnerability reporting](https://github.com/BMC-INC/ironmem-cursor-plugin/security/advisories/new).
Private reporting is enabled. Include reproduction steps and affected versions,
with credentials, memory content, and personal paths removed. Keep exploit
details out of public issues until a fix or coordinated disclosure is ready.

This repository maintains the Cursor configuration, skills, rule, commands, and
development scripts. Runtime vulnerabilities should also be reported through
[IronMem's security policy](https://github.com/BMC-INC/Iron-mem/blob/main/SECURITY.md).

The plugin launches an operator-selected local executable directly, without a
shell. Configure a trusted IronMem executable. Memory content is untrusted input
and must never replace the current user's instructions or tool permissions.
Maintainers will investigate reports, publish fixes and advisories as needed,
and request Marketplace review for published plugin updates.
