"""CLI command: queue

Manage Synapse evaluation queues.

Example:
    $ cnb-tools queue --help
"""

import sys
from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools.modules import queue, utils
from cnb_tools.modules.client import UnknownSynapseID

app = typer.Typer()


@app.command()
def get(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
):
    """Get details about an evaluation queue."""
    try:
        ev = queue.get_evaluation(evaluation_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    typer.echo(f"ID:          {ev.id}")
    typer.echo(f"Name:        {ev.name}")
    typer.echo(f"Description: {ev.description or '—'}")
    typer.echo(f"Project:     {ev.contentSource}")
    if ev.quota:
        typer.echo(f"Quota:       {ev.quota}")


@app.command()
def set_quota(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    first_round_start: Annotated[
        Optional[str],
        typer.Option(
            "--start",
            help='Local datetime for the first round start, e.g. "2025-01-01 00:00:00"',
        ),
    ] = None,
    round_duration_millis: Annotated[
        Optional[int],
        typer.Option("--round-duration", help="Duration of each round in milliseconds"),
    ] = None,
    number_of_rounds: Annotated[
        Optional[int],
        typer.Option("--rounds", help="Total number of rounds"),
    ] = None,
    submissions_per_round: Annotated[
        Optional[int],
        typer.Option("--per-round", help="Max submissions per participant per round"),
    ] = None,
    total_submissions: Annotated[
        Optional[int],
        typer.Option("--total", help="Hard cap on total submissions per participant"),
    ] = None,
):
    """Set the submission quota for an evaluation queue.

    Only the options you provide are updated; existing quota settings are
    preserved.
    """
    try:
        queue.set_evaluation_quota(
            evaluation_id,
            first_round_start=first_round_start,
            round_duration_millis=round_duration_millis,
            number_of_rounds=number_of_rounds,
            submissions_per_round=submissions_per_round,
            total_submissions=total_submissions,
        )
    except UnknownSynapseID as err:
        sys.exit(err)
    typer.echo(f"✅ Quota updated for evaluation queue {evaluation_id}.")


@app.command()
def bulk_status(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    from_status: Annotated[
        str,
        typer.Option("--from", help="Current status of submissions to update"),
    ] = "SCORED",
    to_status: Annotated[
        str,
        typer.Option("--to", help="Status to assign"),
    ] = "VALIDATED",
):
    """Bulk-update the status of all submissions in an evaluation queue.

    Useful for re-scoring: flip submissions from SCORED back to VALIDATED
    so they are picked up by a scoring harness again.
    """
    utils.change_all_submission_status(evaluation_id, from_status, to_status)
    typer.echo(
        f"✅ All {from_status} submissions in queue {evaluation_id} "
        f"updated to {to_status}."
    )
