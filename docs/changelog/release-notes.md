## In development

### Features
- CLI
   * Annotate submission: `submission annotate <submission ID> <filepath to JSON file>`
   * Download submission: `submission download <submission ID> --dest`
   * Delete one or more submissions: `submission delete [--force] <submission ID 1> <submission ID 2> ...`
   * Get information about submission: `submission info <submission ID>`
   * Update submission status: `submission update-status <submission ID> <new status>`

- Package
   * New class: `Submission`

### Docs
- add [Termynal plug-in](https://github.com/mkdocs-plugins/termynal)
- mention using a Python environment before installing

## 0.1.1

* Add Dockerfile for GH package.
* Add CI workflow to deploy image on ghcr.io.

## 0.1.0

* First commit. Prepare for PyPI publishing.
* Add initial version of code, docs, etc.
* Add CI workflows and templates.
