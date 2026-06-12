"""Module for managing the annotations of challenge submissions.

This module provides utility functions that extend synapseclient for managing
submission annotations in Synapse challenges.
"""

import json

# TODO: Revert to OOP approach once synapseclient bug is fixed.
# See: https://github.com/Sage-Bionetworks-Challenges/cnb-tools/issues/43
# from synapseclient.models import SubmissionStatus

from synapseclient import SubmissionStatus
from synapseclient.annotations import to_submission_status_annotations
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.core.retry import with_retry

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID


def get_submission_status(submission_id: int) -> SubmissionStatus:
    """Get the submission status object containing annotations.

    Tip: Example Use Case
      Read the current annotations on a submission before deciding
      whether to update or overwrite them.

    Args:
      submission_id: ID of the submission.

    Returns:
      ``SubmissionStatus`` object with current annotations.

    Raises:
      UnknownSynapseID: If the submission ID is invalid.
    """
    # TODO: Revert to OOP approach once synapseclient bug is fixed.
    # get_synapse_client()  # ensure authentication
    # return SubmissionStatus(id=str(submission_id)).get()
    syn = get_synapse_client()
    try:
        return syn.getSubmissionStatus(submission_id)
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def format_annotations(submission_status: SubmissionStatus) -> str:
    """Format submission annotations as a human-readable string.

    Tip: Example Use Case
      Display the current status and all annotation key-value pairs
      of a submission for quick review in the terminal.

    Args:
      submission_status: ``SubmissionStatus`` object.

    Returns:
      Formatted string with the status and annotations as indented JSON.
    """
    output = f"     Status: {submission_status.status}\n"
    output += "Annotations:\n"
    # TODO: Revert to OOP approach once synapseclient bug is fixed.
    # output += json.dumps(submission_status.submission_annotations, indent=2)
    output += json.dumps(submission_status.submissionAnnotations, indent=2)
    return output


def update_annotations(
    submission_id: int,
    new_annotations: dict[str, str | int | float | bool],
    verbose: bool = False,
) -> SubmissionStatus:
    """Update submission annotations.

    Tip: Example Use Case
      After scoring a submission, write the scores back to the
      submission so they appear in the challenge leaderboard.

    Args:
      submission_id: ID of the submission.
      new_annotations: Dictionary of annotations to add or update.
      verbose: If True, print the updated annotations after storing.

    Returns:
      Updated ``SubmissionStatus`` object.
    """
    # TODO: Revert to OOP approach once synapseclient bug is fixed.
    # status = get_submission_status(submission_id)
    # status.submission_annotations = {
    #     **(status.submission_annotations or {}),
    #     **new_annotations,
    # }
    # status = status.store()
    syn = get_synapse_client()
    status = get_submission_status(submission_id)
    status.submissionAnnotations.update(new_annotations)
    status = syn.store(status)

    print(f"Submission ID {submission_id} annotations updated.")

    if verbose:
        print("Annotations:")
        # TODO: Revert to OOP approach once synapseclient bug is fixed.
        # print(json.dumps(status.submission_annotations, indent=2))
        print(json.dumps(status.submissionAnnotations, indent=2))

    return status


def _submission_annotations_to_dict(annotations: dict, is_private: bool = True) -> dict:
    """Convert legacy submission status annotations to a flat dictionary."""
    return {
        annot["key"]: annot["value"]
        for annotation_type in annotations
        for annot in annotations[annotation_type]
        if annotation_type not in ["scopeId", "objectId"]
        and annot["isPrivate"] == is_private
    }


