# My Day — a Second Brain plugin

Your day at a glance: recent email, meetings around today, and open tasks, with
a manual refresh of the capture pipelines behind them.

| Part | Holds |
|---|---|
| `plugin.json` | id `my-day`, version, the framework API it is built for, and `requires: graph|outlook` |
| `backend/` | `register(api)`; routes served under `/plugins/my-day/` |
| `ui/` | the screens (`/my-day`, `/my-day/emails`, `/my-day/calendar`, `/my-day/todo`) and the sidebar entry |
| `tests/` | the plugin's own tests; run on publish, never packaged |

The plugin talks to the framework only through the Plugin API: `app.plugin_api`
in the backend and `src/pluginHost/` in the screens. Customers shown on emails
and meetings come from the Entities plugin's `entities.customers` service; with
Entities not installed, My Day shows no customers.

## Publish

From a Second Brain checkout:

```bash
src/backend/.venv/Scripts/python.exe src/backend/scripts/publish_plugin.py <path-to-this-repo>
```

It refuses to publish unless every check passes (manifest, layout, import
boundary, these tests, the screens building inside that framework) and never
overwrites a published version — bump `version` in `plugin.json` first. Then
install it from Settings → Marketplace and restart the backend.

## Tests

```bash
PYTHONPATH=<second-brain>/src/backend python -m pytest tests
```
