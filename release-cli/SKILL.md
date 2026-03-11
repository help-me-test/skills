---
name: release-cli
description: >
  Full HelpMeTest CLI release pipeline. Use when the user says "release cli",
  "ship cli", "publish cli", "new cli version", or "release the CLI". Covers
  everything from version bump through GitHub workflow monitoring and live
  installation verification. Always use this skill — do not try to do a CLI
  release manually step by step.
---

# CLI Release

Execute every step in order. Do not skip verification steps — a release is not done until `helpmetest --version` confirms the new version.

## Step 0: Commit any uncommitted work in `cli/`

Check for uncommitted files in `./cli`:

```bash
cd cli && git status
```

If there are uncommitted changes, commit them following the conventions in `@prompts/commit.md` before proceeding. The release commit must be on top of a clean working tree.

## Step 1: Find the latest PUBLISHED release

Git tags and GitHub Releases are not the same — a tag can exist without the CI ever building and publishing the release. Always base your version bump on the last successfully *published* release, not just the last git tag.

```bash
cd cli
gh release list --limit 5
```

This shows the actual published releases. The latest one (status `Latest`) is the baseline for your version bump. If a tag exists locally that has no corresponding GitHub Release, skip it.

Also cross-check what version the live installer actually serves:

```bash
curl -s https://helpmetest.com/install/version 2>/dev/null || echo "(endpoint not available)"
```

Use whichever of `gh release list` or the live version is more recent as the true baseline.

## Step 2: Analyze commits and determine version bump

```bash
cd cli
git log <last-published-tag>..HEAD --oneline
```

Decide the bump type by reading every commit since the last PUBLISHED release:
- **MAJOR** — breaking API changes (rare)
- **MINOR** — any new feature or capability added (`✨` commits)
- **PATCH** — bug fixes only (`🐛`, `🩹` commits)

When in doubt: if there's even one `✨` commit, it's MINOR.

## Step 3: Update `cli/package.json`

Bump `"version"` to the new semver string. This is the single source of truth for the version.

## Step 4: Update `cli/RELEASE_NOTES.md`

Add a new section at the top (below the `# Release Notes` heading):

```
## vX.Y.Z (YYYY-MM-DD)

### New Features       ← only if any
### Improvements       ← only if any
### Bug Fixes          ← only if any
```

Write every entry from the **customer's perspective** — what value they get, not what code changed. Rewrite commit messages into plain English. Example:

- Commit: `🐛 mcp->interactive: Unregister session on Exit`
- Release note: `**Interactive Session Cleanup**: Fixed a bug where interactive debugging sessions were not properly cleaned up after closing, preventing stale room names from appearing in subsequent sessions.`

## Step 5: Commit and tag

```bash
cd cli
git add package.json RELEASE_NOTES.md
git commit -m "🔖 Release vX.Y.Z"
git tag vX.Y.Z
```

Note: use `v` prefix on the tag (e.g. `v1.37.0`), not on the package.json version string.

## Step 6: Push commit and tags

```bash
cd cli
git push && git push --tags
```

Ask the user to confirm before pushing if there's any uncertainty about the version number chosen.

## Step 7: Monitor the GitHub Actions workflow

```bash
cd cli
sleep 5
gh run list --limit 1
```

If the run is `in_progress`, wait and re-check:

```bash
sleep 60
gh run list --limit 1
```

If it fails, inspect the logs:

```bash
gh run view <run-id> --log-failed
```

**Known expected failure**: The workflow may fail on "Restart installer deployment" with a `Forbidden` error — this is a known namespace permission issue and is safe to ignore. Proceed to step 8.

**Known failure — artifact storage quota**: The `Upload binaries` step may fail with "Artifact storage quota has been hit." GitHub recalculates usage every 6-12 hours, so deleting artifacts and re-running won't help immediately. **Fall back to building and publishing locally instead:**

```bash
cd cli

# Build all platform binaries (bun cross-compiles from macOS)
./build.sh

# Publish to both GitHub repos
GITHUB_TOKEN=<token-from-workflow-file> ./publish.sh
```

The `GITHUB_TOKEN` value is in `.github/workflows/build-release.yml`. This produces the same result as CI — all 8 platform binaries published to both `help-me-test/cli-code` and `help-me-test/cli`. Note: macOS `.pkg` installers won't be rebuilt (requires Apple signing secrets) — existing ones from a previous release will be attached instead.

If the failure is unexpected (build error, test failure, etc.), stop and investigate before continuing.

## Step 8: Clear the installer cache

```bash
curl https://helpmetest.com/install/clearcache
```

This endpoint clears the cached GitHub release data so the installer picks up the new binaries immediately.

**Important**: Use `helpmetest.com/install/clearcache`, NOT `installer.helpmetest.com`.

## Step 9: Verify the release

```bash
curl -fsSL https://helpmetest.com/install.sh | bash
helpmetest --version
```

Expected output: `X.Y.Z` (the version you just released, without the `v` prefix).

If the version is wrong:
1. Check tags were pushed: `cd cli && git tag -l | grep vX.Y.Z`
2. Check installer pods: `kubectl-hetzner1 get pods -n helpmetest -l app=installer`
3. Check installer logs: `kubectl-hetzner1 logs -n helpmetest deployment/installer`
4. Re-run: `curl https://helpmetest.com/install/clearcache` and wait 2-3 minutes

## Step 10: Smoke test key commands

```bash
helpmetest status
timeout 2 helpmetest mcp --verbose || true
```

If these work without errors, the release is complete. Report the version shipped to the user.
