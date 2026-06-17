---
name: release
description: 'Prepare and publish a new cnb-tools release. USE FOR: user says "release", "cut a release", "new version", or "release prep". PERFORMS: determines next SemVer, creates release-prep/<version> branch, bumps version in pyproject.toml, upgrades synapseclient to latest and updates its minimum pin, updates changelog, runs uv lock, commits and pushes, then guides the user to open a PR, merge, and publish the GitHub release.'
argument-hint: 'Target version (e.g. 0.5.0). Omit to auto-determine from changelog.'
---

# cnb-tools Release Process

## Versioning Rules (SemVer)

| Change type | Bump |
|---|---|
| Breaking API changes | **major** (x.0.0) |
| New CLI commands or public functions | **minor** (0.x.0) |
| Bug fixes, refactors, docs only | **patch** (0.0.x) |

## Steps

### 1. Confirm starting state
```bash
git branch --show-current   # must be main
git log --oneline -5
```

### 2. Determine next version
- Read current version from `pyproject.toml`
- Read `docs/changelog/release-notes.md` → `## In development` section
- Apply versioning rules → `<next>`

### 3. Create release branch
```bash
git checkout -b release-prep/<next>
```

### 4. Upgrade synapseclient to latest (minor/patch only)
```bash
uv lock --upgrade-package synapseclient
```
Read the current pin from `pyproject.toml` and the resolved version from `uv.lock` (search for `name = "synapseclient"`).

- If the resolved version is a **major** bump (e.g. `4.x.x` → `5.x.x`): revert with `uv lock` (no `--upgrade-package`) and do **not** change the pin — flag this to the user for manual review.
- Otherwise: update the minimum pin in `pyproject.toml` to match:
```toml
"synapseclient>=<resolved-version>",
```

### 5. Edit files

**`pyproject.toml`** — bump `version`:
```toml
version = "<next>"
```

**`docs/changelog/release-notes.md`** — rename `## In development` → `## <next>`. Fill in any missing entries. Omit empty subsections. Order: Features → Bug fixes → Docs.

### 6. Commit and push
```bash
git add pyproject.toml uv.lock docs/changelog/release-notes.md
git commit -m "release prep/<next>"
git push -u origin release-prep/<next>
```

### 7. Open PR and merge
If `gh` CLI is available:
```bash
gh pr create --title "Release prep/<next>" --body "" --base main
gh pr merge --merge release-prep/<next>
```
Otherwise provide this URL and ask the user to open it, create the PR, and merge:
`https://github.com/Sage-Bionetworks-Challenges/cnb-tools/compare/release-prep/<next>`

### 8. Create GitHub release
Ask the user to:
1. Go to **Releases → Draft a new release**
2. Set tag: `v<next>`
3. Click **"Generate release notes"** → Publish

## Constraints
- Never push directly to `main`
- Always commit `uv.lock` alongside any `pyproject.toml` change
