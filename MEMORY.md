# MEMORY

Standing rules for this repository — what an agent must know to change the My Day
plugin without breaking an install. Rules only: no history, no narrative.

**Scope.** This file covers **this plugin only**. Second Brain (the framework) is
a separate repository with its own memory; nothing about its internals belongs
here, and a session opened here does not know them. A capability this plugin needs
and the Plugin API lacks is recorded here and raised there.

---

- **[2026-09-17] The Plugin API is the only way in.** The backend imports
  `app.plugin_api` and nothing else from the framework; the screens import only
  their own files, `src/pluginHost/`, and react / react-router. Publishing refuses
  anything else, and the rule exists because a reached-past import breaks on the
  next framework change while `framework_api` still matches.
- **[2026-09-17] `framework_api` must equal the host's exactly.** A mismatch is
  refused at load, with the reason on System Health. When the framework moves that
  version, republish this plugin against it -- it will not load otherwise.
- **[2026-09-17] Customers belong to the Entities plugin.** Ask
  `get_service("entities.customers")` at call time, never in `register` (plugins
  load in install order), and treat `None` as normal: without Entities installed
  My Day shows no customer and still works.
- **[2026-09-17] My Day registers no Cockpit subject enricher.** Cockpit's
  customer field is the Entities plugin's; adding one here would mean two plugins
  claiming the same field.
- **[2026-09-17] Refresh triggers the real capture Pipelines' own cron jobs**
  (`threads-builder`, `meeting-builder`) and returns when the trigger is sent, not
  when capture finishes. A Pipeline with no cron job is reported, never silently
  skipped.
- **[2026-09-17] Every change ships through publishing.** `publish_plugin.py <repo>
  --dry-run` runs the manifest, layout, import-boundary, test and screen-build
  gates; a published version is immutable, so a change means a new `version`.
