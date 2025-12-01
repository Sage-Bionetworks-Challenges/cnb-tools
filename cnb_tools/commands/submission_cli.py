"""CLI command: submission

Manage submissions.

Example:
    $ cnb-tools submission --help
"""

import sys
from pathlib import Path

from enum import Enum
from typing_extensions import Annotated
import typer

from cnb_tools.modules.base import UnknownSynapseID
from cnb_tools.modules import annotation, submission


class Status(str, Enum):
    received = "RECEIVED"
    validated = "VALIDATED"
    invalid = "INVALID"
    scored = "SCORED"
    accepted = "ACCEPTED"
    closed = "CLOSED"


app = typer.Typer()


@app.command()
def annotate(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    json_file: Annotated[
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
    annotation.update_annotations_from_file(submission_id, str(json_file), verbose)


@app.command()
def change_status(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    new_status: Annotated[Status, typer.Argument()],
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip_errors",
            help="Continue update even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Update one or more submission statuses."""
    for submission_id in submission_ids:
        try:
            annotation.update_submission_status(submission_id, new_status.value)
        except UnknownSynapseID as err:
            if skip_errors:
                print(f"Unknown submission ID: {submission_id} - skipping...")
                continue
            sys.exit(err)


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
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip_errors",
            help="Continue deletion even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Delete one or more submissions."""
    print()
    if force:
        for submission_id in submission_ids:
            try:
                submission.delete_submission(submission_id)
            except UnknownSynapseID as err:
                if skip_errors:
                    print(f"Unknown submission ID: {submission_id} - skipping...")
                    continue
                sys.exit(err)
    else:
        print("No deletion was done.")


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
    submission.download_submission(submission_id, str(dest))


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
                "longer runtimes (default: false)"
            ),
        ),
    ] = False,
):
    """Get information about a submission"""
    submission.print_submission_info(submission_id, verbose)


@app.command()
def reset(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip_errors",
            help="Continue update even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Reset one or more submission to RECEIVED."""
    change_status(
        submission_ids=submission_ids, new_status="RECEIVED", skip_errors=skip_errors
    )
