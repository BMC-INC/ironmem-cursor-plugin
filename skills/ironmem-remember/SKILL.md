---
name: ironmem-remember
description: Save an explicit user-approved fact, preference, decision, or correction to IronMem with the appropriate project or user scope.
---

# Save a durable fact

1. Confirm the user's instruction identifies what to remember. Summarize the
   precise durable fact; exclude temporary speculation and whole transcripts.
2. For a project decision, call `remember` with `text`, the absolute `project`
   root, and `scope: "project"`. Use `scope: "user"` only for a cross-project
   preference or fact the user intended to retain. Choose a supported `kind`
   such as `preference`, `architecture`, `project_config`, or `error_solution`.
3. Do not save credentials, access tokens, or private third-party material.
   Sensitive personal information requires appropriate user consent and the
   runtime's governance fields. If consent is absent, leave it unsaved.
4. Inspect the tool result and report success only after IronMem confirms it.
   Surface a refusal or failure. Do not disable governance or retry with a less
   restrictive classification to force a write.
5. Record a correction with its evidence when replacing an outdated belief.
   Do not automatically wipe a project, delete source evidence, or refresh a
   provider-backed profile as part of saving a fact.
