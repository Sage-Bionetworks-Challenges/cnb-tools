---
name: challenge-summary
description: 'Summarize the current state of a Synapse challenge. USE FOR: user says "summarize challenge", "challenge summary", "how is the challenge going", "challenge stats", or "give me an overview of the challenge". PERFORMS: runs cnb-tools stats command, optionally shows submission trends by day or week, and optionally shows participant breakdown by org type.'
argument-hint: 'Synapse project ID (e.g. syn12345).'
---

# Challenge Summary Skill

Produces a full summary of a running or completed Synapse challenge using
`cnb-tools` CLI commands.

## What this skill produces

1. **Core stats** — registered participants, teams, queues, total submissions, participants map URL
2. **Submission trends** — histogram of submissions over time (by day or week)
3. **Participant breakdown** — org-type distribution (Academia, Industry, Government, Non-profit)

---

## Step 1: Gather inputs

Ask the user if you don't already know:
- `<project_id>` — Synapse ID of the challenge project (e.g. `syn74274097`)
- Preferred time granularity: **daily** (default) or **weekly**

---

## Step 2: Core stats

```bash
cnb-tools challenge stats <project_id>
```

This outputs:
- Registered participants (individual members of the participant team)
- Registered teams (teams registered to the challenge)
- Evaluation queues (total count)
- Total submissions (across all queues)
- Participants map URL: `https://www.synapse.org/Map:<team_id>`

---

## Step 3: Submission trends

```bash
# Daily breakdown
cnb-tools summarize submissions <project_id>

# Weekly breakdown (recommended for longer challenges)
cnb-tools summarize submissions <project_id> --weekly
```

This fetches `createdOn` timestamps from all submissions across all queues in
parallel and renders a histogram grouped by day or ISO week.

---

## Step 4: Participant breakdown

```bash
cnb-tools summarize participants <project_id>
```

Classifies each participant by organization type based on `company` and
`industry` fields in their Synapse user profile.

Categories and colors:
| Category | Color |
|---|---|
| Academia | cyan |
| Industry / For-profit | yellow |
| Government | blue |
| Non-profit | magenta |
| Other | red |
| Not specified | dim |

> **Note:** A large proportion of users leave `company`/`industry` blank,
> so "Not specified" is expected to be the largest category. Categories
> are estimated using keyword matching and may not be fully accurate.


---

## Interpreting the output

- **Registered participants vs teams**: participants = individual users in the
  participant team; teams = teams registered to submit (one team can have many
  members).
- **Submission trends**: spikes near deadlines are normal. Look for the final
  week to identify late-stage activity.
- **Per-queue breakdown**: Docker queues typically have far fewer submissions
  than prediction queues — this is expected.

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `UnknownSynapseID` on stats | Project not registered as a challenge | Run `cnb-tools challenge get <project_id>` to verify |
| Submission count seems low | API pagination was capped at 10 queues (old bug, fixed) | Ensure you're on the latest version |
| `Other / Not specified` is very high | Most users don't fill in company/industry | Expected; surface it honestly |
