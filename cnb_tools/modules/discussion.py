"""Module for managing Synapse Discussion forums, threads, and replies.

Provides a low-level class (``DiscussionApi``) that wraps the Synapse REST
API for discussions, plus convenience free-functions for common operations.
"""

import json
import re
import urllib.request
from dataclasses import dataclass
from typing import Iterator

from synapseclient import Synapse

from cnb_tools.modules.client import get_synapse_client


def _camel_to_snake(name: str) -> str:
    """Convert a camelCase string to snake_case."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


def _from_dict(cls: type, data: dict):
    """Construct a dataclass from an API response dict, converting camelCase keys."""
    converted = {_camel_to_snake(k): v for k, v in data.items()}
    return cls(**{k: v for k, v in converted.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Dataclasses for discussion objects
# ---------------------------------------------------------------------------


@dataclass
class Forum:
    """Represents a Synapse Forum."""

    id: str
    project_id: str
    etag: str | None = None


@dataclass
class Thread:
    """Represents a Synapse discussion thread."""

    id: str
    forum_id: str
    title: str
    created_on: str
    modified_on: str
    created_by: str
    message_key: str
    etag: str | None = None
    is_deleted: bool = False
    is_edited: bool = False
    is_pinned: bool = False


@dataclass
class Reply:
    """Represents a reply inside a Synapse discussion thread."""

    id: str
    thread_id: str
    forum_id: str
    created_on: str
    modified_on: str
    created_by: str
    message_key: str
    etag: str | None = None
    is_deleted: bool = False
    is_edited: bool = False


# ---------------------------------------------------------------------------
# DiscussionApi class
# ---------------------------------------------------------------------------


class DiscussionApi:
    """Low-level wrapper around the Synapse Discussion REST API.

    Args:
        syn: An authenticated Synapse client. If not provided, one will be
            created automatically via ``get_synapse_client()``.
    """

    def __init__(self, syn: Synapse | None = None):
        self.syn = syn or get_synapse_client()

    # -- Forum ----------------------------------------------------------------

    def get_project_forum(self, project_id: str) -> Forum:
        """
        Args:
            project_id: Synapse ID of the project.
        """
        result = self.syn.restGET(f"/project/{project_id}/forum")
        return _from_dict(Forum, result)

    def get_forum(self, forum_id: str) -> Forum:
        """
        Args:
            forum_id: Synapse Forum ID.
        """
        result = self.syn.restGET(f"/forum/{forum_id}")
        return _from_dict(Forum, result)

    # -- Thread ---------------------------------------------------------------

    def get_forum_threads(
        self, forum_id: str, limit: int = 20, offset: int = 0
    ) -> Iterator[Thread]:
        """
        Args:
            forum_id: Synapse Forum ID.
            limit: Page size (default 20).
            offset: Page offset (default 0).
        """
        url = (
            f"/forum/{forum_id}/threads?limit={limit}&offset={offset}&filter=NO_FILTER"
        )
        while url is not None:
            result = self.syn.restGET(url)
            for item in result.get("results", []):
                yield _from_dict(Thread, item)
            next_page_token = result.get("nextPageToken")
            url = (
                f"/forum/{forum_id}/threads?nextPageToken={next_page_token}"
                if next_page_token
                else None
            )

    def create_thread(self, forum_id: str, title: str, message: str) -> Thread:
        """
        Args:
            forum_id: Synapse Forum ID.
            title: Thread title.
            message: Thread body (markdown supported).
        """
        body = {"forumId": forum_id, "title": title, "messageMarkdown": message}
        result = self.syn.restPOST("/thread", json.dumps(body))
        return _from_dict(Thread, result)

    def update_thread_title(self, thread_id: str, title: str) -> Thread:
        """
        Args:
            thread_id: Synapse Thread ID.
            title: New title.
        """
        result = self.syn.restPUT(
            f"/thread/{thread_id}/title", json.dumps({"title": title})
        )
        return _from_dict(Thread, result)

    def update_thread_message(self, thread_id: str, message: str) -> Thread:
        """
        Args:
            thread_id: Synapse Thread ID.
            message: New body text (markdown supported).
        """
        result = self.syn.restPUT(
            f"/thread/{thread_id}/message",
            json.dumps({"messageMarkdown": message}),
        )
        return _from_dict(Thread, result)

    def delete_thread(self, thread_id: str) -> None:
        """
        Args:
            thread_id: Synapse Thread ID.
        """
        self.syn.restDELETE(f"/thread/{thread_id}")

    def pin_thread(self, thread_id: str) -> None:
        """
        Args:
            thread_id: Synapse Thread ID.
        """
        self.syn.restPUT(f"/thread/{thread_id}/pin", None)

    def unpin_thread(self, thread_id: str) -> None:
        """
        Args:
            thread_id: Synapse Thread ID.
        """
        self.syn.restPUT(f"/thread/{thread_id}/unpin", None)

    # -- Reply ----------------------------------------------------------------

    def get_thread_replies(
        self, thread_id: str, limit: int = 20, offset: int = 0
    ) -> Iterator[Reply]:
        """
        Args:
            thread_id: Synapse Thread ID.
            limit: Page size (default 20).
            offset: Page offset (default 0).
        """
        url = f"/thread/{thread_id}/replies?limit={limit}&offset={offset}&filter=NO_FILTER"
        while url is not None:
            result = self.syn.restGET(url)
            for item in result.get("results", []):
                yield _from_dict(Reply, item)
            next_page_token = result.get("nextPageToken")
            url = (
                f"/thread/{thread_id}/replies?nextPageToken={next_page_token}"
                if next_page_token
                else None
            )

    def create_reply(self, thread_id: str, message: str) -> Reply:
        """
        Args:
            thread_id: Synapse Thread ID.
            message: Reply body (markdown supported).
        """
        body = {"threadId": thread_id, "messageMarkdown": message}
        result = self.syn.restPOST("/reply", json.dumps(body))
        return _from_dict(Reply, result)

    def delete_reply(self, reply_id: str) -> None:
        """
        Args:
            reply_id: Synapse Reply ID.
        """
        self.syn.restDELETE(f"/reply/{reply_id}")

    # -- Message text ---------------------------------------------------------

    def get_thread_text(self, thread: Thread) -> str:
        """Fetch the raw markdown body of a thread message.

        Args:
            thread: Thread object (must have a ``messageKey`` attribute).

        Returns:
            Markdown string of the thread body.
        """
        url_response = self.syn.restGET(f"/thread/{thread.id}/messageUrl")
        with urllib.request.urlopen(url_response["messageUrl"]) as resp:
            return resp.read().decode()

    def get_reply_text(self, reply: Reply) -> str:
        """Fetch the raw markdown body of a reply message.

        Args:
            reply: Reply object.

        Returns:
            Markdown string of the reply body.
        """
        url_response = self.syn.restGET(f"/reply/{reply.id}/messageUrl")
        with urllib.request.urlopen(url_response["messageUrl"]) as resp:
            return resp.read().decode()


# ---------------------------------------------------------------------------
# Convenience free-functions
# ---------------------------------------------------------------------------


def get_forum_threads(project_id: str) -> Iterator[Thread]:
    """Yield all discussion threads in a Synapse project's forum.

    Args:
        project_id: Synapse ID of the project.
    """
    api = DiscussionApi()
    forum = api.get_project_forum(project_id)
    yield from api.get_forum_threads(forum.id)


def get_thread_replies(thread_id: str) -> Iterator[Reply]:
    """Yield all replies in a discussion thread.

    Args:
        thread_id: Synapse Thread ID.
    """
    api = DiscussionApi()
    yield from api.get_thread_replies(thread_id)


def get_forum_participants(project_id: str) -> set[str]:
    """Get the set of user IDs that have posted in a project's forum.

    Args:
        project_id: Synapse ID of the project.
    """
    api = DiscussionApi()
    forum = api.get_project_forum(project_id)
    participants: set[str] = set()
    for thread in api.get_forum_threads(forum.id):
        participants.add(thread.created_by)
        for reply in api.get_thread_replies(thread.id):
            participants.add(reply.created_by)
    return participants


def create_thread(project_id: str, title: str, message: str) -> Thread:
    """Create a new discussion thread in a project's forum.

    Args:
        project_id: Synapse ID of the project.
        title: Thread title.
        message: Thread body (markdown supported).
    """
    api = DiscussionApi()
    forum = api.get_project_forum(project_id)
    return api.create_thread(forum.id, title, message)


def copy_thread(
    thread: Thread,
    target_forum_id: str,
    *,
    api: DiscussionApi | None = None,
) -> Thread:
    """Copy a thread (and all its replies) to another forum.

    Args:
        thread: Source Thread to copy.
        target_forum_id: ID of the destination Forum.
        api: Shared DiscussionApi instance (created if not provided).
    """
    api = api or DiscussionApi()
    message = api.get_thread_text(thread)
    new_thread = api.create_thread(target_forum_id, thread.title, message)
    for reply in api.get_thread_replies(thread.id):
        copy_reply(reply, new_thread.id, api=api)
    return new_thread


def copy_reply(
    reply: Reply,
    target_thread_id: str,
    *,
    api: DiscussionApi | None = None,
) -> Reply:
    """Copy a reply to another thread.

    Args:
        reply: Source Reply to copy.
        target_thread_id: ID of the destination Thread.
        api: Shared DiscussionApi instance (created if not provided).
    """
    api = api or DiscussionApi()
    message = api.get_reply_text(reply)
    return api.create_reply(target_thread_id, message)


def copy_forum(source_project_id: str, target_project_id: str) -> None:
    """Copy all threads and replies from one project's forum to another.

    Args:
        source_project_id: Synapse ID of the source project.
        target_project_id: Synapse ID of the destination project.
    """
    api = DiscussionApi()
    source_forum = api.get_project_forum(source_project_id)
    target_forum = api.get_project_forum(target_project_id)
    for thread in api.get_forum_threads(source_forum.id):
        copy_thread(thread, target_forum.id, api=api)
