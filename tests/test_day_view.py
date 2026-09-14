"""My Day's behaviour, against a stand-in for the Plugin API.

The window is pinned to 2026-09-14, so it runs 2026-09-11 to 2026-09-17.
"""
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend
from backend.day_view import DayView
from backend.routes import build_router

TODAY = date(2026, 9, 14)

INDEX = {
    "Adnoc": {"stem": "Adnoc", "path": "Work/Customers/Adnoc/Adnoc.md",
              "frontmatter": {"type": "Customer", "name": "Adnoc"}, "tags": ["customer/adnoc"]},
    "G42": {"stem": "G42", "path": "Work/Partners/G42/G42.md",
            "frontmatter": {"type": "Partner", "name": "G42"}, "tags": ["partner/g42"]},
    "Pricing call": {"stem": "Pricing call", "path": "Work/Threads/Pricing call/Pricing call.md",
                     "frontmatter": {"type": "Thread", "thread_name": "Pricing call",
                                     "last_message_at": "2026-09-14T09:00:00", "conversation_id": "c1"},
                     "tags": ["partner/g42", "customer/adnoc"]},
    "Old thread": {"stem": "Old thread", "path": "Work/Threads/Old thread/Old thread.md",
                   "frontmatter": {"type": "Thread", "thread_name": "Old", "last_message_at": "2026-09-01T09:00:00"},
                   "tags": []},
    "msg-1": {"stem": "msg-1", "path": "x", "tags": [],
              "frontmatter": {"type": "RawMessage", "conversation_id": "c1", "received": "2026-09-13T08:00", "sender": "Bob"}},
    "msg-2": {"stem": "msg-2", "path": "x", "tags": [],
              "frontmatter": {"type": "RawMessage", "conversation_id": "c1", "received": "2026-09-14T08:59", "sender": "Alice"}},
    "Weekly": {"stem": "Weekly", "path": "Work/Meetings/Weekly/Weekly.md",
               "frontmatter": {"type": "Meeting", "subject": "Weekly sync", "tags": ["customer/adnoc"]},
               "tags": ["customer/adnoc"]},
    "2026-09-15 Weekly": {"stem": "2026-09-15 Weekly",
                          "path": "Work/Meetings/Weekly/occurrences/2026-09-15 Weekly.md",
                          "frontmatter": {"type": "Meeting", "start": "2026-09-15T10:00"}, "tags": []},
}

TASKS = {
    "Work/Tasks/a.md": {"subject": "Send proposal", "due": "2026-09-20"},
    "Work/Tasks/b.md": {"subject": "Book travel", "due": None},
    "Work/Tasks/c.md": {"subject": "Done already", "status": "Completed", "due": "2026-09-10"},
    "Work/Tasks/d.md": {"subject": "Call back", "due": "2026-09-16", "customer": "Adnoc"},
}


class FakeVault:
    def index(self):
        return dict(INDEX)

    def notes_in_kind(self, kind):
        return list(TASKS) if kind == "Tasks" else []

    def read_note(self, path):
        return dict(TASKS[path]), ""


class FakePipelines:
    def get(self, pipeline_id):
        if pipeline_id == "threads-builder":
            return {"id": pipeline_id, "name": "Threads", "cron_job_id": "job-threads", "cron_profile_id": "profile-a"}
        return None


class FakeHermes:
    def __init__(self):
        self.runs = []

    def run_cron_job(self, job_name, profile_id=None):
        self.runs.append((job_name, profile_id))
        return True


class FakeApi:
    def __init__(self):
        self.plugin_id = "my-day"
        self.vault = FakeVault()
        self.pipelines = FakePipelines()
        self.hermes = FakeHermes()
        self.routers = []
        self.subject_enrichers = []

    def register_router(self, router):
        self.routers.append(router)

    def register_subject_enricher(self, enricher):
        self.subject_enrichers.append(enricher)


@pytest.fixture()
def api():
    return FakeApi()


@pytest.fixture()
def view(api):
    return DayView(api, today=lambda: TODAY)


def test_register_wires_a_router_and_the_customer_enricher(api):
    backend.register(api)

    assert len(api.routers) == 1
    assert len(api.subject_enrichers) == 1


def test_emails_are_windowed_with_the_customer_and_latest_sender(view):
    [item] = view.list_email_items()

    assert item == {
        "subject": "Pricing call", "sender": "Alice", "customer": "Adnoc",
        "received": "2026-09-14T09:00:00", "stem": "Pricing call",
    }


def test_emails_for_one_day(view):
    assert len(view.list_email_items("2026-09-14")) == 1
    assert view.list_email_items("2026-09-15") == []


def test_a_meeting_occurrence_inherits_its_series_subject_and_customer(view):
    [item] = view.list_calendar_items()

    assert item == {"subject": "Weekly sync", "start": "2026-09-15T10:00", "customer": "Adnoc", "stem": "2026-09-15 Weekly"}


def test_open_tasks_only_dated_first_undated_last(view):
    subjects = [item["subject"] for item in view.list_todo_items()]

    assert subjects == ["Call back", "Send proposal", "Book travel"]


def test_refresh_triggers_configured_pipelines_and_reports_the_rest(view, api):
    results = view.trigger_refresh()

    assert results == [
        {"pipeline_id": "threads-builder", "triggered": True, "detail": "triggered"},
        {"pipeline_id": "meeting-builder", "triggered": False, "detail": "no cron job configured"},
    ]
    assert api.hermes.runs == [("job-threads", "profile-a")]


def test_summary_counts_and_always_the_full_window(view):
    assert view.summary("2026-09-15") == {
        "emails": {"count": 0},
        "calendar": {"count": 1},
        "todo": {"count": 3},
        "window": {"start": "2026-09-11", "end": "2026-09-17"},
    }


def test_the_customer_enricher_prefers_the_customer_over_a_partner(view):
    assert view.customer_subject_enricher("email", {}, ["partner/g42", "customer/adnoc"]) == {"customer": "Adnoc"}
    assert view.customer_subject_enricher("email", {}, ["partner/g42"]) == {}


def test_the_router_serves_the_screens_and_rejects_a_day_outside_the_window(view):
    app = FastAPI()
    app.include_router(build_router(view), prefix="/plugins/my-day")
    client = TestClient(app)

    assert client.get("/plugins/my-day/emails").status_code == 200
    assert client.get("/plugins/my-day/summary", params={"day": "2026-09-01"}).status_code == 400
    assert client.post("/plugins/my-day/refresh").status_code == 200
