# Branch Refactoring Plan

## Executive Summary

**DECISIONS MADE:**
- ✅ **Dual Branch Strategy** - `main` (production only), `dev` (full development environment)
- ✅ **Hotfix Approach** - Default to Option 3 (reverse merge: fix on `main`, merge to `dev`)
- ✅ **Dev Tools** - Physically removed from `main`, kept on `dev`
- ✅ **Merge Protection** - `.gitattributes` prevents dev_tools from merging `dev` → `main`
- ✅ **pyproject.toml** - Remove exclusion on `main` (not needed), keep on `dev` (safety)
- ✅ **Default Branch** - Keep `main` as GitHub default (industry standard)
- ✅ **Version Bumping** - Bump on `dev`, merge to `main`, tag on `main` (tags = releases)

**Key Benefits:**
- Clean production branch (what you see is what ships)
- Automated merge protection via `.gitattributes`
- Simple hotfix workflow (merge `main` → `dev` to sync)
- Zero risk of dev_tools leaking into production

## Current State

- **Branch:** `main` (single branch)
- **dev_tools Status:** Present in repository, excluded from wheel via `pyproject.toml`
- **Build Exclusion:** `exclude = ["src/memo_transcriber/dev_tools/**"]`
- **Git Status:** Clean working tree

## Proposed Branch Structure

### `main` - Production Branch
- **Purpose:** Clean production code only
- **Contents:**
  - All production modules (15 .py files)
  - No `dev_tools/` directory physically present
  - Ready for PyPI publishing
- **Merge Strategy:** Only merge from `dev` via PR after feature completion
- **Protection:** Should be the default branch for releases

### `dev` - Development Branch
- **Purpose:** Active development with full tooling
- **Contents:**
  - All production modules
  - `dev_tools/` directory with development commands
  - Testing infrastructure
- **Merge Strategy:** Feature branches merge into `dev`, then `dev` → `main` for releases
- **Workflow:** Day-to-day development happens here

## Migration Steps

### Phase 1: Create Dev Branch (Preserve Current State)
```bash
# Create dev branch from current main (contains dev_tools)
git checkout -b dev
git push -u origin dev

# Verify dev_tools exists
ls -la src/memo_transcriber/dev_tools/
```

### Phase 2: Clean Main Branch (Remove Dev Tools)
```bash
# Switch back to main
git checkout main

# Remove dev_tools directory
git rm -r src/memo_transcriber/dev_tools/

# Remove dev_tools exclusion from pyproject.toml (no longer needed on main)
# Edit pyproject.toml and remove the line: exclude = ["src/memo_transcriber/dev_tools/**"]
# (or use Edit tool if running this with Claude Code)

# Commit removal
git commit -m "Remove dev_tools from production branch

Development tools moved to dev branch for separation of concerns.
Production branch contains only shippable code.
Removed pyproject.toml exclusion since dev_tools no longer exists here.

See: branch_refactor.md for migration details"

# Push cleaned main
git push origin main
```

### Phase 3: Configure Git Attributes (Prevent Auto-Merge)
```bash
# Switch to main branch
git checkout main

# Create/update .gitattributes to prevent dev_tools from merging
cat >> .gitattributes <<'EOF'
# Prevent dev_tools from being merged into main branch
src/memo_transcriber/dev_tools/** merge=ours
EOF

# Configure the 'ours' merge driver (keeps main's version, i.e., deleted)
git config merge.ours.driver true

# Commit the gitattributes change
git commit -am "Configure git attributes to block dev_tools merges

Prevents dev_tools/ from being merged from dev → main.
Uses 'ours' merge strategy to keep main's version (deleted)."

git push origin main
```

**What this does:** When merging from `dev` to `main`, any changes to `src/memo_transcriber/dev_tools/**` will be ignored, keeping main's version (which doesn't have dev_tools). This prevents conflicts and accidental inclusion.

### Phase 4: Verify Separation
```bash
# On main - should NOT have dev_tools
git checkout main
ls src/memo_transcriber/dev_tools/  # Should fail
cat .gitattributes  # Should show merge=ours rule

# On dev - should HAVE dev_tools
git checkout dev
ls src/memo_transcriber/dev_tools/  # Should succeed
cat .gitattributes  # May or may not have the rule (optional on dev)

# Test the merge protection
git checkout main
git merge dev --no-commit --no-ff
git status  # dev_tools should NOT appear in staged changes
git merge --abort  # Clean up test merge
```


## Git Attributes Merge Strategy

### How It Works

