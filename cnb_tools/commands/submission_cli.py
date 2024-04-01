"""CLI command: submission

Manage submissions.

Example:
    $ cnb-tools submission --help
"""

from pathlib import Path

from enum import Enum
from typing_extensions import Annotated
import typer

from cnb_tools.classes.annotation import SubmissionAnnotation
from cnb_tools.classes.submission import Submission


class Status(str, Enum):
    received = "RECEIVED"
    validated = "VALIDATED"
    invalid = "INVALID"
    accepted = "ACCEPTED"
    closed = "CLOSED"


app = typer.Typer()


@app.command()
def info(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help=(
                "Also output submission annotations - this may result in "
                "longer runtimes (default: false)"),
        ),
    ] = False,
):
    """Get information about a submission"""
    submission = Submission(submission_id)
    submission.info(verbose)


@app.command()
def download(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    dest: Annotated[
        Path,
        typer.Option(
            "--dest",
            "-d",
            help="Filepath to download destination (if submission is a file)",
        ),
    ] = ".",
):
    """Get a submission (file/Docker image)"""
    submission = Submission(submission_id)
    submission.download(dest)


@app.command()
def annotate(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    annots_file: Annotated[
        Path,
        typer.Argument(
            help="Filepath to JSON file containing annotations", exists=True
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Output final submission annotations (default: false)",
        ),
    ] = False,
):
    """Annotate one or more submission(s) with a JSON file."""
    submission_annots = SubmissionAnnotation(submission_id)
    submission_annots.update_with_file(annots_file, verbose)


@app.command()
def change_status(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    new_status: Annotated[Status, typer.Argument()],
):
    """Update one or more submission statuses."""
    for submission_id in submission_ids:
        submission_annots = SubmissionAnnotation(submission_id)
        submission_annots.update_status(new_status)


@app.command()
def reset(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
):
    """Reset one or more submission to RECEIVED."""
    change_status(submission_ids=submission_ids, new_status="RECEIVED")


@app.command()
def delete(
    submission_ids: Annotated[
        list[int],
        typer.Argument(help="One or more submission ID(s)"),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt=(
                "❗Are you sure you want to delete the submission(s)?\n\n"
                "Once deleted, submission(s) CANNOT be recovered."
            ),
            help="Force [red]deletion[/red] without confirmation.",
        ),
    ] = False,
):
    """Delete one or more submissions."""
    print()
    if force:
        for submission_id in submission_ids:
            submission = Submission(submission_id)
            submission.delete()
    else:
        print("No deletion was done.")
