"""The emails one Thread is made of -- My Day's Cockpit tab (framework API v3).

This lives here rather than in the framework: the Cockpit is a generic component for
chatting with agents about a subject, and knowing that a Thread is made of emails in a
`messages/` folder is knowledge about email, which is this plugin's (operator,
2026-09-24)."""
import pytest

from backend.thread_emails import MessageNotFoundError, SubjectNotFoundError, ThreadEmails

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

    def __init__(self, index, sections=None, attachments=None):
        self._index = index
        self._sections = sections or {}
        self._attachments = attachments or []

    def index(self):
        return dict(self._index)

    def read_note(self, path):
        text = open(path, encoding="utf-8").read()
        frontmatter = {}
        body = text
        if text.startswith("---"):
            _, header, body = text.split("---", 2)
            for line in header.strip().splitlines():
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip('"')
        return frontmatter, body.lstrip("\n")

    def read_section(self, path, header):
        """The host reads the note's own section (framework API v6); here it is
        whatever the test put there."""
        return self._sections.get(header)

    def attachments(self, subject_note_stem):
        return list(self._attachments)


class Api:
    def __init__(self, index, sections=None, attachments=None):
        self.vault = Vault(index, sections, attachments)


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
    api = Api(
        {"Pricing call": {"stem": "Pricing call", "path": str(note), "frontmatter": {"thread_name": "Pricing"}}},
        sections={"Summary": "Masdar asked for revised pricing; [[Adnoc]] terms apply."},
        attachments=[{"title": "Order form", "filename": "Order-Form.pdf",
                      "note_path": str(folder / "Files" / "Order-Form" / "Order-Form.md")}],
    )
    return ThreadEmails(api), folder


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


# -- what the Emails tab reads ------------------------------------------------------


def test_the_thread_detail_carries_its_summary_emails_and_files(thread):
    """Operator, 2026-09-25: the tab should hold the thread's summary, its emails
    and the documents that came attached -- so reading the mail does not mean
    opening three screens."""
    emails, _ = thread

    detail = emails.detail_for("Pricing call")

    # A Thread's subject line is its `thread_name`; its stem is the conversation
    # id, which on the real install is a bare GUID.
    assert detail["subject"] == "Pricing"
    assert detail["summary"] == "Masdar asked for revised pricing; [[Adnoc]] terms apply."
    assert [email["sender"] for email in detail["emails"]] == ["Amr Elsayed", "Tim Burke"]
    # The stem, not the path: the screen links to the real file through it.
    assert detail["attachments"] == [
        {"title": "Order form", "filename": "Order-Form.pdf", "stem": "Order-Form"},
    ]


def test_a_thread_whose_summary_is_not_written_yet_says_so_rather_than_empty(tmp_path):
    note = tmp_path / "Pricing call.md"
    note.write_text('---\ntype: "Thread"\n---\n', encoding="utf-8")
    emails = ThreadEmails(Api({"Pricing call": {"stem": "Pricing call", "path": str(note)}}))

    assert emails.detail_for("Pricing call")["summary"] is None


def test_an_unknown_thread_is_not_an_empty_thread():
    with pytest.raises(SubjectNotFoundError):
        ThreadEmails(Api({})).detail_for("nope")


def test_one_email_comes_back_with_the_text_that_was_captured(thread):
    emails, _ = thread

    email = emails.body_for("Pricing call", "2026-09-22-Amr Elsayed")

    assert email["sender_email"] == "amraze@microsoft.com"
    assert email["body"].strip() == "body"


def test_a_message_stem_cannot_name_a_note_outside_the_thread(thread):
    """A stem arrives from a URL, and two notes may share a name (framework
    `BUG-076`) -- so the email is addressed inside its own Thread's folder."""
    emails, _ = thread

    with pytest.raises(MessageNotFoundError):
        emails.body_for("Pricing call", "../Pricing call")


def test_a_note_in_the_folder_that_is_not_a_message_cannot_be_read_as_one(thread):
    emails, folder = thread
    (folder / "messages" / "mine.md").write_text('---\ntype: "Note"\n---\n\nprivate\n', encoding="utf-8")

    with pytest.raises(MessageNotFoundError):
        emails.body_for("Pricing call", "mine")
