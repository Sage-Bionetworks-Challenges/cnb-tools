from pathlib import Path
from typing import List

from typing_extensions import Annotated
import typer

app = typer.Typer()


@app.command()
def info(
    submission_id: Annotated[int, typer.Argument(help="Submission ID to get info")]
):
    """Get information about a submission"""
    print(f"ID: {submission_id}")
    print("Challenge: Awesome Challenge")
    print("Date: 2024-01-01")
    print("Submitter: awesome-user")
    print("Team (if any): Awesome Team")
    print("Status: SCORED")


@app.command()
def pull(
    submission_id: Annotated[int, typer.Argument(help="Submission ID to download")],
    dest: Annotated[
        Path,
        typer.Option(
            "--dir",
            "-d",
            help="Directory to download submission into (if submission is a file)",
        ),
    ] = ".",
):
    """Get a submission (file/Docker image)"""
    submission_type = "file"
    if submission_type == "file":
        print(f"Downloading {submission_id} to {dest}...")
    else:
        print("Pulling Docker image...")
    print("✅")


@app.command()
def annotate(
    submission_ids: Annotated[
        List[int],
        typer.Argument(help="One or more submission ID(s) to annotate"),
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
    submission_id: Annotated[List[int], typer.Argument(help="Submission ID to update")],
    new_status: Annotated[
        str, typer.Argument(help="One of [RECEIVED, VALIDATED, INVALID, ACCEPTED]")
    ],
):
    """Update a submission status."""
    print(f"Updating {submission_id} to status: {new_status}...")
    print("✅")


@app.command()
def reset(
    submission_id: Annotated[int, typer.Argument(help="Submission ID to reset")],
):
    """Reset a submission status."""
    print(f"Resetting {submission_id} to status RECEIVED...")
    print("✅")


@app.command()
def delete(
    submission_ids: Annotated[
        List[int],
        typer.Argument(help="One or more submission ID(s) to [red]delete[/red]"),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="Are you sure you want to delete the submission(s)?",
            help="Force [red]deletion[/red] without confirmation.",
        ),
    ] = False,
):
    """Delete one or more submissions."""
    if force:
        for submission in submission_ids:
            print(f"Deleting submissions: {submission}")
        print("✅")
    else:
        print("No deletion was done.")
