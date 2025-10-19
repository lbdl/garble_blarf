# Developer Guide - GarbleBlarf

This document explains the development workflow, branching strategy, and contribution process for the memo-transcriber project.

## Branch Strategy

This project uses a **dual-branch workflow** to maintain clean separation between production code and development tools.

### Branch Overview

| Branch | Purpose | Contains |
|--------|---------|----------|
| **`main`** | Production releases | Production code only (NO `dev_tools/`) |
| **`dev`** | Active development | Production code + `dev_tools/` directory |

**Key principle:** What's in `main` is exactly what ships to users. No development-only code, no exceptions.

### Branch Details

#### `main` - Production Branch
- **Purpose:** Clean, shippable code for releases
- **Contents:** All production modules (15 .py files)
- **Does NOT contain:** `dev_tools/` directory
- **Protected by:** `.gitattributes` prevents `dev_tools/` from merging in
- **When to use:** Release tagging, hotfixes
- **Default branch:** Yes (users clone this by default)

#### `dev` - Development Branch
- **Purpose:** Day-to-day development with full tooling
- **Contents:** All production code + development tools
- **Contains:** `dev_tools/` directory with internal commands
- **When to use:** Feature development, experiments, testing
- **pyproject.toml:** Keeps `dev_tools/**` exclusion for safety

## Standard Workflows

### 1. Feature Development

```bash
# Start from dev branch
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/my-feature-name

# Make your changes
# ... edit files ...
git add .
git commit -m "Add my feature"

# Push and create PR
git push -u origin feature/my-feature-name
# Open PR: feature/my-feature-name → dev
```

**Always branch from `dev`, never from `main`.**

### 2. Release Workflow

```bash
# 1. Bump version on dev
git checkout dev
# Edit pyproject.toml: version = "0.2.0"
git commit -m "Bump version to 0.2.0"
git push origin dev

# 2. Merge to main
git checkout main
git pull origin main
git merge dev
# .gitattributes automatically excludes dev_tools - no conflicts!

# 3. Tag the release on main
git push origin main
git tag v0.2.0
git push origin v0.2.0

# 4. Build and publish (if releasing to PyPI)
# python -m build
# twine upload dist/*
```

**Key points:**
- Version bumps happen on `dev`
- Tags are created on `main` (tags = releases)
- `.gitattributes` prevents `dev_tools/` from merging

### 3. Hotfix Workflow

**Scenario:** Critical bug found in production that needs immediate fix.

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-description

# 2. Fix the bug
# ... make fixes ...
git commit -m "Fix critical bug in production"

# 3. Merge into main and tag
git checkout main
git merge hotfix/critical-bug-description
git tag v0.1.1  # Patch version bump
git push origin main v0.1.1

# 4. Sync back to dev (important!)
git checkout dev
git merge main  # Brings hotfix into dev
git push origin dev

# 5. Clean up
git branch -d hotfix/critical-bug-description
```

**Why this approach:**
- Fast path to production (fix on main directly)
- Simple sync (merge `main` → `dev`)
- No risk of forgetting to sync (just merge, no cherry-picking)

## Git Attributes Merge Protection

The `.gitattributes` file on `main` contains:

```
src/memo_transcriber/dev_tools/** merge=ours
```

**What this does:**
- When merging `dev` → `main`, Git uses the "ours" strategy for `dev_tools/`
- "ours" = keep `main`'s version (which is deleted)
- Result: `dev_tools/` never accidentally merges into `main`

**Important note:** If you modify files in `dev_tools/` on dev and merge to main, you may see a "modify/delete" conflict. Simply resolve with:

```bash
git rm src/memo_transcriber/dev_tools/<filename>
```

This keeps it deleted on `main`, which is correct.

## Version Bumping

**Strategy:** Bump on `dev`, tag on `main`

### Semantic Versioning

Follow [semver](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes (0.x.x → 1.0.0)
- **MINOR:** New features, backwards compatible (0.1.x → 0.2.0)
- **PATCH:** Bug fixes, backwards compatible (0.1.0 → 0.1.1)

### How to Bump Version

1. **On dev:** Edit `pyproject.toml` version field
2. **Commit:** `git commit -m "Bump version to X.Y.Z"`
3. **Merge to main:** Follow release workflow above
4. **Tag on main:** `git tag vX.Y.Z`

**Why tag on main?**
- Tags represent releases
- Releases happen from `main` (production branch)
- GitHub releases are created from tags on main
- Clear: tag creation = shipped to users

## pyproject.toml Exclusions

**On `main`:**
```toml
exclude = [
    "test_*.db",
    "*.db-journal",
    ".dev"
]
```
No `dev_tools/**` exclusion needed since directory doesn't exist.

**On `dev`:**
```toml
exclude = [
    "src/memo_transcriber/dev_tools/**",  # ← Kept for safety
    "test_*.db",
    "*.db-journal",
    ".dev"
]
```
Keeps exclusion in case dev_tools accidentally get added during development.

## Common Tasks

### Switching Between Branches

```bash
# Work on dev (with dev_tools)
git checkout dev
ls src/memo_transcriber/dev_tools/  # ✅ Exists

# Check production state
git checkout main
ls src/memo_transcriber/dev_tools/  # ❌ Does not exist
```

### Testing Build Locally

```bash
# On main branch (what ships)
git checkout main
python -m build
ls dist/  # Check wheel contents

# Verify dev_tools NOT in wheel
unzip -l dist/memo_transcriber-*.whl | grep dev_tools
# Should return nothing
```

### Checking Which Branch You're On

```bash
git branch  # * shows current branch
git status  # First line shows branch name
```

## Development Tools (dev_tools/)

The `dev_tools/` directory contains internal debugging and development commands that are **NOT** shipped to users.

**Location:** `src/memo_transcriber/dev_tools/`

**Contains:**
- `dev_commands.py` - Internal CLI commands for debugging
- `__init__.py` - Package marker with documentation

**Only available:**
- On `dev` branch
- When developing from source
- When running `uv pip install -e ".[dev]"`

**Never available:**
- On `main` branch
- In published wheel/sdist
- To end users

## Troubleshooting

### "I accidentally committed dev_tools to main"

```bash
git checkout main
git rm -r src/memo_transcriber/dev_tools/
git commit -m "Remove dev_tools from main"
git push origin main
```

### "My merge from dev → main has conflicts"

If you see conflicts in `dev_tools/`:

```bash
# Keep main's version (deleted)
git rm src/memo_transcriber/dev_tools/<conflicted-file>
git commit
```

### "I want to test a feature without switching branches"

```bash
# Use git worktrees (advanced)
git worktree add ../memo-transcriber-dev dev
cd ../memo-transcriber-dev
# Work here without affecting main worktree
```

## Quick Reference

| Task | Command |
|------|---------|
| Start feature | `git checkout dev && git checkout -b feature/name` |
| Release version | `git checkout main && git merge dev && git tag vX.Y.Z` |
| Hotfix | `git checkout main && git checkout -b hotfix/name` |
| Sync hotfix to dev | `git checkout dev && git merge main` |
| Check current branch | `git branch` or `git status` |
| Verify dev_tools | `ls src/memo_transcriber/dev_tools/` |

## Resources

- **Full migration details:** See `branch_refactor.md`
- **Project overview:** See `.claude/context.md`
- **User documentation:** See `README.md`
- **CLI help:** Run `memo-transcriber --help` or `comparator --help`

---

**Questions?** Open an issue on GitHub or check the project wiki.

**Last updated:** 2025-10-19
