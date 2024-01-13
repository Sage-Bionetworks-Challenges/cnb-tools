from typing import Optional
from typing_extensions import Annotated
import typer

app = typer.Typer()


@app.command()
def info(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [blue]get info[/blue]")
    ]
):
    """[bold blue]Get[/bold blue] information about a submission"""
    print(f"ID: {submission_id}")
    print("Challenge: Awesome Challenge")
    print("Date: 2024-01-01")
    print("Submitter: awesome-user")
    print("Team (if any): Awesome Team")
    print("Status: SCORED")


@app.command()
def download(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [blue]download[/blue]")
    ],
    dest: Annotated[
        str,
        typer.Option(..., "-D", "--dir", help="Directory to download submission into"),
    ] = ".",
):
    """[bold blue]Download[/bold blue] a submission"""
    print(f"Downloading {submission_id} to {dest}...")
    print("✅")


@app.command()
def annotate(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [orange1]annotate[/orange1]")
    ],
    annotations: Annotated[str, typer.Argument(help="Filepath to JSON file")],
):
    """[bold orange1]Annotate[/bold orange1] a submission."""
    print(f"Annotating {submission_id}...")
    print("✅")


@app.command()
def update_status(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [orange1]update[/orange1]")
    ],
    new_status: Annotated[
        str, typer.Argument(help="One of [RECEIVED, VALIDATED, INVALID, ACCEPTED]")
    ] = "ACCEPTED",
):
    """[bold orange1]Update[/bold orange1] a submission status."""
    print(f"Updating {submission_id} to status: {new_status}...")
    print("✅")


@app.command()
def reset(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [orange1]reset[/orange1]")
    ],
):
    """[bold orange1]Reset[/bold orange1] a submission status."""
    print(f"Resetting {submission_id} to status RECEIVED...")
    print("✅")


@app.command()
def delete(
    submission_id: Annotated[
        int, typer.Argument(help="Submission ID to [red]delete[/red]")
    ],
    force: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to delete the submission(s)?",
            help="Force [red]deletion[/red] without confirmation.",
        ),
    ],
):
    """[bold red]Delete[/bold red] one or more submissions."""
    if force:
        print(f"Deleting submissions: {submission_id}")
        print("✅")
    else:
        print("Nothing was done.")
