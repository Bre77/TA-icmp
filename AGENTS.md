# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- This app runs on `splunk_input_runtime` (https://github.com/Bre77/splunk-input-runtime), not `splunklib`/`splunk-sdk`. `lib/requirements.txt` pins it to an exact commit archive URL with a `sha256:` hash recorded in a comment above it (no PyPI package exists yet, so there is no `==version` line to pin against). Bump both the commit and the recorded hash together when the runtime releases a new version; never point at a branch.
- This app has no credential/account surface: it never touches `storage/passwords` and never used `Script.service` for anything beyond a no-op namespace assignment, which was deleted in the migration. There is nothing to strand on upgrade and no credential-continuity gate is needed here.
- `.build.sh` vendors `lib/` fresh on every build (`pip install -t lib -r lib/requirements.txt --no-dependencies`); `lib/` is gitignored except `lib/requirements.txt`. Do not commit vendored packages into `lib/` - an old vendored `lib/splunklib/` and `lib/icmplib/` tree was committed by mistake early in this repo's history and removed as part of the `splunk_input_runtime` migration.
- The runner owns `EventWriter.close()`; app code must not call it explicitly. `splunk_input_runtime`'s `close()` is idempotent by design regardless.
- `Bre77/SplunkUI-devcontainer`'s `test-harness/verify-splunklib-app.sh` is app-agnostic - point it at this repo to get a `dependency=splunk_input_runtime` build+import check on both Python 3.9 and 3.13.
- Version is recorded in three places that must stay in sync: `package.json` and both `version =` lines in `default/app.conf` (`[launcher]` and `[id]`). A mismatch fails AppInspect.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
