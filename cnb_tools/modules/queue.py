"""Module for managing the challenge submission evaluation queues.

This module provides utility functions that extend synapseclient for managing
evaluation queues in Synapse challenges.
"""

from synapseclient import Evaluation
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.base import get_synapse_client, UnknownSynapseID


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


def get_evaluation_name(evaluation_id: int) -> str:
    """Get the name of an evaluation queue.

    Args:
        evaluation_id: Evaluation queue ID

    Returns:
        Evaluation queue name
    """
    evaluation = get_evaluation(evaluation_id)
    return evaluation.name


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
