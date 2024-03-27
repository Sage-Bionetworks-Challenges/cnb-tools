"""CLI command: submission

Manage submissions.

Example:
    $ cnb-tools submission --help
"""

from pathlib import Path
from typing import List

from typing_extensions import Annotated
import typer

from cnb_tools.classes.submission import Submission

app = typer.Typer()


@app.command()
def info(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")]
):
    """Get information about a submission"""
    submission = Submission(submission_id)
    submission.view()


@app.command()
def download(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    dest: Annotated[
        Path,
        typer.Option(
            "--dir",
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
    submission_ids: Annotated[
        List[int],
        typer.Argument(help="One or more submission ID(s)"),
    ],
    annotations: Annotated[
        Path, typer.Argument(help="Filepath to JSON file", exists=True)
    ],
):
    """Annotate one or more submission(s) with a JSON file."""
    for submission in submission_ids:
        print(f"Annotating {submission} with {annotations}...")
        print("✅")


@app.command()
def change_status(
    submission_id: Annotated[List[int], typer.Argument(help="Submission ID")],
    new_status: Annotated[
        str, typer.Argument(help="One of [RECEIVED, VALIDATED, INVALID, ACCEPTED]")
    ],
):
    """Update a submission status."""
    print(f"Updating {submission_id} to status: {new_status}...")
    print("✅")


@app.command()
def reset(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
):
    """Reset a submission status."""
    print(f"Resetting {submission_id} to status RECEIVED...")
    print("✅")


@app.command()
def delete(
    submission_ids: Annotated[
        List[int],
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
