"""Module for managing the challenge submission evaluation queues.

This module provides utility functions that extend synapseclient for managing
evaluation queues in Synapse challenges.
"""

import datetime

from synapseclient import Evaluation
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID


def get_evaluation(evaluation_id: int) -> Evaluation:
    """Get an evaluation queue by ID.

    Args:
        evaluation_id: Evaluation queue ID

    Returns:
        Evaluation object

    Raises:
        UnknownSynapseID: If the evaluation ID is invalid
    """
    syn = get_synapse_client()
    try:
        return syn.getEvaluation(evaluation_id)
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def get_challenge_name_from_evaluation(evaluation_id: int) -> str:
    """Get the challenge name for an evaluation queue.

    Args:
        evaluation_id: Evaluation queue ID

    Returns:
        Challenge name
    """
    syn = get_synapse_client()
    evaluation = get_evaluation(evaluation_id)
    parent_id = evaluation.contentSource
    return syn.get(parent_id).name


def create_evaluation(name: str, description: str, project_id: str) -> Evaluation:
    """Create and store a new evaluation queue on a Synapse project.

    Args:
        name: Queue name.
        description: Queue description.
        project_id: Synapse ID of the parent project.

    Returns:
        The newly created Evaluation object.
    """
    syn = get_synapse_client()
    return syn.store(
        Evaluation(name=name, description=description, contentSource=project_id)
    )


# ---------------------------------------------------------------------------
# Submission quota management
# ---------------------------------------------------------------------------


def _datetime_to_epoch_ms(date_string: str) -> int:
    """Convert a local datetime string to a UTC millisecond epoch integer.

    Args:
        date_string: A date/time string parseable by
            ``datetime.datetime.fromisoformat`` (e.g. ``"2025-01-01 08:00:00"``).

    Returns:
        UTC millisecond epoch timestamp.
    """
    local_dt = datetime.datetime.fromisoformat(date_string)
    # Convert local → UTC by applying the local UTC offset.
    utc_dt = local_dt.astimezone(datetime.timezone.utc)
    return int(utc_dt.timestamp() * 1000)


def set_evaluation_quota(
    evaluation_id: int | str,
    *,
    first_round_start: str | None = None,
    round_duration_millis: int | None = None,
    number_of_rounds: int | None = None,
    submissions_per_round: int | None = None,
    total_submissions: int | None = None,
) -> Evaluation:
    """Set the submission quota on an evaluation queue.

    Only the parameters you provide are updated; existing quota fields not
    mentioned are left unchanged.

    Args:
        evaluation_id: Evaluation queue ID.
        first_round_start: ISO-8601 local datetime string for the first
            round start (e.g. ``"2025-01-01 00:00:00"``).
        round_duration_millis: Duration of each round in milliseconds.
        number_of_rounds: Total number of rounds.
        submissions_per_round: Max submissions per participant per round.
        total_submissions: Hard cap on total submissions per participant.

    Returns:
        The updated Evaluation object.
    """
    syn = get_synapse_client()
    evaluation = get_evaluation(int(evaluation_id))

    quota_dict: dict = {}
    if first_round_start is not None:
        quota_dict["firstRoundStart"] = _datetime_to_epoch_ms(first_round_start)
    if round_duration_millis is not None:
        quota_dict["roundDurationMillis"] = round_duration_millis
    if number_of_rounds is not None:
        quota_dict["numberOfRounds"] = number_of_rounds
    if submissions_per_round is not None:
        quota_dict["submissionLimit"] = submissions_per_round
    if total_submissions is not None:
        quota_dict["totalSubmissionLimit"] = total_submissions

    if not quota_dict:
        return evaluation  # nothing to do

    # Merge with any existing quota settings.
    existing_quota: dict = getattr(evaluation, "quota", None) or {}
    existing_quota.update(quota_dict)
    evaluation.quota = existing_quota

    return syn.store(evaluation)
