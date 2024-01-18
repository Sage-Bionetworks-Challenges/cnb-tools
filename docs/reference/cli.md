## Basic usage

<!--termynal -->
```
(cnb-tools) $ cnb-tools
Manage challenges on Synapse.org from the CLI

Enter `cnb-tools --help` for usage information.


# Get the current version
(cnb-tools) $ cnb-tools --version
cnb-tools v0.2.0
```

---

## `submission`

### `annotate`

Annotate a submission.  Existing annotations will be replaced with
the new values from the JSON file.

```bash
cnb-tools submission annotate SUB_ID JSON_FILE
```

Replace the following:

* _`SUB_ID`_ - submission ID to annotate
* _`JSON_FILE`_ - filepath to JSON file containing annotations as key-value pairs


### `change-status`

Update a submission status to one of:

* `RECEIVED`
* `VALIDATED`
* `INVALID`
* `SCORED`
* `ACCEPTED`
* `OPEN`
* `CLOSED`

```bash
cnb-tools submission change-status SUB_ID STATUS
```

Replace the following:

* _`SUB_ID`_ - submission ID to update
* _`STATUS`_ - new status

!!!Note
    Consider using [`reset`](#reset) if you need to update the status
    to `RECEIVED`.


### `delete`

Delete one or more submission(s) from the evaluation queue. By default,
this action will require confirmation; optionally use `--force` to bypass
the prompt.

!!!Warning 
    Once a submission has been deleted, it can NOT be recovered.  This
    includes the metadata about the submission.  Use this command with
    caution.

```bash
cnb-tools submission delete SUB_ID ... [--force]
```

Replace the following:

* _`SUB_ID ...`_ - submission ID(s) to delete
* `--force` - force deletion without confirmation


### `info`

Get general information about a submission.

```bash
cnb-tools submission info SUB_ID
```

Replace the following:

* _`SUB_ID`_ - submission ID to get info


### `pull`

Download a submission to your local machine.  If the submission
is a flat file, you can optionally specify the download destination
with `-d DESTINATION`

```bash
cnb-tools submission pull SUB_ID [-d/--dir DESTINATION]
```

Replace the following:

* _`SUB_ID`_ - submission ID to download
* `-d/--dir `_`DESTINATION`_ - (optional) filepath to where submission
    will be downloaded


### `reset`

Reset a submission (set the `status` to `RECEIVED`) and remove all
existing annotations.

```bash
cnb-tools submission reset SUB_ID
```

Replace the following:

* _`SUB_ID`_ - submission ID to reset

---
