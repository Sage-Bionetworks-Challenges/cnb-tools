"""CLI command: submission

Manage submissions.

Example:
    $ cnb-tools submission --help
"""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from enum import Enum
from typing_extensions import Annotated
import typer

from cnb_tools.modules.client import UnknownSynapseID
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
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    json_file: Annotated[
        Path,
        typer.Option(
            "--file",
            "-f",
            help="Filepath to JSON file containing annotations",
            exists=True,
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
    legacy: Annotated[
        bool,
        typer.Option(
            "--legacy",
            help=(
                "Use legacy structured annotation format (stringAnnos/longAnnos/"
                "doubleAnnos) for compatibility with older leaderboard widgets "
                "(default: false)"
            ),
        ),
    ] = False,
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip-errors",
            help="Continue if an unknown ID error is encountered (default: false)",
        ),
    ] = False,
):
    """Annotate one or more submission(s) with a JSON file.

    When --legacy is set, also writes annotations in the legacy
    stringAnnos/longAnnos/doubleAnnos format for compatibility with
    older leaderboard widgets.
    """

    def _annotate_one(submission_id: int) -> tuple[int, BaseException | None]:
        try:
            if legacy:
                annotation.update_legacy_annotations_from_file(
                    submission_id, str(json_file), verbose=verbose
                )
            annotation.update_annotations_from_file(
                submission_id, str(json_file), verbose
            )
            return (submission_id, None)
        except UnknownSynapseID as err:
            return (submission_id, err)

    if skip_errors:
        with ThreadPoolExecutor(max_workers=min(8, len(submission_ids))) as pool:
            futures = {pool.submit(_annotate_one, sid): sid for sid in submission_ids}
            for future in as_completed(futures):
                sid, err = future.result()
                if err is not None:
                    print(f"Unknown submission ID: {sid} - skipping...")
    else:
        for sid in submission_ids:
            _, err = _annotate_one(sid)
            if err is not None:
                sys.exit(err)


@app.command()
def change_status(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    new_status: Annotated[Status, typer.Argument()],
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip-errors",
            help="Continue update even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Update one or more submission statuses."""

    def _change_one(submission_id: int) -> tuple[int, BaseException | None]:
        try:
            annotation.update_submission_status(submission_id, new_status.value)
            return (submission_id, None)
        except UnknownSynapseID as err:
            return (submission_id, err)

    if skip_errors:
        with ThreadPoolExecutor(max_workers=min(8, len(submission_ids))) as pool:
            futures = {pool.submit(_change_one, sid): sid for sid in submission_ids}
            for future in as_completed(futures):
                sid, err = future.result()
                if err is not None:
                    print(f"Unknown submission ID: {sid} - skipping...")
    else:
        for sid in submission_ids:
            _, err = _change_one(sid)
            if err is not None:
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
            "--skip-errors",
            help="Continue deletion even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Delete one or more submissions."""
    print()
    if force:

        def _delete_one(submission_id: int) -> tuple[int, BaseException | None]:
            try:
                submission.delete_submission(submission_id)
                return (submission_id, None)
            except UnknownSynapseID as err:
                return (submission_id, err)

        if skip_errors:
            with ThreadPoolExecutor(max_workers=min(8, len(submission_ids))) as pool:
                futures = {pool.submit(_delete_one, sid): sid for sid in submission_ids}
                for future in as_completed(futures):
                    sid, err = future.result()
                    if err is not None:
                        print(f"Unknown submission ID: {sid} - skipping...")
        else:
            for sid in submission_ids:
                _, err = _delete_one(sid)
                if err is not None:
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
def get(
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
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """Get information about a submission"""
    if as_json:
        import json
        import dataclasses

        sub = submission.get_submission(submission_id)
        typer.echo(json.dumps(dataclasses.asdict(sub), indent=2, default=str))
    else:
        submission.print_submission_info(submission_id, verbose)


@app.command()
def get_contributors(
    submission_id: Annotated[int, typer.Argument(help="Submission ID")],
    human_readable: Annotated[
        bool,
        typer.Option(
            "--pretty-print",
            "-pp",
            help="Resolve IDs to team/user names (default: false)",
        ),
    ] = False,
):
    """Get contributors for a submission."""
    sub = submission.get_submission(submission_id)

    if sub.team_id:
        team = (
            submission.get_submitter_name(sub.team_id)
            if human_readable
            else sub.team_id
        )
        typer.echo(f"Team: {team}\n")

    contributors = submission.get_submission_contributors(submission_id)
    if contributors:
        typer.echo("Contributors:")
        if human_readable:
            principal_ids = [user.get("principalId") for user in contributors]
            with ThreadPoolExecutor(max_workers=min(8, len(principal_ids))) as pool:
                names = list(
                    pool.map(
                        lambda p: submission.get_submitter_name(int(p)), principal_ids
                    )
                )
            for name in names:
                typer.echo(f"  {name}")
        else:
            for user in contributors:
                typer.echo(f"  {user.get('principalId')}")
    else:
        typer.echo("No contributors found.")


@app.command()
def batch_download(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    dest: Annotated[
        Path,
        typer.Option(
            "--dest",
            "-d",
            help="Root destination directory (default: current directory)",
        ),
    ] = ".",
    status: Annotated[
        str | None,
        typer.Option(
            "--status",
            "-s",
            help=(
                "Only download submissions with this status "
                "(e.g. SCORED, ACCEPTED). Downloads all statuses if omitted."
            ),
        ),
    ] = None,
):
    """Batch-download all submission files from an evaluation queue.

    Files are saved under DEST/<submitter>/<submission_id><ext>.
    Docker submissions are skipped.
    """
    submission.batch_download_submissions(evaluation_id, str(dest), status)


@app.command()
def reset(
    submission_ids: Annotated[
        list[int], typer.Argument(help="One or more submission ID(s)")
    ],
    skip_errors: Annotated[
        bool,
        typer.Option(
            "--skip-errors",
            help="Continue update even if unknown ID error is encountered (default: False)",
        ),
    ] = False,
):
    """Reset one or more submission to RECEIVED."""
    change_status(
        submission_ids=submission_ids,
        new_status=Status.received,
        skip_errors=skip_errors,
    )