def update_legacy_annotations(
    submission_id: int,
    new_annotations: dict[str, str | int | float | bool],
    is_private: bool = True,
    verbose: bool = False,
) -> SubmissionStatus:
    """Update submission annotations using the legacy structured format.

    Note: Backwards Compatibility
      This function is intended for challenges that use older leaderboard
      widgets requiring the legacy ``stringAnnos`` / ``longAnnos`` /
      ``doubleAnnos`` annotation format. Prefer :func:`update_annotations`
      for new challenges.

    Args:
      submission_id: ID of the submission.
      new_annotations: Dictionary of annotations to add or update.
      is_private: If True (default), annotations are stored as private and
        will not be visible on public leaderboards.
      verbose: If True, print the updated annotations after storing.

    Returns:
      Updated ``SubmissionStatus`` object.
    """
    syn = get_synapse_client()
    status = get_submission_status(submission_id)

    existing_annots = status.get("annotations", {})
    private_annotations = _submission_annotations_to_dict(
        existing_annots, is_private=True
    )
    public_annotations = _submission_annotations_to_dict(
        existing_annots, is_private=False
    )

    if is_private:
        private_annotations.update(new_annotations)
    else:
        public_annotations.update(new_annotations)

    priv = to_submission_status_annotations(private_annotations, is_private=True)
    pub = to_submission_status_annotations(public_annotations, is_private=False)

    combined = {"stringAnnos": [], "longAnnos": [], "doubleAnnos": []}
    for annot_type in ["stringAnnos", "longAnnos", "doubleAnnos"]:
        priv_list = priv.get(annot_type)
        pub_list = pub.get(annot_type)
        if priv_list:
            combined[annot_type].extend(priv_list)
        if pub_list:
            combined[annot_type].extend(pub_list)
        if not priv_list and not pub_list:
            combined.pop(annot_type)

    status["annotations"] = combined
    status = syn.store(status)

    print(f"Submission ID {submission_id} annotations updated.")

    if verbose:
        print("Annotations:")
        print(json.dumps(status.get("annotations"), indent=2))

    return status


def update_annotations_from_file(
    submission_id: int, annots_file: str, verbose: bool = False
) -> SubmissionStatus:
    """Update submission annotations from a JSON file.

    Tip: Example Use Case
      After a scoring script writes results to ``scores.json``, pass
      the file directly to attach all scores to the submission at once.

    Args:
      submission_id: ID of the submission.
      annots_file: Path to a JSON file containing annotation key-value pairs.
      verbose: If True, print the updated annotations after storing.

    Returns:
      Updated ``SubmissionStatus`` object.
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


def update_legacy_annotations_from_file(
    submission_id: int,
    annots_file: str,
    is_private: bool = True,
    verbose: bool = False,
) -> SubmissionStatus:
    """Update legacy submission annotations from a JSON file.

    Note: Backwards Compatibility
      Use this for challenges that require the legacy ``stringAnnos`` /
      ``longAnnos`` / ``doubleAnnos`` annotation format. Prefer
      :func:`update_annotations_from_file` for new challenges.

    Args:
      submission_id: ID of the submission.
      annots_file: Path to a JSON file containing annotation key-value pairs.
      is_private: If True (default), annotations are stored as private.
      verbose: If True, print the updated annotations after storing.

    Returns:
      Updated ``SubmissionStatus`` object.
    """
    with open(annots_file, encoding="utf-8") as f:
        new_annotations = json.load(f)

    # Filter annotations with null and empty-list values
    new_annotations = {
        key: value for key, value in new_annotations.items() if value not in [None, []]
    }

    return with_retry(
        lambda: update_legacy_annotations(
            submission_id, new_annotations, is_private, verbose
        ),
        wait=3,
        retries=10,
        retry_status_codes=[412, 429, 500, 502, 503, 504],
        verbose=True,
    )


def update_submission_status(submission_id: int, new_status: str) -> SubmissionStatus:
    """Update the status of a submission.

    Tip: Example Use Case
      Mark a submission as ``ACCEPTED`` after it passes validation,
      or ``INVALID`` if it fails a required check.

    Args:
      submission_id: ID of the submission.
      new_status: New status value (e.g. ``"ACCEPTED"``, ``"INVALID"``,
        ``"SCORED"``).

    Returns:
      Updated ``SubmissionStatus`` object.
    """
    # TODO: Revert to OOP approach once synapseclient bug is fixed.
    # status = get_submission_status(submission_id)
    # status.status = new_status
    # status = status.store()
    syn = get_synapse_client()
    status = get_submission_status(submission_id)
    status.status = new_status
    status = syn.store(status)

    print(f"Updated submission ID {submission_id} to status: {new_status}")

    return status
