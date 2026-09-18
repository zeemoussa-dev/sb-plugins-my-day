# CLAUDE.md — sb-plugins-my-day

Guidance for Claude Code working in **this** repository.

## What this repository is

The source of the **My Day plugin** for Second Brain: the screens and endpoints
that show a day at a glance — recent email, meetings around today, open tasks —
with a manual refresh of the capture pipelines behind them.

A published version of this plugin is installed into an install from its
Marketplace. The framework itself carries none of this.

## What this repository is not

- **Not the framework.** Second Brain is a **separate repository**. Its source
  never appears here, and this plugin may import only the Plugin API.
- **Not an agent's content.** Skills, Templates and business rules belong to an
  install's own repository.

## Layout

```
plugin.json     id, name, version, framework_api, requires
backend/        register(api); routes served under /plugins/my-day/
ui/             the screens and the sidebar entry
tests/          this plugin's own tests; run on publish, never packaged
```

## Rules

- **The backend imports `app.plugin_api` and nothing else** from the framework;
  its own modules import each other relatively. The screens import only their own
  files, `src/pluginHost/`, and react / react-router. Publishing refuses anything
  else.
- **`framework_api` must match the host exactly.** When the framework moves that
  version, this plugin is republished against it or it will not load.
- **Customers come from the Entities plugin** via `get_service("entities.customers")`,
  asked for at call time, not in `register`. With Entities absent, My Day shows no
  customer and still works.
- **Publish before believing anything.** `publish_plugin.py <repo> --dry-run` runs
  every gate: manifest, layout, import boundary, these tests, and a real build of
  the screens inside the framework.
- **Separate commits per logical change**, never skip hooks, never force-push.
  Update `CHANGELOG.md` and bump `version` for a change that ships.

## Tests

```bash
PYTHONPATH=<second-brain-checkout>/src/backend python -m pytest tests
```

They run against a stand-in for the Plugin API, so they need no install.
