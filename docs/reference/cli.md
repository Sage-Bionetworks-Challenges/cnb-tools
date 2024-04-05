<!--termynal -->

```
(cnb-tools) $ cnb-tools
Manage challenges on Synapse.org from the CLI

Enter `cnb-tools --help` for usage information.


# Get the current version
(cnb-tools) $ cnb-tools --version
cnb-tools v0.2.0


# Basic usage
(cnb-tools) $ cnb-tools COMMAND ARGS [OPTIONS]
```

---

## Command: `submission`

Manage submissions on Synapse, e.g. download prediction file/Docker model,
view submission metadata, update submission status, etc.

### `annotate`

Annotate a submission using a JSON file. This subcommand can be used to update
existing annotations with new values.

```bash
cnb-tools submission annotate SUB_ID JSON_FILE [--verbose]
```

Replace the following:

- _`SUB_ID`_ - submission ID
- _`JSON_FILE`_ - filepath to JSON file containing annotations as
  key-value pairs

Options:

Name | Type | Description | Default
--|--|--|--
`--verbose` | boolean | Output all submission annotations after annotating | False

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
cnb-tools submission delete SUB_ID ... [--force] [--skip-errors]
```

Replace the following:

- _`SUB_ID ...`_ - submission ID(s)

Options:

Name | Type | Description | Default
--|--|--|--
`--force` | boolean | Force deletion without confirmation | False
`--skip-errors` | boolean | Continue update even if unknown ID error is encountered | False

### `download`

Download a submission to your local machine.

If the submission is a file, you can optionally specify the download destination
with `--dest` (or `-d`). `--dest` is ignored if the submission is a Docker image.

```bash
cnb-tools submission download SUB_ID [--dest/-d DESTINATION]
```

Replace the following:

- _`SUB_ID`_ - submission ID

Options:

Name | Type | Description | Default
--|--|--|--
`--dest`, `-d` | str  | Filepath to where submission will be downloaded | `.`

### `info`

Get general information about a submission, such as the submission date, who
submitted it, and name of the challenge. You can also get the current status
and annotations with `--verbose`.

```bash
cnb-tools submission info SUB_ID [--verbose]
```

Replace the following:

- _`SUB_ID`_ - submission ID

Options:

Name | Type | Description | Default
--|--|--|--
`--verbose` | boolean | Output the submission status and annotations | False

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

!!!info "More commands coming soon!"
