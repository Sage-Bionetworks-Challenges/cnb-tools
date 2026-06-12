"""Module for managing challenge submissions.

This module provides utility functions that extend synapseclient for managing
submissions in Synapse challenges.
"""

from pathlib import Path

from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.models import Evaluation, Submission, SubmissionBundle

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID
from cnb_tools.modules import annotation


def get_submission(submission_id: int) -> Submission:
    """Get a submission by ID.

    Tip: Example Use Case
      Fetch a submission object to read its metadata (team, evaluation,
      entity ID) before deciding whether to score or reject it.

    Args:
      submission_id: ID of the submission.

    Returns:
      Synapse ``Submission`` object.

    Raises:
      UnknownSynapseID: If the submission ID is invalid.
    """
    get_synapse_client()  # ensure authentication
    try:
        return Submission(id=str(submission_id)).get()
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def delete_submission(submission_id: int) -> None:
    """Delete a submission.

    Tip: Example Use Case
      Remove a test submission made during challenge development before
      opening the queue to participants.

    Args:
      submission_id: ID of the submission to delete.
    """
    get_synapse_client()  # ensure authentication
    Submission(id=str(submission_id)).delete()
    print(f"Submission deleted: {submission_id}")


def download_submission(submission_id: int, dest: str = ".") -> None:
    """Download a submission file or display a Docker pull command.

    Tip: Example Use Case
      Pull a participant's Docker image locally to run it manually
      during debugging or manual review.

    Args:
      submission_id: ID of the submission.
      dest: Destination directory for downloaded files (default: current
        directory). Ignored for Docker submissions.
    """
    syn = get_synapse_client()
    submission = get_submission(submission_id)

    if submission.docker_digest is not None:
        print(
            f"Submission ID {submission_id} is a Docker image \U0001f433 To "
            "'download', run the following:\n\n"
            f"docker pull {submission.docker_repository_name}"
            f"@{submission.docker_digest}\n\n"
            "If you receive an error, try logging in first with: "
            "docker login docker.synapse.org"
        )
    else:
        syn.getSubmission(submission_id, downloadLocation=dest)
        location = Path.cwd() if str(dest) == "." else dest
        print(f"Submission ID {submission_id} downloaded to: {location}")


def get_submitter_name(submitter_id: int) -> str:
    """Get the display name of a submitter (team or individual user).

    Tip: Example Use Case
      Resolve a raw team or user ID to a human-readable name when
      building a leaderboard or notification email.

    Args:
      submitter_id: Synapse Team ID or User ID.

    Returns:
      Team name or username.
    """
    syn = get_synapse_client()
    try:
        return syn.getTeam(submitter_id).get("name")
    except SynapseHTTPError:
        return syn.getUserProfile(submitter_id).get("userName")


def get_challenge_name(evaluation_id: int) -> str:
    """Get the challenge name for an evaluation queue.

    Tip: Example Use Case
      Display a friendly challenge name alongside submission metadata
      instead of a raw evaluation ID.

    Args:
      evaluation_id: Evaluation queue ID.

    Returns:
      Name of the parent Synapse project.

    Raises:
      UnknownSynapseID: If the evaluation ID is invalid.
    """
    syn = get_synapse_client()
    try:
        evaluation = Evaluation(id=str(evaluation_id)).get()
        parent_id = evaluation.content_source
        return syn.get(parent_id).name
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. " "Check the ID and try again."
        ) from err


def print_submission_info(
    submission_id: int,
    verbose: bool = False,
) -> None:
    """Print information about a submission.

    Args:
        submission_id: ID of the submission
        verbose: If True, also print submission annotations
    """
    sub = get_submission(submission_id)
    submitter_id = sub.team_id or sub.user_id

    challenge_display = get_challenge_name(sub.evaluation_id)
    submitter_display = get_submitter_name(submitter_id)

    print(f"ID:        {submission_id}")
    print(f"Challenge: {challenge_display}")
    print(f"Date:      {sub.created_on[:10]}")
    print(f"Submitter: {submitter_display}")

    if verbose:
        status = annotation.get_submission_status(submission_id)
        print(annotation.format_annotations(status))


def get_submission_contributors(submission_id: int) -> list[dict[str, object]]:
    """Get the contributors for a single submission from its metadata.

    Tip: Example Use Case
      Quickly list everyone credited on a specific submission without
      scanning an entire evaluation queue.

    Args:
      submission_id: ID of the submission.

    Returns:
      List of contributor records from the submission metadata (each record
      includes at least ``principalId`` and ``createdOn``).

    Raises:
      UnknownSynapseID: If the submission ID is invalid.
    """
    sub = get_submission(submission_id)
    return list(sub.contributors) if sub.contributors else []


def get_contributors(
    evaluation_ids: list[int | str],
    status: str = "SCORED",
) -> set[str]:
    """Get the set of contributor principal IDs from evaluation queues.

    Scans all submissions with the given *status* across each queue and
    returns every ``principalId`` listed in ``submission.contributors``.

    Tip: Example Use Case
      Collect all contributors from the scored submissions to send
      certificates or acknowledgement emails after the challenge ends.

    Args:
      evaluation_ids: One or more evaluation queue IDs.
      status: Only consider submissions in this status. Default ``"SCORED"``.

    Returns:
      Set of Synapse principal IDs (strings) for all matching contributors.
    """
    get_synapse_client()  # ensure authentication
    all_contributors: set[str] = set()
    for evaluation_id in evaluation_ids:
        for bundle in SubmissionBundle.get_evaluation_submission_bundles(
            evaluation_id=str(evaluation_id), status=status
        ):
            if bundle.submission and bundle.submission.contributors:
                all_contributors.update(bundle.submission.contributors)
    return all_contributors


def batch_download_submissions(
    evaluation_id: int,
    dest: str = ".",
    status: str | None = None,
) -> None:
    """Download all submission files from an evaluation queue.

    Files are organized into subdirectories named after each submitter.
    Each file is renamed to ``<submission_id><original_extension>`` so
    organizers can trace a file back to its submission. Docker submissions
    are skipped with an informational message.

    Tip: Example Use Case
      Download every prediction file submitted to a challenge queue at
      the end of the challenge for offline analysis or archival.

    Args:
      evaluation_id: Evaluation queue ID.
      dest: Root destination directory (default: current directory).
        Subdirectories per submitter are created automatically.
      status: Only download submissions in this status (e.g.
        ``"SCORED"``, ``"ACCEPTED"``). If ``None``, all submissions are
        downloaded regardless of status.
    """
    syn = get_synapse_client()
    base = Path(dest)
    count = 0

    for sub in syn.getSubmissions(evaluation_id, status=status):
        submission_id = sub["id"]
        submitter_id = sub.get("teamId") or sub.get("userId")
        submitter_name = get_submitter_name(int(submitter_id)).replace(" ", "_")

        download_dir = base / submitter_name
        download_dir.mkdir(parents=True, exist_ok=True)

        if sub.get("dockerDigest"):
            print(
                f"Skipping submission {submission_id} "
                f"(Docker image — use `cnb-tools submission download` to get pull command)"
            )
            continue

        downloaded = syn.getSubmission(
            submission_id, downloadLocation=str(download_dir)
        )
        original = Path(downloaded.filePath)
        renamed = download_dir / f"{submission_id}{original.suffix}"
        original.rename(renamed)
        print(f"Downloaded submission {submission_id} → {renamed}")
        count += 1

    print(f"\nDone. {count} file(s) downloaded to: {Path(dest).resolve()}")
