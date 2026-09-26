# CHANGELOG

All notable changes to the My Day plugin. The framework (Second Brain) is a separate
repository and is never copied in here.

## [Unreleased]

- fix: the reader shows the thread's subject line, not its conversation id (1.6.1). A Thread carries its subject
  as `thread_name`; reading `subject`/`title` fell through to the stem, which on the real install is a bare GUID.
  The newest thread also opens by itself now, and a file whose note is titled after the file no longer repeats it.

- feat: the Emails tab reads a thread, instead of indexing it (1.6.0, framework API v6). A list beside a reader:
  the thread's `Summary`, the emails it is made of -- each one opening in place to read the captured text -- and
  the files that came attached, which open as the real file. Reading an email no longer means leaving the tab
  (operator, 2026-09-25: "the emails tab should include the related documents ... as well as the emails it self
  the thread summary. We need to make the email more useful"). The summary and the attachments come from the host
  (`vault.read_section`, `vault.attachments`) rather than being re-derived here, and bodies render through
  `NoteText`, so they read as the app renders vault text. Needs framework API v6.

- fix: a meeting hidden behind a same-named note is listed again (1.5.0, framework API v5, framework `BUG-076`).
  The framework's by-name index keeps one note per file name, and a meeting captured alongside its own invitation
  email shares that name -- so My Day listed four of the day's five meetings and counted four in the summary.
  The day view now sweeps `api.vault.entries()`, which is every note; `index()` stays for looking one up by name.
  Needs framework API v5, so this version will not load on an older host.

- feat: a Thread's own emails, as a tab inside the Cockpit (1.4.0, framework API v3, framework `ADR-025`). A captured Thread keeps one note per real email under its `messages/` folder; the Cockpit showed the Thread note, its people and its attachments, and never the emails. The framework briefly carried this itself, which made it know what a Thread is made of -- the operator's correction (2026-09-24): the Cockpit is a generic component for chatting with agents about a subject, and email is this plugin's domain. So `backend/thread_emails.py` reads the folder through the Plugin API, `GET /plugins/my-day/threads/{stem}/emails` serves it, and `ui/ThreadEmailsTab.tsx` is contributed through the host's new `cockpitTabs` contract. Needs framework API v3, so this version will not load on an older host.

- docs: `CLAUDE.md` and `MEMORY.md` for this repository (framework `ADR-023`): a session opened here works on
  this plugin alone, with the Plugin API boundary, the `framework_api` rule, and where customers come from.

## 1.3.0 — 2026-09-17

- feat: customers come from the Entities plugin's `entities.customers` service; My Day no longer carries its own
  resolver or Cockpit enricher. Without Entities installed, nothing has a customer and nothing fails.

## 1.2.0 — 2026-09-17

- chore: built against Plugin API v2. No behaviour change.

## 1.1.0 — 2026-09-17

- fix: the Pending Approvals card is gone. Its backend had been archived in the framework on 2026-08-20, so the
  card always read "Nothing awaiting approval" (framework `BUG-064`).

## 1.0.0 — 2026-09-14

- feat: My Day extracted from the framework -- summary, emails, calendar and to-do screens under `/my-day`,
  served by `/plugins/my-day/`, with its own tests. Behaviour unchanged from the framework's version.
