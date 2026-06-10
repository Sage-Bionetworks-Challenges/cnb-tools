"""Module for managing the challenge submission evaluation queues.

This module provides utility functions that extend synapseclient for managing
evaluation queues in Synapse challenges.
"""

import json

from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.models import Evaluation

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID


def get_evaluation(evaluation_id: int) -> Evaluation:
    """Get an evaluation queue by ID.

    Tip: Example Use Case
      Retrieve a queue to inspect its name, quota settings, or content
      source project before running a bulk status update.

    Args:
      evaluation_id: Evaluation queue ID.

    Returns:
      Synapse ``Evaluation`` object.

    Raises:
      UnknownSynapseID: If the evaluation ID is invalid.
    """
    get_synapse_client()  # ensure authentication
    try:
        return Evaluation(id=str(evaluation_id)).get()
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def get_evaluation_ids_by_project(project_id: str) -> list[str]:
    """Return the IDs of all evaluation queues linked to a Synapse project.

    Tip: Example Use Case
      List every queue associated with a challenge project before bulk-
      updating permissions or closing the challenge.

    Args:
      project_id: Synapse ID of the challenge project.

    Returns:
      List of evaluation queue ID strings.
    """
    get_synapse_client()  # ensure authentication
    evaluations = Evaluation.get_evaluations_by_project(project_id=project_id)
    return [ev.id for ev in evaluations if ev.id]


def get_challenge_name_from_evaluation(evaluation_id: int) -> str:
    """Get the challenge name for an evaluation queue.

    Tip: Example Use Case
      Resolve a queue ID to a human-readable challenge name when
      building submission summaries or leaderboards.

    Args:
      evaluation_id: Evaluation queue ID.

    Returns:
      Name of the parent Synapse project.
    """
    syn = get_synapse_client()
    evaluation = get_evaluation(evaluation_id)
    parent_id = evaluation.content_source
    return syn.get(parent_id).name


def create_evaluation(
    name: str,
    description: str,
    project_id: str,
    submission_instructions_message: str = "Please see the challenge wiki for submission instructions.",
    submission_receipt_message: str = "Your submission has been received and is queued for evaluation.",
) -> Evaluation:
    """Create and store a new evaluation queue on a Synapse project.

    Tip: Example Use Case
      Add a second task queue to an existing challenge project without
      going through the Synapse web interface.

    Args:
      name: Queue name.
      description: Queue description.
      project_id: Synapse ID of the parent project.
      submission_instructions_message: Instructions shown to submitters. Must be a non-empty string.
      submission_receipt_message: Message shown to submitters after submission. Must be a non-empty string.

    Returns:
      The newly created ``Evaluation`` object.
    """
    get_synapse_client()  # ensure authentication
    return Evaluation(
        name=name,
        description=description,
        content_source=project_id,
        submission_instructions_message=submission_instructions_message,  # TODO: this should be optional, remove once synapseclient supports that
        submission_receipt_message=submission_receipt_message,  # TODO: this should be optional, remove once synapseclient supports that
    ).store()


def create_evaluation_round(
    evaluation_id: int | str,
    round_start: str,
    round_end: str,
    *,
    daily_limit: int | None = None,
    weekly_limit: int | None = None,
    monthly_limit: int | None = None,
    total_limit: int | None = None,
) -> dict:
    """Create an EvaluationRound for an evaluation queue.

    Uses the modern ``POST /evaluation/{evalId}/round`` API. Each round
    defines a time window and optional per-period submission limits.
    Multiple rounds can be created for the same queue.

    Tip: Example Use Case
      Limit participants to 3 submissions per day and 10 total during
      the active phase of a challenge.

    Args:
      evaluation_id: Evaluation queue ID.
      round_start: ISO-8601 datetime string for when the round opens
        (e.g. ``"2025-01-01T00:00:00.000Z"``).
      round_end: ISO-8601 datetime string for when the round closes
        (e.g. ``"2025-06-01T00:00:00.000Z"``).
      daily_limit: Max submissions per participant per day. Resets daily
        at 00:00:00 UTC.
      weekly_limit: Max submissions per participant per calendar week.
        Resets every Monday at 00:00:00 UTC.
      monthly_limit: Max submissions per participant per calendar month.
        Resets on the 1st of each month at 00:00:00 UTC.
      total_limit: Hard cap on total submissions per participant for the
        entire round duration.

    Returns:
      The newly created EvaluationRound dict.
    """
    syn = get_synapse_client()
    limits = []
    if daily_limit is not None:
        limits.append({"limitType": "DAILY", "maximumSubmissions": daily_limit})
    if weekly_limit is not None:
        limits.append({"limitType": "WEEKLY", "maximumSubmissions": weekly_limit})
    if monthly_limit is not None:
        limits.append({"limitType": "MONTHLY", "maximumSubmissions": monthly_limit})
    if total_limit is not None:
        limits.append({"limitType": "TOTAL", "maximumSubmissions": total_limit})

    body: dict = {
        "evaluationId": str(evaluation_id),
        "roundStart": round_start,
        "roundEnd": round_end,
    }
    if limits:
        body["limits"] = limits

    return syn.restPOST(f"/evaluation/{evaluation_id}/round", json.dumps(body))
