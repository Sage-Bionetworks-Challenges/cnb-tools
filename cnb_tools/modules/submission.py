"""Module for managing challenge submissions.

This module provides utility functions that extend synapseclient for managing
submissions in Synapse challenges.
"""

from pathlib import Path
from synapseclient import Submission as SynapseSubmission
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.base import get_synapse_client, UnknownSynapseID
from cnb_tools.modules import annotation


def get_submission(submission_id: int, download_file: bool = False) -> SynapseSubmission:
    """Get a submission by ID.
    
    Args:
        submission_id: ID of the submission
        download_file: If True, download the submission file
        
    Returns:
        Synapse Submission object
        
    Raises:
        UnknownSynapseID: If the submission ID is invalid
    """
    syn = get_synapse_client()
    try:
        return syn.getSubmission(submission_id, downloadFile=download_file)
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. "
            "Check the ID and try again."
        ) from err


def delete_submission(submission_id: int) -> None:
    """Delete a submission.
    
    Args:
        submission_id: ID of the submission to delete
    """
    syn = get_synapse_client()
    submission = get_submission(submission_id)
    syn.delete(submission)
    print(f"Submission deleted: {submission_id}")


def download_submission(submission_id: int, dest: str = ".") -> None:
    """Download a submission file or display Docker pull command.
    
    Args:
        submission_id: ID of the submission
        dest: Destination directory for download (default: current directory)
    """
    syn = get_synapse_client()
    submission = get_submission(submission_id)
    
    if "dockerDigest" in submission:
        print(
            f"Submission ID {submission_id} is a Docker image 🐳 To "
            "'download', run the following:\n\n"
            f"docker pull {submission.dockerRepositoryName}"
            f"@{submission.dockerDigest}\n\n"
            "If you receive an error, try logging in first with: "
            "docker login docker.synapse.org"
        )
    else:
        syn.getSubmission(submission_id, downloadLocation=dest)
        location = Path.cwd() if str(dest) == "." else dest
        print(f"Submission ID {submission_id} downloaded to: {location}")


def get_submitter_name(submitter_id: int) -> str:
    """Get the name of a submitter (team or user).
    
    Args:
        submitter_id: Team ID or User ID
        
    Returns:
        Team name or username
    """
    syn = get_synapse_client()
    try:
        return syn.getTeam(submitter_id).get("name")
    except SynapseHTTPError:
        return syn.getUserProfile(submitter_id).get("userName")


def get_challenge_name(evaluation_id: int) -> str:
    """Get the challenge name for an evaluation queue.
    
    Args:
        evaluation_id: Evaluation queue ID
        
    Returns:
        Challenge name
    """
    syn = get_synapse_client()
    try:
        evaluation = syn.getEvaluation(evaluation_id)
        parent_id = evaluation.contentSource
        return syn.get(parent_id).name
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. "
            "Check the ID and try again."
        ) from err


def print_submission_info(submission_id: int, verbose: bool = False) -> None:
    """Print information about a submission.
    
    Args:
        submission_id: ID of the submission
        verbose: If True, also print submission annotations
    """
    submission = get_submission(submission_id)
    challenge = get_challenge_name(submission.evaluationId)
    submitter_id = submission.get("teamId") or submission.get("userId")
    submitter = get_submitter_name(submitter_id)
    
    print(f"         ID: {submission_id}")
    print(f"  Challenge: {challenge}")
    print(f"       Date: {submission.createdOn[:10]}")
    print(f"  Submitter: {submitter}")
    
    if verbose:
        status = annotation.get_submission_status(submission_id)
        print(annotation.format_annotations(status))
