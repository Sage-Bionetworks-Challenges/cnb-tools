"""Module for managing the annotations of challenge submissions.

This module provides utility functions that extend synapseclient for managing
submission annotations in Synapse challenges.
"""

import json

from synapseclient import SubmissionStatus
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.core.retry import with_retry

from cnb_tools.modules.base import get_synapse_client, UnknownSynapseID


def get_submission_status(submission_id: int) -> SubmissionStatus:
    """Get the submission status object containing annotations.

    Args:
        submission_id: ID of the submission

    Returns:
        SubmissionStatus object with current annotations

    Raises:
        UnknownSynapseID: If the submission ID is invalid
    """
    syn = get_synapse_client()
    try:
        return syn.getSubmissionStatus(submission_id)
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def format_annotations(submission_status: SubmissionStatus) -> str:
    """Format submission annotations for display.

    Args:
        submission_status: SubmissionStatus object

    Returns:
        Formatted string representation of status and annotations
    """
    output = f"     Status: {submission_status.status}\n"
    output += "Annotations:\n"
    output += json.dumps(submission_status.submissionAnnotations, indent=2)
    return output


def update_annotations(
    submission_id: int,
    new_annotations: dict[str, str | int | float | bool],
    verbose: bool = False,
) -> SubmissionStatus:
    """Update submission annotations.

    Args:
        submission_id: ID of the submission
        new_annotations: Dictionary of annotations to add/update
        verbose: If True, print updated annotations

    Returns:
        Updated SubmissionStatus object
    """
    syn = get_synapse_client()
    status = get_submission_status(submission_id)
    status.submissionAnnotations.update(new_annotations)
    status = syn.store(status)

    print(f"Submission ID {submission_id} annotations updated.")

    if verbose:
        print("Annotations:")
        print(json.dumps(status.submissionAnnotations, indent=2))

    return status


def update_annotations_from_file(
    submission_id: int, annots_file: str, verbose: bool = False
) -> SubmissionStatus:
    """Update submission annotations from a JSON file.

    Args:
        submission_id: ID of the submission
        annots_file: Path to JSON file containing annotations
        verbose: If True, print updated annotations

    Returns:
        Updated SubmissionStatus object
    """
    with open(annots_file, encoding="utf-8") as f:
        new_annotations = json.load(f)

    # Filter annotations with null and empty-list values
    new_annotations = {
        key: value for key, value in new_annotations.items() if value not in [None, []]
    }

    return with_retry(
        lambda: update_annotations(submission_id, new_annotations, verbose),
        wait=3,
        retries=10,
        retry_status_codes=[412, 429, 500, 502, 503, 504],
        verbose=True,
    )


def update_submission_status(submission_id: int, new_status: str) -> SubmissionStatus:
    """Update submission status.

    Args:
        submission_id: ID of the submission
        new_status: New status value (e.g., 'ACCEPTED', 'REJECTED', 'SCORED')

    Returns:
        Updated SubmissionStatus object
    """
    syn = get_synapse_client()
    status = get_submission_status(submission_id)
    status.status = new_status
    status = syn.store(status)

    print(f"Updated submission ID {submission_id} to status: {new_status}")

    return status
