---
name: release-skills
description: Universal release workflow. Auto-detects version files and changelogs. Supports Node.js, Python, Rust, Claude Plugin, and generic projects. MUST run before every git commit to update CHANGELOG.md. Use when user says "release", "发布", "new version", "bump version", "push", "推送", "commit", "提交".
---

# Release Skills

Universal release workflow supporting any project type.

## Quick Start

Just run `/release-skills` - auto-detects your project configuration.

## Supported Projects

| Project Type | Version File | Auto-Detected |
|--------------|--------------|---------------|
| Node.js | package.json | ✓ |
| Python | pyproject.toml | ✓ |
| Rust | Cargo.toml | ✓ |
| Claude Plugin | marketplace.json | ✓ |
| Generic | VERSION / version.txt | ✓ |

## Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without executing |
| `--major` | Force major version bump |
| `--minor` | Force minor version bump |
| `--patch` | Force patch version bump |

## Workflow

### Step 1: Detect Project Configuration

1. Check for `.releaserc.yml` (optional config override)
2. Auto-detect version file by scanning (priority order):
   - `package.json` (Node.js)
   - `pyproject.toml` (Python)
   - `Cargo.toml` (Rust)
   - `marketplace.json` or `.claude-plugin/marketplace.json` (Claude Plugin)
   - `VERSION` or `version.txt` (Generic)
3. Scan for changelog file: `CHANGELOG.md`
4. Display detected configuration

**Output Example**:
```
Project detected:
  Version file: package.json (1.2.3)
  Changelog: CHANGELOG.md
```

### Step 2: Analyze Changes Since Last Tag

```bash
LAST_TAG=$(git tag --sort=-v:refname | head -1)
git log ${LAST_TAG}..HEAD --oneline
git diff ${LAST_TAG}..HEAD --stat
```

Categorize by conventional commit types:

| Type | Description |
|------|-------------|
| feat | New features |
| fix | Bug fixes |
| docs | Documentation |
| refactor | Code refactoring |
| perf | Performance improvements |
| test | Test changes |
| style | Formatting, styling |
| chore | Maintenance (skip in changelog) |

**Breaking Change Detection**:
- Commit message starts with `BREAKING CHANGE`
- Commit body/footer contains `BREAKING CHANGE:`
- Removed public APIs, renamed exports, changed interfaces

If breaking changes detected, warn user: "Breaking changes detected. Consider major version bump (--major flag)."

### Step 3: Determine Version Bump

Rules (in priority order):
1. User flag `--major/--minor/--patch` → Use specified
2. BREAKING CHANGE detected → Major bump (1.x.x → 2.0.0)
3. `feat:` commits present → Minor bump (1.2.x → 1.3.0)
4. Otherwise → Patch bump (1.2.3 → 1.2.4)

Display version change: `1.2.3 → 1.3.0`

### Step 4: Generate Changelog

1. **Detect third-party contributors**:
   - Check merge commits: `git log ${LAST_TAG}..HEAD --merges --pretty=format:"%H %s"`
   - For each merged PR, identify the PR author via `gh pr view <number> --json author --jq '.author.login'`
   - Compare against repo owner (`gh repo view --json owner --jq '.owner.login'`)
   - If PR author ≠ repo owner → third-party contributor
2. **Generate content**:
   - Date format: YYYY-MM-DD
   - **Third-party contributions**: Append contributor attribution `(by @username)` to the changelog entry
3. **Insert at file head** (preserve existing content)

**Changelog Format**:

```markdown
## {VERSION} - {YYYY-MM-DD}

### Features
- Description of new feature
- Description of third-party contribution (by @username)

### Fixes
- Description of fix

### Documentation
- Description of docs changes
```

Only include sections that have changes. Omit empty sections.

**Third-Party Attribution Rules**:
- Only add `(by @username)` for contributors who are NOT the repo owner
- Use GitHub username with `@` prefix
- Place at the end of the changelog entry line

**Example** (CHANGELOG.md):
```markdown
## 1.3.0 - 2026-01-22

### Features
- Add user authentication module (by @contributor1)
- Support OAuth2 login

### Fixes
- Fix memory leak in connection pool
```

### Step 5: Group Changes by Skill/Module

Analyze commits since last tag and group by affected skill/module:

1. **Identify changed files** per commit
2. **Group by skill/module**:
   - `skills/<skill-name>/*` → Group under that skill
   - Root files (CLAUDE.md, etc.) → Group as "project"
   - Multiple skills in one commit → Split into multiple groups
3. **For each group**, identify related README updates needed

**Example Grouping**:
```
cover-image:
  - feat: add new style options
  - fix: handle transparent backgrounds
  → README updates: options table

comic:
  - refactor: improve panel layout algorithm
  → No README updates needed

project:
  - docs: update CLAUDE.md architecture section
```

### Step 6: Commit Each Skill/Module Separately

For each skill/module group (in order of changes):

1. **Check README updates needed**:
   - Scan `README.md` for mentions of this skill/module
   - Verify options/flags documented correctly
   - Update usage examples if syntax changed
   - Update feature descriptions if behavior changed

2. **Stage and commit**:
   ```bash
   git add skills/<skill-name>/*
   git add README.md  # If updated for this skill
   git commit -m "<type>(<skill-name>): <meaningful description>"
   ```

3. **Commit message format**:
   - Use conventional commit format: `<type>(<scope>): <description>`
   - `<type>`: feat, fix, refactor, docs, perf, etc.
   - `<scope>`: skill name or "project"
   - `<description>`: Clear, meaningful description of changes

