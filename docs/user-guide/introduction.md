# Introduction

Running a crowd-sourced challenge on Synapse involves a lot of repeated, manual
steps — creating projects, configuring evaluation queues, managing submissions,
and closing everything down at the end. **cnb-tools** is designed to make those
steps faster and less error-prone, whether you are running a small internal
benchmark or a large public Challenge.

This page walks through a typical challenge lifecycle and shows where
cnb-tools fits in at each stage.

---

## Stage 1: Setup

Before a challenge opens, organizers need to create the challenge infrastructure
on Synapse: a new Synapse project, participant and organizer teams, evaluation queues,
and data folders.

```bash
# Scaffold everything in one command
cnb-tools challenge create "My Challenge" --tasks 2
```

If you already have an existing Synapse project and just want to register it as
a challenge and link a participant team:

```bash
cnb-tools challenge register syn12345 syn67890
```

You can also configure submission quotas on a queue upfront:

```bash
cnb-tools queue add-round 98765 \
  --start "2025-03-01T00:00:00.000Z" \
  --end   "2025-06-01T00:00:00.000Z" \
  --daily 3
```

---

## Stage 2: Launch

When the challenge is ready to open, make the project publicly visible and
set its status to `Active`:

```bash
cnb-tools challenge launch syn12345
```

---

## Stage 3: Active Challenge

While the challenge is running, submissions come in and organizers need to
validate them, update statuses, and annotate results.

**Check which submission teams are registered:**

```bash
cnb-tools challenge teams syn12345
```

**Inspect a submission:**

```bash
cnb-tools submission get 112233 --verbose
```

**Update statuses in bulk after validation:**

```bash
cnb-tools submission change-status 112233 114455 116677 VALIDATED
```

**Annotate submissions with scores from a JSON file:**

```bash
cnb-tools submission annotate 112233 114455 --file scores.json
```

**Download prediction files for manual review or debugging:**

```bash
cnb-tools submission batch-download 98765 --dest ./predictions --status RECEIVED
```

For automated validation pipelines, the `validation_toolkit` module provides
ready-made checks you can use inside your validation scripts. See the
[How-To: Write a Validation Script](validation-toolkit.md) guide for a
working example.

---

## Stage 4: Closing

When the challenge ends, close it to prevent new submissions, lock the
participant team, and update the project status:

```bash
cnb-tools challenge close syn12345
```

---

## Next Steps

- [Cheat Sheet](cheat-sheet.md) — quick-reference tables for all CLI commands and Python API functions
- [CLI Reference](../reference/cli.md) — full documentation for every command and option
- [How-To: Write a Validation Script](validation-toolkit.md) — using the `validation_toolkit` module in your evaluation pipeline