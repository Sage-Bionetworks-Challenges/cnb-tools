"""CLI command: summarize

Summarize challenge by submissions and participants.

Example:
    $ cnb-tools summarize --help
    $ cnb-tools summarize submissions syn12345678
    $ cnb-tools summarize submissions syn12345678 --weekly
    $ cnb-tools summarize participants syn12345678
"""

import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import typer
from rich import box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from synapseclient.models import UserProfile
from typing_extensions import Annotated

from cnb_tools.modules.challenge import get_challenge
from cnb_tools.modules.client import UnknownSynapseID, get_synapse_client
from cnb_tools.modules.queue import get_evaluations_by_project

app = typer.Typer()

# ---------------------------------------------------------------------------
# Participant classification
# ---------------------------------------------------------------------------

_ACADEMIA_KEYWORDS = {
    "university",
    "université",
    "universitat",
    "universidad",
    "universidade",
    "college",
    "institute",
    "institution",
    "school",
    "hospital",
    "clinic",
    "academic",
    "academia",
    "research",
    "laboratory",
    "lab",
    "student",
    "faculty",
    "department",
    "dept",
    "center",
    "centre",
}
_INDUSTRY_KEYWORDS = {
    "inc",
    "corp",
    "corporation",
    "ltd",
    "llc",
    "gmbh",
    "pharma",
    "biotech",
    "therapeutics",
    "diagnostics",
    "technologies",
    "solutions",
    "systems",
    "software",
    "consulting",
    "ventures",
}
_GOVERNMENT_KEYWORDS = {
    "government",
    "federal",
    "national",
    "ministry",
    "agency",
    "bureau",
    "nih",
    "nci",
    "fda",
    "cdc",
    "nasa",
    "darpa",
}
_NONPROFIT_KEYWORDS = {
    "foundation",
    "nonprofit",
    "non-profit",
    "charity",
    "association",
    "society",
    "alliance",
}

_CATEGORY_ORDER = [
    "Academia",
    "Industry / For-profit",
    "Government",
    "Non-profit",
    "Other",
    "Not specified",
]
_CATEGORY_COLORS = {
    "Academia": "cyan",
    "Industry / For-profit": "yellow",
    "Government": "blue",
    "Non-profit": "magenta",
    "Other": "red",
    "Not specified": "dim",
}


def _classify_org(company: str, industry: str) -> str:
    text = (company + " " + industry).lower()
    if not text.strip():
        return "Not specified"
    for kw in _ACADEMIA_KEYWORDS:
        if kw in text:
            return "Academia"
    for kw in _GOVERNMENT_KEYWORDS:
        if kw in text:
            return "Government"
    for kw in _NONPROFIT_KEYWORDS:
        if kw in text:
            return "Non-profit"
    for kw in _INDUSTRY_KEYWORDS:
        if kw in text:
            return "Industry / For-profit"
    return "Other"


# ---------------------------------------------------------------------------
# Submission trends helpers
# ---------------------------------------------------------------------------


def _fetch_submission_dates(syn, evaluation_id: str) -> list[str]:
    dates = []
    for sub in syn.getSubmissions(evaluation_id):
        created_on = sub.get("createdOn")
        if created_on:
            dt = datetime.fromisoformat(created_on.replace("Z", "+00:00"))
            dates.append(dt.strftime("%Y-%m-%d"))
    return dates


def _to_week(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def submissions(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
    weekly: Annotated[
        bool,
        typer.Option("--weekly", help="Group by ISO week instead of day"),
    ] = False,
):
    """Show a histogram of submissions over time.

    Fetches all submissions across every evaluation queue and prints a bar
    chart grouped by day (default) or ISO week (--weekly).
    """
    syn = get_synapse_client()
    console = Console()

    try:
        evaluations = get_evaluations_by_project(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)

    if not evaluations:
        typer.echo(f"No evaluation queues found for {project_id}.")
        return

    console.print(
        f"Found [bold]{len(evaluations)}[/bold] queue(s). Fetching submissions...\n"
    )

    all_dates: list[str] = []

    def _fetch(ev) -> list[str]:
        return _fetch_submission_dates(syn, ev.id)

    with ThreadPoolExecutor(max_workers=min(8, len(evaluations))) as pool:
        futures = {pool.submit(_fetch, ev): ev for ev in evaluations}
        for future in as_completed(futures):
            all_dates.extend(future.result())

    if not all_dates:
        typer.echo("No submissions found.")
        return

    if weekly:
        counts: Counter = Counter(_to_week(d) for d in all_dates)
        label = "week"
    else:
        counts = Counter(all_dates)
        label = "day"

    sorted_keys = sorted(counts.keys())
    max_count = max(counts.values())
    total = sum(counts.values())
    bar_width = 40

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        title=f"Submissions per {label}  (total: {total})",
        title_style="bold",
    )
    table.add_column(label.capitalize(), style="dim", no_wrap=True)
    table.add_column("Bar", min_width=bar_width)
    table.add_column("Count", justify="right", style="bold green")
    table.add_column("%", justify="right", style="cyan")

    for key in sorted_keys:
        count = counts[key]
        filled = int(count / max_count * bar_width) if max_count > 0 else 0
        bar = "[green]" + "█" * filled + "[/green]"
        pct = f"{count / total * 100:.1f}"
        table.add_row(key, bar, str(count), pct)

    console.print(table)


@app.command()
def participants(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
):
    """Show a breakdown of participants by organization type.

    Classifies each participant based on the company and industry fields in
    their Synapse profile using keyword matching. Results are estimates.
    """
    syn = get_synapse_client()
    console = Console()

    try:
        chal = get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)

    team_id = chal["participantTeamId"]
    console.print(
        f"Project [bold]{project_id}[/bold] → participant team [bold]{team_id}[/bold]"
    )

    members = list(syn._GET_paginated(f"/teamMembers/{team_id}"))
    user_ids = [m["member"]["ownerId"] for m in members]
    console.print(
        f"Found [bold]{len(user_ids)}[/bold] member(s). Fetching profiles...\n"
    )

    def _classify(uid: str) -> str:
        profile = UserProfile.from_id(user_id=int(uid))
        return _classify_org(
            profile.company or "",
            profile.industry or "",
        )

    counts: Counter = Counter()
    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("Fetching profiles...", total=len(user_ids))
        with ThreadPoolExecutor(max_workers=min(16, len(user_ids))) as pool:
            futures = {pool.submit(_classify, uid): uid for uid in user_ids}
            for future in as_completed(futures):
                counts[future.result()] += 1
                progress.advance(task)

    total = sum(counts.values())
    bar_width = 40
    max_count = max(counts.values()) if counts else 1

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        title=f"Participant breakdown  (total: {total})",
        title_style="bold",
    )
    table.add_column("Category", no_wrap=True)
    table.add_column("Bar", min_width=bar_width)
    table.add_column("Count", justify="right", style="bold green")
    table.add_column("%", justify="right", style="cyan")

    for category in _CATEGORY_ORDER:
        count = counts.get(category, 0)
        color = _CATEGORY_COLORS[category]
        filled = int(count / max_count * bar_width) if count > 0 else 0
        bar = f"[{color}]" + "█" * filled + f"[/{color}]"
        pct = f"{count / total * 100:.1f}" if count > 0 else "0.0"
        table.add_row(f"[{color}]{category}[/{color}]", bar, str(count), pct)

    console.print(table)
    console.print(
        "[dim]Note: Categories are estimated using keyword matching on self-reported "
        "company and industry fields. Results may not be accurate.[/dim]\n"
    )