**`.gitattributes` entry on main branch:**
```
src/memo_transcriber/dev_tools/** merge=ours
```

**Git config:**
```bash
git config merge.ours.driver true
```

**Behavior:**
- When merging from `dev` → `main`, Git sees changes to files matching `src/memo_transcriber/dev_tools/**`
- The `merge=ours` strategy tells Git: "Keep our version (main's version)"
- Since main doesn't have these files, they stay deleted
- No conflicts, no manual intervention, no accidental inclusion

**Benefits:**
- ✅ Automatic - no manual conflict resolution
- ✅ Safe - impossible to accidentally merge dev_tools into main
- ✅ Simple - one-time setup, works forever
- ✅ Per-path - only affects dev_tools, other files merge normally

**Note:** The `.gitattributes` file only needs to exist on `main`. It can optionally exist on `dev` but has no effect there.

## Considerations & Tradeoffs

### ✅ Benefits
1. **Clear Separation:** Production code is physically separated from dev tools
2. **Cleaner Main:** No need for pyproject.toml exclusions
3. **Release Confidence:** What's in main is exactly what ships
4. **Git History:** Clear distinction between feature development and releases
5. **Automated Protection:** `.gitattributes` prevents dev_tools from accidentally merging into main
6. **Zero Manual Intervention:** Merges from dev → main "just work" without conflict resolution

## Standard Workflows

### Version Bumping Strategy

**Workflow:**
1. **Bump version on `dev`** - Edit `pyproject.toml`, commit version change
2. **Merge `dev` → `main`** - Brings version bump to production
3. **Tag on `main`** - Create release tag on main after merge
4. **Push everything** - `git push origin main --tags`

**Example:**
```bash
# On dev: bump version
git checkout dev
# Edit pyproject.toml: version = "0.2.0"
git commit -m "Bump version to 0.2.0"
git push origin dev

# Merge to main
git checkout main
git merge dev
git push origin main

# Tag the release on main
git tag v0.2.0
git push origin v0.2.0
```

**Why this approach:**
- Version bumps happen during development (on dev)
- Tags represent releases (created on main)
- Both branches have same version in `pyproject.toml` after merge
- Tags are visible from both branches (point to same commit SHA)
- Clear: tag creation = release to production

### Feature Development Workflow

```bash
# Always branch from dev for new features
git checkout dev
git pull origin dev
git checkout -b feature/new-feature

# ... make changes ...
git commit -m "Add new feature"
git push -u origin feature/new-feature

# PR: feature/new-feature → dev
```

### Release Workflow

```bash
# When ready to release
git checkout dev
git pull origin dev

# Merge dev into main (.gitattributes automatically excludes dev_tools)
git checkout main
git pull origin main
git merge dev

# No conflicts for dev_tools - gitattributes handles it automatically!
# Review changes (should be production code only)
git diff HEAD~1

# Push release
git push origin main
git tag v0.2.0
git push origin v0.2.0
```

### Hotfix Workflow

**Scenario:** Critical bug found in production (main) that needs immediate fix.

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug
# ... fix the bug ...
git commit -m "Fix critical bug in production"

# Merge into main and tag
git checkout main
git merge hotfix/critical-bug
git tag v0.1.1
git push origin main v0.1.1

# Merge main back into dev (reverse of normal flow)
git checkout dev
git merge main  # Brings hotfix into dev
git push origin dev

# Clean up
git branch -d hotfix/critical-bug
```

**Why this approach:**
- Simplest sync (just merge main → dev), no cherry-picking
- No risk of forgetting to sync back
- Clean merge without complications
- Fast path to production

## Implementation Checklist

### Decisions ✅
- [x] Dual branch strategy (main = production, dev = development)
- [x] Hotfix via reverse merge (main → dev)
- [x] Remove pyproject.toml exclusion on main, keep on dev
- [x] Keep main as GitHub default branch
- [x] Bump versions on dev, tag releases on main

### Execution Steps
1. [ ] Execute Phase 1: Create dev branch (preserve current state)
2. [ ] Execute Phase 2: Clean main branch (remove dev_tools + pyproject exclusion)
3. [ ] Execute Phase 3: Configure .gitattributes on main
4. [ ] Execute Phase 4: Verify separation and test merge protection
5. [ ] Update README.md with new branching strategy
6. [ ] Update .claude/context.md with new workflow
7. [ ] Set up branch protection rules on GitHub (if applicable)
8. [ ] Test full workflow: feature branch → dev → main

---

*Created: 2025-10-19*
*Updated: 2025-10-19*
*Status: ✅ **APPROVED - Ready for execution***
