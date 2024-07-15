## In development

### Features
- Add new CLI command: `cnb-tools challenge SUBCOMMAND`

### Docs
- Add How-To tutorial on how the Validation Toolkit can be used

### Bug fixes
- Remove custom classes, as to prevent future confusion with synapseclient's classes

## 0.3.2

### Bug fixes
- Replace `|` with `typing.Union` for type-hinting in order to be compatible with Python 3.9

## 0.3.1

### Bug fixes
- Fix Docker image deployment ([#30](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/30))

## 0.3.0

### Features
- Add new module: validation_toolkit ([#26](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/26))

### Bug fixes
- Handle use case when there is one or more unknown submission IDs in given list ([#23](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/23))

## 0.2.0

### Features
- Add new CLI command: `cnb-tools submission SUBCOMMAND` ([#14](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/14), [#19](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/19))

### Docs
- Add Termynal plug-in ([#10](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/10))

### Internal
- Dependency version bump ([#18](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/18))
- General CI workflow updates ([#11](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/11), [#13](https://github.com/Sage-Bionetworks-Challenges/cnb-tools/pull/13))

## 0.1.1

- Add Dockerfile for GH package.
- Add CI workflow to deploy image on ghcr.io.

## 0.1.0

- First commit. Prepare for PyPI publishing.
- Add initial version of code, docs, etc.
- Add CI workflows and templates.
