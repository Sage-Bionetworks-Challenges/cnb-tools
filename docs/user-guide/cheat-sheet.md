# Cheat Sheet

A quick-reference summary of the Python API. For CLI commands, see the [CLI Reference](../reference/cli.md).

!!! note "Need more Synapse functionality?"
    cnb-tools covers challenge-specific operations. For broader interactions
    with Synapse — uploading files, managing permissions on arbitrary entities,
    querying tables, etc. — use the
    [Synapse Python Client](https://python-docs.synapse.org/) directly.
    cnb-tools installs it as a dependency, so it is always available.

---

## Python API

### Challenge

```python
from cnb_tools import get_challenge, create_challenge, delete_challenge, get_registered_teams

get_challenge(project_id)                  # get challenge metadata
create_challenge(project_id, team_id)      # register project as a challenge
delete_challenge(challenge_id)             # delete a challenge
get_registered_teams(challenge_id)         # list all registered teams
```

### Queue

```python
from cnb_tools import get_evaluation, get_evaluations_by_project, create_evaluation, create_evaluation_round

get_evaluation(evaluation_id)                        # get queue details
get_evaluations_by_project(project_id)               # list all queue objects for a project
create_evaluation(name, description, project_id)     # create a new queue
create_evaluation_round(evaluation_id, ...)          # add a submission round
```

### Submission

```python
from cnb_tools import get_submission, delete_submission, download_submission, batch_download_submissions
from cnb_tools import get_submitter_name, get_submission_contributors

get_submission(submission_id)                        # fetch a submission
get_submitter_name(principal_id)                     # resolve ID to name
get_submission_contributors(submission_id)           # list contributors
download_submission(submission_id, dest)             # download a file submission
batch_download_submissions(evaluation_id, dest)      # batch-download from a queue
delete_submission(submission_id)                     # delete a submission
```

### Annotations

```python
from cnb_tools import get_submission_status, update_annotations, update_annotations_from_file, update_submission_status

get_submission_status(submission_id)                          # get current status + annotations
update_annotations(submission_id, {"score": 0.95})           # update annotations from a dict
update_annotations_from_file(submission_id, "scores.json")   # update annotations from a JSON file
update_submission_status(submission_id, "SCORED")            # update submission status
```

### Validation Toolkit

```python
from cnb_tools import validation_toolkit as vtk

vtk.check_missing_keys(truth["id"], pred["id"])       # missing IDs
vtk.check_unknown_keys(truth["id"], pred["id"])       # unknown IDs
vtk.check_duplicate_keys(pred["id"])                  # duplicate IDs
vtk.check_nan_values(pred["score"])                   # NaN/None values
vtk.check_nan_values(pred["score"], include_inf=True) # also flag inf/-inf
vtk.check_values_range(pred["score"], 0, 1)           # values outside [min, max]
vtk.check_binary_values(pred["label"])                # values other than 0 or 1
vtk.check_valid_values(pred["label"], {"a", "b"})     # values outside allowed set
vtk.check_not_constant(pred["score"])                 # all-identical predictions
```