"""Module for managing Synapse Discussion forums, threads, and replies.

Thin wrappers over the Synapse Discussion REST API. All functions return raw
dicts so callers are not coupled to any local dataclass — when synapseclient
ships native Discussion support these can be replaced one-for-one.
"""

import json
import urllib.request
from typing import Iterator

from cnb_tools.modules.client import get_synapse_client


def _get_forum_id(project_id: str) -> str:
    """Return the forum ID for a Synapse project."""
    syn = get_synapse_client()
    return syn.restGET(f"/project/{project_id}/forum")["id"]


def _paginate(syn, url: str) -> Iterator[dict]:
    """Yield all results from a paginated Synapse REST endpoint."""
    while url is not None:
        result = syn.restGET(url)
        yield from result.get("results", [])
        token = result.get("nextPageToken")
        url = url.split("?")[0] + f"?nextPageToken={token}" if token else None


def get_forum_threads(project_id: str) -> Iterator[dict]:
    """Yield all discussion threads in a Synapse project's forum.

    Tip: Example Use Case
      Iterate over all threads to build a summary of questions asked
      by participants during the challenge.

    Args:
      project_id: Synapse ID of the project.

    Yields:
      Thread dicts with keys ``id``, ``forumId``, ``title``, ``createdBy``,
      ``createdOn``, etc.
    """
    syn = get_synapse_client()
    forum_id = _get_forum_id(project_id)
    url = f"/forum/{forum_id}/threads?limit=20&offset=0&filter=NO_FILTER"
    yield from _paginate(syn, url)


def get_forum_participants(project_id: str) -> set[str]:
    """Get the set of user IDs that have posted in a project's forum.

    Tip: Example Use Case
      Identify which participants were actively engaged in the forum
      to include them in challenge acknowledgements.

    Args:
      project_id: Synapse ID of the project.

    Returns:
      Set of Synapse user IDs (as strings) for all thread and reply authors.
    """
    syn = get_synapse_client()
    forum_id = _get_forum_id(project_id)
    participants: set[str] = set()
    thread_url = f"/forum/{forum_id}/threads?limit=20&offset=0&filter=NO_FILTER"
    for thread in _paginate(syn, thread_url):
        participants.add(thread["createdBy"])
        reply_url = f"/thread/{thread['id']}/replies?limit=20&offset=0&filter=NO_FILTER"
        for reply in _paginate(syn, reply_url):
            participants.add(reply["createdBy"])
    return participants


def create_thread(project_id: str, title: str, message: str) -> dict:
    """Create a new discussion thread in a project's forum.

    Tip: Example Use Case
      Post a challenge announcement or a data update notice directly
      from a script without opening the Synapse web interface.

    Args:
      project_id: Synapse ID of the project.
      title: Thread title.
      message: Thread body (markdown supported).

    Returns:
      The newly created Thread dict.
    """
    syn = get_synapse_client()
    forum_id = _get_forum_id(project_id)
    body = {"forumId": forum_id, "title": title, "messageMarkdown": message}
    return syn.restPOST("/thread", json.dumps(body))


def _get_message_text(url: str) -> str:
    """Fetch message body from a Synapse pre-signed URL response."""
    syn = get_synapse_client()
    url_response = syn.restGET(url)
    with urllib.request.urlopen(url_response["messageUrl"]) as resp:
        return resp.read().decode()


def copy_thread(thread: dict, target_forum_id: str) -> dict:
    """Copy a thread and all its replies to another forum.

    Tip: Example Use Case
      Migrate Q&A threads from a previous challenge's forum to a new
      challenge project to preserve historical context.

    Args:
      thread: Source thread dict (must have ``id`` and ``title``).
      target_forum_id: ID of the destination forum.

    Returns:
      The newly created thread dict in the destination forum.
    """
    syn = get_synapse_client()
    message = _get_message_text(f"/thread/{thread['id']}/messageUrl")
    body = {
        "forumId": target_forum_id,
        "title": thread["title"],
        "messageMarkdown": message,
    }
    new_thread = syn.restPOST("/thread", json.dumps(body))
    reply_url = f"/thread/{thread['id']}/replies?limit=20&offset=0&filter=NO_FILTER"
    for reply in _paginate(syn, reply_url):
        reply_text = _get_message_text(f"/reply/{reply['id']}/messageUrl")
        syn.restPOST(
            "/reply",
            json.dumps({"threadId": new_thread["id"], "messageMarkdown": reply_text}),
        )
    return new_thread


def copy_forum(source_project_id: str, target_project_id: str) -> None:
    """Copy all threads and replies from one project's forum to another.

    Tip: Example Use Case
      Duplicate the entire Q&A forum from a completed challenge into a
      new challenge project as a starting point for participants.

    Args:
      source_project_id: Synapse ID of the source project.
      target_project_id: Synapse ID of the destination project.
    """
    syn = get_synapse_client()
    source_forum_id = _get_forum_id(source_project_id)
    target_forum_id = _get_forum_id(target_project_id)
    thread_url = f"/forum/{source_forum_id}/threads?limit=20&offset=0&filter=NO_FILTER"
    for thread in _paginate(syn, thread_url):
        copy_thread(thread, target_forum_id)