**Example Commits**:
```bash
git commit -m "feat(cover-image): add watercolor and minimalist styles"
git commit -m "fix(comic): improve panel layout for long dialogues"
git commit -m "docs(project): update architecture documentation"
```

**Common README Updates Needed**:
| Change Type | README Section to Check |
|-------------|------------------------|
| New options/flags | Options table, usage examples |
| Renamed options | Options table, usage examples |
| New features | Feature description, examples |
| Breaking changes | Migration notes, deprecation warnings |
| Restructured internals | Architecture section (if exposed to users) |

### Step 7: Generate Changelog and Update Version

1. **Generate changelog** (as described in Step 4)
2. **Update version file**:
   - Read version file (JSON/TOML/text)
   - Update version number
   - Write back (preserve formatting)

**Version Paths by File Type**:

| File | Path |
|------|------|
| package.json | `$.version` |
| pyproject.toml | `project.version` |
| Cargo.toml | `package.version` |
| marketplace.json | `$.metadata.version` |
| VERSION / version.txt | Direct content |

### Step 8: User Confirmation

Before creating the release commit, ask user to confirm:

**Use AskUserQuestion with two questions**:

1. **Version bump** (single select):
   - Show recommended version based on Step 3 analysis
   - Options: recommended (with label), other semver options
   - Example: `1.2.3 → 1.3.0 (Recommended)`, `1.2.3 → 1.2.4`, `1.2.3 → 2.0.0`

2. **Push to remote** (single select):
   - Options: "Yes, push after commit", "No, keep local only"

**Example Output Before Confirmation**:
```
Commits created:
  1. feat(cover-image): add watercolor and minimalist styles
  2. fix(comic): improve panel layout for long dialogues
  3. docs(project): update architecture documentation

Changelog preview:
  ## 1.3.0 - 2026-01-22
  ### Features
  - Add watercolor and minimalist styles to cover-image
  ### Fixes
  - Improve panel layout for long dialogues in comic

Ready to create release commit and tag.
```

### Step 9: Create Release Commit and Tag

After user confirmation:

1. **Stage version and changelog file**:
   ```bash
   git add <version-file>
   git add CHANGELOG.md
   ```

2. **Create release commit**:
   ```bash
   git commit -m "chore: release v{VERSION}"
   ```

3. **Create tag**:
   ```bash
   git tag v{VERSION}
   ```

4. **Push if user confirmed** (Step 8):
   ```bash
   git push origin main
   git push origin v{VERSION}
   ```

**Note**: Do NOT add Co-Authored-By line. This is a release commit, not a code contribution.

**Post-Release Output**:
```
Release v1.3.0 created.

Commits:
  1. feat(cover-image): add watercolor and minimalist styles
  2. fix(comic): improve panel layout for long dialogues
  3. docs(project): update architecture documentation
  4. chore: release v1.3.0

Tag: v1.3.0
Status: Pushed to origin  # or "Local only - run git push when ready"
```

## Configuration (.releaserc.yml)

Optional config file in project root to override defaults:

```yaml
# .releaserc.yml - Optional configuration

# Version file (auto-detected if not specified)
version:
  file: package.json
  path: $.version  # JSONPath for JSON, dotted path for TOML

# Changelog file (auto-detected if not specified)
changelog:
  file: CHANGELOG.md

  # Section mapping (conventional commit type → changelog section)
  # Use null to skip a type in changelog
  sections:
    feat: Features
    fix: Fixes
    docs: Documentation
    refactor: Refactor
    perf: Performance
    test: Tests
    chore: null

# Commit message format
commit:
  message: "chore: release v{version}"

# Tag format
tag:
  prefix: v  # Results in v1.0.0
  sign: false

# Additional files to include in release commit
include:
  - README.md
  - package.json
```

## Dry-Run Mode

When `--dry-run` is specified:

```
=== DRY RUN MODE ===

Project detected:
  Version file: package.json (1.2.3)
  Changelog: CHANGELOG.md

Last tag: v1.2.3
Proposed version: v1.3.0

Changes grouped by skill/module:
  cover-image:
    - feat: add watercolor style
    - feat: add minimalist style
    → Commit: feat(cover-image): add watercolor and minimalist styles
    → README updates: options table

  comic:
    - fix: panel layout for long dialogues
    → Commit: fix(comic): improve panel layout for long dialogues
    → No README updates

Changelog preview:
  ## 1.3.0 - 2026-01-22
  ### Features
  - Add watercolor and minimalist styles to cover-image
  ### Fixes
  - Improve panel layout for long dialogues in comic

Commits to create:
  1. feat(cover-image): add watercolor and minimalist styles
  2. fix(comic): improve panel layout for long dialogues
  3. chore: release v1.3.0

No changes made. Run without --dry-run to execute.
```

## Example Usage

```
/release-skills              # Auto-detect version bump
/release-skills --dry-run    # Preview only
/release-skills --minor      # Force minor bump
/release-skills --patch      # Force patch bump
/release-skills --major      # Force major bump (with confirmation)
```

## When to Use

Trigger this skill when user requests:
- "release", "发布", "create release", "new version", "新版本"
- "bump version", "update version", "更新版本"
- "prepare release"
- "commit", "提交", "git commit"
- "push to remote" (with uncommitted changes)

**Important**:
- Before every git commit, this skill MUST be executed first to update CHANGELOG.md. No commit should be made without an up-to-date changelog.
- If user says "just push", "直接 push", "just commit", or "直接提交" with uncommitted changes, STILL follow all steps above first.
