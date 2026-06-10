"""CLI command: queue

Manage Synapse evaluation queues.

Example:
    $ cnb-tools queue --help
"""

import dataclasses
import json
import sys
from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools.modules import queue
from cnb_tools.modules.client import UnknownSynapseID

app = typer.Typer()


@app.command()
def get(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """Get details about an evaluation queue."""
    try:
        ev = queue.get_evaluation(evaluation_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    if as_json:
        typer.echo(json.dumps(dataclasses.asdict(ev), indent=2))
    else:
        typer.echo(f"ID:          {ev.id}")
        typer.echo(f"Name:        {ev.name}")
        typer.echo(f"Description: {ev.description or '—'}")
        typer.echo(f"Project:     {ev.content_source}")


@app.command()
def add_round(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    round_start: Annotated[
        str,
        typer.Option(
            "--start",
            help='ISO-8601 datetime when the round opens, e.g. "2025-01-01T00:00:00.000Z"',
        ),
    ],
    round_end: Annotated[
        str,
        typer.Option(
            "--end",
            help='ISO-8601 datetime when the round closes, e.g. "2025-06-01T00:00:00.000Z"',
        ),
    ],
    daily_limit: Annotated[
        Optional[int],
        typer.Option("--daily", help="Max submissions per participant per day"),
    ] = None,
    weekly_limit: Annotated[
        Optional[int],
        typer.Option(
            "--weekly", help="Max submissions per participant per calendar week"
        ),
    ] = None,
    monthly_limit: Annotated[
        Optional[int],
        typer.Option(
            "--monthly", help="Max submissions per participant per calendar month"
        ),
    ] = None,
    total_limit: Annotated[
        Optional[int],
        typer.Option("--total", help="Hard cap on total submissions per participant"),
    ] = None,
):
    """Add a submission round to an evaluation queue.

    Creates an EvaluationRound with optional per-day, per-week, per-month,
    or total submission limits. Multiple rounds can be added to the same queue.
    """
    try:
        result = queue.create_evaluation_round(
            evaluation_id,
            round_start=round_start,
            round_end=round_end,
            daily_limit=daily_limit,
            weekly_limit=weekly_limit,
            monthly_limit=monthly_limit,
            total_limit=total_limit,
        )
    except Exception as err:
        sys.exit(f"⛔ {err}")
    typer.echo(f"✅ Round {result['id']} added to evaluation queue {evaluation_id}.")
    typer.echo(f"   Start: {result['roundStart']}")
    typer.echo(f"   End:   {result['roundEnd']}")
    if result.get("limits"):
        for lim in result["limits"]:
            typer.echo(f"   {lim['limitType']}: {lim['maximumSubmissions']}")
