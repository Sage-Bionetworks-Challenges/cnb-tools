---
name: create-challenge
description: 'Create a new Synapse challenge from scratch. USE FOR: user says "create a challenge", "set up a challenge", "new challenge", "scaffold a challenge". PERFORMS: collects challenge name, task count, and portal preferences, runs cnb-tools challenge create, guides infrastructure setup (py-orca or SynapseWorkflowOrchestrator), then walks through launch and post-setup steps.'
argument-hint: 'Challenge name, number of tasks, and whether to register on the Challenge Portal.'
---

# Create a New Synapse Challenge

Scaffolds a complete challenge project on Synapse using `cnb-tools`.

## What gets created

| Resource | Details |
|---|---|
| Live project | Synapse project named after the challenge, Status = `Upcoming` |
| Participants team | Public-join team; email notifications disabled |
| Organizers team | Private team for challenge staff |
| Evaluation queues | One per task (e.g. "My Challenge Task 1") |
| Data folders | `Data/` (Training, Validation) — participants get download access |
| | `Private Data/` (Groundtruth, Test) — organizers only |
| Wiki | Copied from the CNB portal template with real IDs substituted |
| Portal registration | Added to `Curated Challenge Projects` table (optional) |

---

## Step 1: Gather inputs

Ask the user:
1. **Challenge name** — used as the project name and prefix for all teams/queues
2. **Number of tasks** — defaults to `1`; creates one queue + data folder set per task
3. **Existing live project?** — if the Synapse project already exists, pass its synID via `--live-site` to skip project creation
4. **Register on portal?** — whether to add to `challenges.synapse.org` (default: yes); use `--no-portal` to skip
5. **GitHub token** *(optional)* — a [GitHub personal access token](https://github.com/settings/tokens) with at least `public_repo` scope (add `repo` scope for private repos). If provided, the evaluation infrastructure repo can be created automatically via the GitHub API in Step 5. If not provided, the user can create it manually via the GitHub UI.
6. **GitHub owner** *(optional, required if token provided)* — the GitHub org or username where the new repo should be created (e.g. `Sage-Bionetworks-Challenges`)

---

## Step 2: Create the challenge

```bash
# Minimal (1 task, register on portal)
cnb-tools challenge create "My Challenge"

# Multiple tasks
cnb-tools challenge create "My Challenge" --tasks 3

# Use an existing Synapse project
cnb-tools challenge create "My Challenge" --live-site syn12345

# Skip portal registration
cnb-tools challenge create "My Challenge" --no-portal
```

On success, outputs:
```
✅ Challenge creation complete:
   Live project synID:    syn<id>
   Participants teamID:   <id>
   Organizers teamID:     <id>
```

Save these IDs — they are needed for all subsequent steps.

---

## Step 3: Verify the setup

```bash
# Confirm challenge is registered
cnb-tools challenge get <live_project_synid>

# List evaluation queues
cnb-tools challenge queues <live_project_synid>

# List registered teams
cnb-tools challenge teams <live_project_synid>
```

---

## Step 4: Customize before launch

Before making the project public:
- Update the wiki on Synapse with challenge-specific instructions, dates, and rules
- Upload training/validation data to `Data/Training` and `Data/Validation`
- Upload ground truth to `Private Data/Groundtruth` and test data to `Private Data/Test`
- Add organizers to the Organizers team on Synapse
- (Optional) Add evaluation round/quota limits to queues:
  ```bash
  cnb-tools queue add-round <queue_id> --start <YYYY-MM-DD> --end <YYYY-MM-DD> --daily-limit 3
  ```

---

## Step 5: Set up evaluation infrastructure

Ask the user which orchestration tool they want to use:

| | **py-orca** (recommended) | **SynapseWorkflowOrchestrator** (legacy) |
|---|---|---|
| Managed by | Sage DPE team | Self-managed |
| Technology | Python + Docker + Nextflow | CWL + Docker |
| Submission type | Prediction files, Docker images | Prediction files, Docker images |
| Perks | Each submission gets their own environment | Offers GPU support for deep-learning challenges |

---

### Option A: py-orca (recommended)

py-orca is the current recommended orchestration tool, run and maintained by the Sage Data Processing & Engineering (DPE) team.

**1. Create your evaluation repo from the template:**

If a GitHub token was provided, create the repo automatically:

```bash
export GITHUB_TOKEN="<your_token>"
export REPO_OWNER="<github_org_or_user>"
export REPO_NAME="<new_repo_name>"  # e.g. my-challenge-evaluation

curl -L \
  -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/Sage-Bionetworks-Challenges/orca-evaluation-templates/generate \
  -d "{\"owner\":\"$REPO_OWNER\",\"name\":\"$REPO_NAME\",\"private\":false}"
```

On success the API returns `201 Created` with the new repo URL in the response. Otherwise, ask the user to go to [orca-evaluation-templates](https://github.com/Sage-Bionetworks-Challenges/orca-evaluation-templates) and click **Use this template → Create a new repository** manually.

**2. Write your scripts:**
- Adapt `validate.py` — define file format checks (columns, data types, value ranges, duplicate/missing IDs, etc.)
- Adapt `score.py` — implement your evaluation metrics (e.g. AUROC, AUPRC)
- Update `requirements.txt` with any additional dependencies

> For multi-task challenges, create additional `validate_taskN()` / `score_taskN()` functions and route to them in the `validate()` / `score()` dispatcher. **Do not modify `main()`** — it is specifically designed for ORCA compatibility.

**3. Dockerize your scripts:**

The template includes a GitHub Actions workflow that automatically builds and publishes a Docker image when you create a new release (use SemVer, e.g. `v1.0.0`). The image will appear under **Packages** in your repo.

To build and push manually instead:
```bash
docker build -t IMAGE_NAME:TAG .
docker push IMAGE_NAME:TAG
```
The image must be publicly accessible so ORCA can pull it.

**4. Connect with the DPE team:**

Reach out to the DPE team via the [DPE Service Desk](https://sagebionetworks.jira.com/servicedesk/customer/portal/5/group/7/create/51) to request that your challenge be added to ORCA. Provide details such as:
- Challenge name
- Synapse project ID
- Evaluation repo URL
- Funding source

**5. Add your container image to your challenge profile:**

Create a PR to [nf-synapse-challenge](https://github.com/Sage-Bionetworks-Workflows/nf-synapse-challenge) to add your container image to your challenge profile. The DPE team will review and merge it, which will make your image available to ORCA.

---

### Option B: SynapseWorkflowOrchestrator

SynapseWorkflowOrchestrator is a self-managed tool that runs CWL workflows on a Synapse-connected server.
It is a legacy tool but it still works for many challenges. It is recommended if you have a server and
are comfortable with self-managing the infrastructure using CWL and Docker.

This may be a good option if funding is limited or if you want to run your own server for evaluation. However,
it requires more setup and maintenance than py-orca.

First, ask the user what **submission type** participants will use:

| Submission type | Template |
|---|---|
| **Data-to-model** — participants submit **prediction files** | [data-to-model-challenge-workflow](https://github.com/Sage-Bionetworks-Challenges/data-to-model-challenge-workflow) |
| **Model-to-data** — participants submit **Docker images** run against hidden data | [model-to-data-challenge-workflow](https://github.com/Sage-Bionetworks-Challenges/model-to-data-challenge-workflow) |

**Quick start (same for both templates):**
1. Create your workflow repo from the template.

   If a GitHub token was provided, set the appropriate template URL and run:

   ```bash
   export GITHUB_TOKEN="<your_token>"
   export REPO_OWNER="<github_org_or_user>"
   export REPO_NAME="<new_repo_name>"  # e.g. my-challenge-workflow
   export TEMPLATE_REPO="data-to-model-challenge-workflow"  # or model-to-data-challenge-workflow

   curl -L \
     -X POST \
     -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     https://api.github.com/repos/Sage-Bionetworks-Challenges/$TEMPLATE_REPO/generate \
     -d "{\"owner\":\"$REPO_OWNER\",\"name\":\"$REPO_NAME\",\"private\":false}"
   ```

   Otherwise, go to the relevant template repo above and click **Use this template → Create a new repository** manually.
2. Adapt the scoring and validation scripts in the `evaluation/` folder
3. Update `workflow.cwl` (and `writeup-workflow.cwl` if applicable) with your challenge's inputs and steps
4. Test CWL scripts locally with [cwltool](https://github.com/common-workflow-language/cwltool):
   ```bash
   cwltool steps/<step>.cwl <inputs.yml>
   ```
5. Create an **"evaluation workflow" file link** in the Synapse challenge project (see below).
6. Deploy SynapseWorkflowOrchestrator on a server and point it at your `workflow.cwl`

**Resources:**
- [CWL user guide](https://www.commonwl.org/user_guide/)
- [Docker docs](https://docs.docker.com/get-started/)
- [SynapseWorkflowOrchestrator](https://github.com/Sage-Bionetworks/SynapseWorkflowOrchestrator)

#### Create the evaluation workflow file link entity

After the GitHub repo exists, create a file link entity in the challenge project that points to the repo zip, is accessible only by organizers, and carries the `ROOT_TEMPLATE` annotation that SynapseWorkflowOrchestrator uses to find the entry-point CWL file.

Run the following Python script (the `project_id`, `organizer_team_id`, `repo_owner`, and `repo_name` values all come from earlier steps):

```python
import synapseclient

syn = synapseclient.login()

# ── fill in from previous steps ──────────────────────────────────────────────
project_id = "<live_project_synid>"
organizer_team_id = "<organizer_team_id>"
repo_owner = "<github_org_or_user>"
repo_name = "<new_repo_name>"
# ─────────────────────────────────────────────────────────────────────────────

zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/main.zip"

# 1. Create an external file handle pointing to the repo zip
file_handle = syn.create_external_file_handle(
    url=zip_url,
    mimetype="application/zip",
)

# 2. Store the file link entity with the ROOT_TEMPLATE annotation
branch = "main"
root_template = f"{repo_name}-{branch}/workflow.cwl"

workflow_entity = synapseclient.File(
    name="evaluation workflow",
    parent=project_id,
    dataFileHandleId=file_handle["id"],
    annotations={"ROOT_TEMPLATE": root_template},
)
workflow_entity = syn.store(workflow_entity)
print(f"Created: {workflow_entity.name} ({workflow_entity.id})")

# 3. Apply local sharing settings — organizers only.
#    POST creates a brand-new ACL for this entity, overriding project inheritance.
#    This ensures the entity stays private even after the project is launched publicly.
acl = {
    "id": workflow_entity.id,
    "resourceAccess": [
        {
            "principalId": int(organizer_team_id),
            "accessType": [
                "READ", "UPDATE", "DELETE", "CHANGE_PERMISSIONS",
                "CHANGE_SETTINGS", "DOWNLOAD", "CREATE", "MODERATE",
            ],
        }
    ],
}
try:
    syn.restPOST(f"/entity/{workflow_entity.id}/acl", body=acl)
except synapseclient.core.exceptions.SynapseHTTPError:
    # Entity already has a local ACL — update it instead
    syn.restPUT(f"/entity/{workflow_entity.id}/acl", body=acl)

print(f"Sharing: organizers-only local ACL applied to {workflow_entity.id}")

---

## Step 6: Launch the challenge

When ready to go public:

```bash
cnb-tools challenge launch <live_project_synid>
```

This grants READ access to all authenticated Synapse users and sets `Status = Active`.

---

## Step 7: Close the challenge (when done)

```bash
cnb-tools challenge close <live_project_synid>
```

This sets `Status = Closed`, revokes submission permissions from the participant team,
and locks the participant team so no new members can join.

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `Team 'X Participants' already exists` | Team name collision from a previous run | Confirm reuse when prompted, or choose a different challenge name |
| `UnknownSynapseID` on `--live-site` | Invalid or inaccessible synID | Verify the synID and that you have EDIT access |
| Portal registration fails | No EDIT access to `syn51476218` | Use `--no-portal` and register manually, or contact a CNB admin |
| Wiki copy fails | Missing READ access to template `syn52941681` | Ensure you are logged in with a Synapse account that can access the template |
