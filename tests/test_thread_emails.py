"""The emails one Thread is made of -- My Day's Cockpit tab (framework API v3).

This lives here rather than in the framework: the Cockpit is a generic component for
chatting with agents about a subject, and knowing that a Thread is made of emails in a
`messages/` folder is knowledge about email, which is this plugin's (operator,
2026-09-24)."""
import pytest

from backend.thread_emails import ThreadEmails

MESSAGE = """---
type: "RawMessage"
sender: "{sender}"
sender_email: "{email}"
subject: "{subject}"
received: "{received}"
---

body
"""


class Vault:
    """The slice of the Plugin API this reader uses."""

    def __init__(self, index):
        self._index = index

    def index(self):
        return dict(self._index)

    def read_note(self, path):
        text = open(path, encoding="utf-8").read()
        frontmatter = {}
        if text.startswith("---"):
            for line in text.split("---")[1].strip().splitlines():
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip('"')
        return frontmatter, text


class Api:
    def __init__(self, index):
        self.vault = Vault(index)


@pytest.fixture()
def thread(tmp_path):
    folder = tmp_path / "Work" / "Threads" / "Pricing call"
    (folder / "messages").mkdir(parents=True)
    note = folder / "Pricing call.md"
    note.write_text('---\ntype: "Thread"\n---\n', encoding="utf-8")
    for sender, email, subject, received in [
        ("Tim Burke", "tburke@masdar.ae", "Re: Pricing", "2026-09-17 20:13:22+00:00"),
        ("Amr Elsayed", "amraze@microsoft.com", "RE: Pricing", "2026-09-22 13:05:01+00:00"),
    ]:
        (folder / "messages" / f"{received[:10]}-{sender}.md").write_text(
            MESSAGE.format(sender=sender, email=email, subject=subject, received=received), encoding="utf-8")
    return ThreadEmails(Api({"Pricing call": {"stem": "Pricing call", "path": str(note)}})), folder


def test_every_email_is_listed_newest_first(thread):
    emails, _ = thread

    listed = emails.list_for("Pricing call")

    assert [email["sender"] for email in listed] == ["Amr Elsayed", "Tim Burke"]
    assert listed[0]["subject"] == "RE: Pricing"
    assert listed[0]["sender_email"] == "amraze@microsoft.com"
    # Each email is a real note, so the tab can link straight to it.
    assert listed[0]["stem"] == "2026-09-22-Amr Elsayed"


def test_a_note_in_the_folder_that_is_not_a_message_is_left_out(thread):
    emails, folder = thread
    (folder / "messages" / "mine.md").write_text('---\ntype: "Note"\n---\n', encoding="utf-8")

    assert len(emails.list_for("Pricing call")) == 2


def test_a_subject_with_no_messages_folder_lists_nothing(tmp_path):
    """A Meeting, or a Thread captured before the folder existed -- not an error."""
    note = tmp_path / "meeting.md"
    note.write_text('---\ntype: "Meeting"\n---\n', encoding="utf-8")
    emails = ThreadEmails(Api({"meeting": {"stem": "meeting", "path": str(note)}}))

    assert emails.list_for("meeting") == []


def test_an_unknown_subject_lists_nothing():
    assert ThreadEmails(Api({})).list_for("nope") == []
