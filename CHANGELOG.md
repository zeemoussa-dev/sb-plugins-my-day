# CHANGELOG

All notable changes to the My Day plugin. The framework (Second Brain) is a separate
repository and is never copied in here.

## [Unreleased]

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
