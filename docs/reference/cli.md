<!--termynal -->

```
(cnb-tools) $ cnb-tools
Manage challenges on Synapse.org from the CLI

Enter `cnb-tools --help` for usage information.


# Get the current version
(cnb-tools) $ cnb-tools --version
cnb-tools v0.4.2


# Basic usage
(cnb-tools) $ cnb-tools COMMAND ARGS [OPTIONS]
```

---

## Command: `challenge`

Manage Synapse challenges.

### `create`

Create a new challenge on Synapse. By default, also registers the challenge on
the [Synapse Challenge Portal](https://challenges.synapse.org); use `--no-portal`
to skip this step.

Creates a live project, Participants and Organizers teams, per-task evaluation
queues, and data folders, and copies the CNB wiki template to the project.

```bash
cnb-tools challenge create NAME [--tasks/-t N] [--live-site SYNID] [--no-portal]
```

Replace the following:

- _`NAME`_ - name of the new challenge

Options:

Name | Type | Description | Default
--|--|--|--
`--tasks`, `-t` | int | Number of task evaluation queues and data folders to create | `1`
`--live-site` | str | Synapse ID of an existing live project (skips live project creation) | —
`--no-portal` | boolean | Skip registering the challenge in the Challenge Portal table | False

### `launch`

Launch a challenge by making the project publicly viewable. Grants READ access
to all authenticated Synapse users and sets the project's `Status` annotation
to `Active`.

```bash
cnb-tools challenge launch PROJECT_ID
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

### `register`

Register an existing Synapse project as a challenge. Attaches a participant
team to the project without scaffolding any additional infrastructure.

```bash
cnb-tools challenge register PROJECT_ID TEAM_ID
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the project to register as a challenge
- _`TEAM_ID`_ - Synapse ID of the participant team

### `unregister`

Unregister a Synapse project as a challenge. The project and its teams are
not affected.

```bash
cnb-tools challenge unregister PROJECT_ID
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

### `get`

Get challenge metadata for a Synapse project.

```bash
cnb-tools challenge get PROJECT_ID [--json]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--json` | boolean | Output raw JSON instead of formatted text | False

### `teams`

List all teams registered to a challenge, with team names resolved.

```bash
cnb-tools challenge teams PROJECT_ID [--json]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--json` | boolean | Output raw JSON instead of formatted text | False

### `queues`

List all evaluation queues for a challenge project.

```bash
cnb-tools challenge queues PROJECT_ID [--json]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--json` | boolean | Output raw JSON instead of formatted text | False

### `close`

Close a challenge. Sets the project `Status` annotation to `Closed`, downgrades
the participant team's evaluation queue permissions from _Can submit_ to _Can view_,
and locks the participant team so no new members can join or request membership.

```bash
cnb-tools challenge close PROJECT_ID
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

### `stats`

Show basic statistics for a challenge: number of registered participants,
registered teams, evaluation queues, total submissions (fetched in parallel
across all queues), and discussion thread count.

```bash
cnb-tools challenge stats PROJECT_ID [--json]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--json` | boolean | Output raw JSON instead of formatted text | False

---

## Command: `queue`

Manage Synapse evaluation queues.

### `get`

Get details about an evaluation queue.

```bash
cnb-tools queue get EVALUATION_ID [--json]
```

Replace the following:

- _`EVALUATION_ID`_ - evaluation queue ID

Options:

Name | Type | Description | Default
--|--|--|--
`--json` | boolean | Output raw JSON instead of formatted text | False

### `add-round`

Add a submission round to an evaluation queue. Multiple rounds can be added to
the same queue. Optionally specify per-day, per-week, per-month, or total
submission limits.

```bash
cnb-tools queue add-round EVALUATION_ID --start START --end END [--daily N] [--weekly N] [--monthly N] [--total N]
```

Replace the following:

- _`EVALUATION_ID`_ - evaluation queue ID

Options:

Name | Type | Description | Default
--|--|--|--
`--start` | str | ISO-8601 datetime when the round opens, e.g. `"2025-01-01T00:00:00.000Z"` | **required**
`--end` | str | ISO-8601 datetime when the round closes, e.g. `"2025-06-01T00:00:00.000Z"` | **required**
`--daily` | int | Max submissions per participant per day | —
`--weekly` | int | Max submissions per participant per calendar week | —
`--monthly` | int | Max submissions per participant per calendar month | —
`--total` | int | Hard cap on total submissions per participant | —

---

## Command: `submission`

Manage submissions on Synapse, e.g. download prediction file/Docker model,
view submission metadata, update submission status, etc.

### `annotate`

Annotate one or more submission(s) with a JSON file. Updates existing
annotations with new values. When `--legacy` is set, also writes annotations
in the legacy `stringAnnos`/`longAnnos`/`doubleAnnos` format for compatibility
with older leaderboard widgets.

```bash
cnb-tools submission annotate SUB_ID ... --file/-f JSON_FILE [--verbose/-v] [--legacy] [--skip-errors]
```

Replace the following:

- _`SUB_ID ...`_ - one or more submission ID(s)
- _`JSON_FILE`_ - filepath to JSON file containing annotations as key-value pairs

Options:

Name | Type | Description | Default
--|--|--|--
`--file`, `-f` | path | Filepath to JSON file containing annotations | **required**
`--verbose`, `-v` | boolean | Output final submission annotations after annotating | False
`--legacy` | boolean | Also write annotations in legacy stringAnnos/longAnnos/doubleAnnos format | False
`--skip-errors` | boolean | Continue if an unknown ID error is encountered | False

### `batch-download`

Batch-download all submission files from an evaluation queue. Files are saved
under `DEST/<submitter>/<submission_id><ext>`. Docker submissions are skipped.

```bash
cnb-tools submission batch-download EVALUATION_ID [--dest/-d DEST] [--status/-s STATUS]
```

Replace the following:

- _`EVALUATION_ID`_ - evaluation queue ID

Options:

Name | Type | Description | Default
--|--|--|--
`--dest`, `-d` | str | Root destination directory | `.`
`--status`, `-s` | str | Only download submissions with this status (e.g. `SCORED`, `ACCEPTED`) | all statuses

### `change-status`

Update the submission status of one or more submission(s).

```bash
cnb-tools submission change-status SUB_ID ... NEW_STATUS [--skip-errors]
```

Replace the following:

- _`SUB_ID ...`_ - submission ID(s)
- _`NEW_STATUS`_ - one of: `RECEIVED` | `VALIDATED` | `INVALID` | `SCORED` |
  `ACCEPTED` | `CLOSED`

!!!Note
    Consider using [`submission reset`](#reset) if you need to update the status to
    `RECEIVED`.

Options:

Name | Type | Description | Default
--|--|--|--
`--skip-errors` | boolean | Continue update even if unknown ID error is encountered | False

### `delete`

Delete one or more submission(s) from the evaluation queue. By default,
this action will require confirmation; optionally use `--force` to bypass
the prompt.

!!!Warning
    Once a submission has been deleted, **it CANNOT be recovered**. Use this
    command with extreme caution.

```bash
cnb-tools submission delete SUB_ID ... [--force/-f] [--skip-errors]
```

Replace the following:

- _`SUB_ID ...`_ - submission ID(s)

Options:

Name | Type | Description | Default
--|--|--|--
`--force`, `-f` | boolean | Force deletion without confirmation | False
`--skip-errors` | boolean | Continue deletion even if unknown ID error is encountered | False

### `download`

Download a submission to your local machine. If the submission is a file, you
can optionally specify the download destination with `--dest` (or `-d`).

```bash
cnb-tools submission download SUB_ID [--dest/-d DESTINATION]
```

Replace the following:

- _`SUB_ID`_ - submission ID

Options:

Name | Type | Description | Default
--|--|--|--
`--dest`, `-d` | str | Filepath to where submission will be downloaded | `.`

### `get`

Get general information about a submission, such as the submission date, who
submitted it, and name of the challenge. Use `--verbose` to also output the
current status and annotations.

```bash
cnb-tools submission get SUB_ID [--verbose/-v] [--json]
```

Replace the following:

- _`SUB_ID`_ - submission ID

Options:

Name | Type | Description | Default
--|--|--|--
`--verbose`, `-v` | boolean | Also output submission status and annotations | False
`--json` | boolean | Output raw JSON instead of formatted text | False

### `get-contributors`

Get the contributors for a submission. Use `--pretty-print` to resolve
principal IDs to team/user names.

```bash
cnb-tools submission get-contributors SUB_ID [--pretty-print/-pp]
```

Replace the following:

- _`SUB_ID`_ - submission ID

Options:

Name | Type | Description | Default
--|--|--|--
`--pretty-print`, `-pp` | boolean | Resolve IDs to team/user names | False

### `reset`

Reset one or more submission(s) (set `status` to `RECEIVED`).

```bash
cnb-tools submission reset SUB_ID ... [--skip-errors]
```

Replace the following:

- _`SUB_ID ...`_ - submission ID(s)

Options:

Name | Type | Description | Default
--|--|--|--
`--skip-errors` | boolean | Continue update even if unknown ID error is encountered | False

---

## Command: `summarize`

Summarize challenge activity for a post-challenge landscape. Results will return
as bar charts, counts, and percentages.

By default, all results are returned, but empty results can be ignored with `--ignore-empty`.

### `submissions`

Show a breakdown of submissions over time. Fetches all submissions across every
evaluation queue and groups them by day (default) or week (`--weekly`).

```bash
cnb-tools summarize submissions PROJECT_ID [--weekly] [--ignore-empty]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--weekly` | boolean | Group by ISO week instead of day | False
`--ignore-empty` | boolean | Hide rows with zero counts | False

### `participants`

Show a breakdown of participants by sector type (academia, government, non-profit, for-profit,
other).

!!!note
    Categories are estimated using keyword matching on self-reported profile
    fields. Results may not be accurate.

```bash
cnb-tools summarize participants PROJECT_ID [--ignore-empty]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--ignore-empty` | boolean | Hide categories with zero participants | False

Categories (in display order):

| Category | Description |
|---|---|
| Academia | Universities, hospitals, institutes, research centers |
| Industry / For-profit | Companies, biotech, pharma, consulting |
| Government | Federal agencies (NIH, FDA, CDC, etc.) |
| Non-profit | Foundations, societies, associations |
| Other | Profile fields filled but no keyword matched |
| Not specified | Both company and industry fields are blank |

### `queues`

Show a breakdown of submissions per evaluation queue.

```bash
cnb-tools summarize queues PROJECT_ID [--ignore-empty]
```

Replace the following:

- _`PROJECT_ID`_ - Synapse ID of the challenge project

Options:

Name | Type | Description | Default
--|--|--|--
`--ignore-empty` | boolean | Hide queues with zero submissions | False
