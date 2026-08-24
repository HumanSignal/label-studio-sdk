# Migrating in-flight projects between environments

Moving annotation projects that are partway through their work from one Label Studio Enterprise environment to another, without losing completed work, without re-serving finished tasks, and without disturbing anything already present in the target. Throughout, **source** is the environment the projects are leaving and **target** is the environment they are arriving in.

The migration itself is done by `migrate-ls-to-ls.py`, which ships with the Label Studio SDK. This runbook is mostly about everything that script does not do.

## 1. When to use this runbook

Use it when the target environment is in service and cannot be wiped. Every step here is additive: projects are recreated in the target and populated with the exported work, and nothing already present in the target is modified or removed.

If the target is empty and can be replaced wholesale, a full environment clone is a simpler option and preserves more, including review history and in-progress drafts. Confirm which situation applies before going further, because it changes the approach entirely.

It assumes:

- Both environments run the same product version, target at or above source.
- Both are quiesced for the length of the maintenance window: no annotation activity in either, no configuration changes, and identity provider synchronisation paused against both.
- SCIM provisioning is configured against both environments from the same identity provider, so users, organization roles, workspaces and group membership arrive in the target automatically and match the source.
- Task media is referenced from the same storage location for both environments. Section 6.3 covers what changes if it is not.

## 2. The tooling

All three scripts live in this directory.

| Script | What it does |
|---|---|
| `migrate-ls-to-ls.py` | Exports each source project and recreates it on the target with its tasks, annotations and authorship. Writes `project_mapping.json`, old project id to new. |
| `preflight_check.py` | Before: verifies every annotation author exists in the target and records the counts to validate against. After: re-reads the migrated projects and compares them to those counts. |
| `copy_project_settings.py` | Copies the enterprise project settings the migration leaves behind, and rebuilds per-task completion state. Driven by `project_mapping.json`. |

`migrate-ls-to-ls.py` is used as shipped. Section 6.2 describes the one edit worth making, and why you may not need it.

## 3. What the migration carries, and what it does not

It carries tasks, annotations, their authorship, and a fixed list of thirty core project fields — including the labeling configuration, annotations per task and the overlap cohort percentage.

Everything else is the subject of this runbook: identity, all enterprise project settings, storage connections, project membership, and the SCIM project-level group mappings.

## 4. Parameters to fill in

| Parameter | Value |
|---|---|
| Source environment URL | |
| Target environment URL | |
| Product version, source and target | |
| Projects in scope, by source ID | |
| Destination workspace ID on the target | |
| Storage location, and confirmation the target can reach it | |
| Identity provider, and SCIM applications targeting each environment | |
| Maintenance window, and confirmation that identity provider sync is paused against both environments for its duration | |
| Fallback period before the source is retired | |

## 5. Who does what

| Party | Responsibility |
|---|---|
| Platform administrator | Quiescing both environments, storage access, runs the three scripts, executes the cutover |
| Annotation lead | Freeze communication to annotators, draft clearance, post-cutover sign-off |
| HumanSignal | Pre-flight review, rehearsal support, on call during the window, validation support |

## 6. Pre-flight

### 6.1 Fix the scope

Record the source project IDs. Everything below is per-project, and the scripts all take the same `--project-ids` style list.

Confirm the target has enough seats for the full annotator population. Both environments stay live through the fallback period agreed in step 6.6, so for that whole time the annotators occupy a seat in each.

### 6.2 Identity: SCIM must be 1:1 before anything is imported

**This is the gate that decides whether the migration succeeds or silently corrupts authorship.** Every annotator who has created work in the source projects must already exist in the target organization, under the same address. By default an author who cannot be resolved does not fail the import — the annotation is silently attached to the account performing it — so ask HumanSignal whether the stricter behaviour, which rejects the import instead, can be enabled for the window.

Run the check:

```bash
export LABEL_STUDIO_URL="https://labelstudio-source.internal"
export LABEL_STUDIO_API_KEY="<source access token>"
export DEST_LABEL_STUDIO_URL="https://labelstudio-target.internal"
export DEST_LABEL_STUDIO_API_KEY="<target access token>"

python preflight_check.py --project-ids 12,15,18
```

Every row of `annotator-reconciliation.csv` must read `yes`. Three other statuses can appear:

- **`no`** — the account does not exist in the target. Usually a historical annotator: someone who annotated months ago and has since left the identity provider group. They are no longer a project member, so a member-list check would show no gap, which is why the script derives authors from the annotations themselves. Reinstate the account, or accept that their work will not carry attribution.
- **`case_mismatch`** — an account exists but under different casing. The import matches the address as an exact string, so this reattributes exactly as a missing account would, while looking fine to any case-insensitive check. Align the SCIM attribute mapping, or correct the address on one side.
- **`no_author_detail`** — the annotation came back with no resolvable author at all. Do not migrate that project until it is understood.

**A note on the script's user creation.** `migrate-ls-to-ls.py` creates users on the target as its first act, from the source organization's full user list. If SCIM has already provisioned everyone — which the gate above confirms — those calls are redundant, and the script logs the resulting errors itself as normal. If you would rather it did not attempt them at all, comment out line 151 (`self.create_users(users)`) before running. Either way, do not rely on it to create accounts: it does not set roles, workspace membership or project membership.

Roles and workspace membership are SCIM-driven and should already match. Project-level membership and the SCIM project group mappings are the exceptions, and are handled in Phase 4.

### 6.3 Cloud storage must be reachable, and must never be resynced

Task URIs travel verbatim in the export, so the target needs network egress and credentials to the same paths. Confirm this before the window.

Two rules for the run itself:

- **Leave `DEFAULT_STORAGE` unset.** The migration script has an option to attach a storage connection to each project it creates. It applies one bucket, prefix and regex to *every* project in the run, and then syncs it. Its default is off; leave it off.
- **Never sync storage into a migrated project.** A sync creates a fresh set of storage links and duplicates every task in the project. Connect storage after the import and leave the connection unsynced — see Phase 4.

**If the bucket is changing**, the migration script cannot help: it exports and imports in one pass, with nowhere to rewrite the URIs in between. Either keep the same bucket for the migration and repoint storage afterwards, or run the export and import as separate steps with a rewrite in between. Decide this before the window; it changes the shape of the cutover.

**Media uploaded through the UI rather than referenced from storage will not resolve on the target**, because the underlying files live on the source instance's media volume. Raise this before proceeding — it requires copying the media content and is a materially different job.

### 6.4 Tokens

Both scripts need an Administrator or Owner token on each instance, taken from the Account page (`/user/account`) — the legacy Access token, not a Personal Access Token.

Be careful not to swap the source and target tokens. Nothing prompts for confirmation, and the migration would run in reverse.

### 6.5 Destination workspace

Create the workspace on the target first — one SCIM already provisions — and pass its ID as `--dest-workspace`. Without it the script drops the workspace parameter entirely and the projects land wherever the default puts them.

### 6.6 Agree the windows

Freeze start time, expected duration, and how long the source stays available as a fallback. Agree who pauses identity provider synchronisation against both environments, and confirm it can be held for the full window and resumed after.

Size the window against the largest project. The migration is single-threaded and exports in chunks of 500 tasks; raise `TIMEOUT` (default 600 seconds) for large projects.

### 6.7 Rehearse

Run the full sequence on one representative project, into the live target, then validate and delete the rehearsal project. The rehearsal necessarily runs outside the maintenance window, against a live target, so treat it as a test of the mechanics and the settings rather than of the window itself. Do it far enough ahead that anything it surfaces can be resolved without pressure.

## 7. Cutover

### Phase 0. Freeze

1. Notify annotators in advance of the stop time, and again at the start of the window.
2. Annotators submit or discard anything in progress. Work that has been started but not submitted does not carry over.
3. Stop further annotation in the source by pausing the annotators, or by setting the projects so no labeling can be started. Leave the group mappings alone: membership is the state Phase 4 depends on, and anything changed here has to be put back.

### Phase 1. Baseline

4. Re-run `preflight_check.py` after the freeze. These post-freeze figures, not anything from the pre-flight run, are what you validate against. Because the source is quiesced they are final.

### Phase 2. Migrate

5. Run the migration, one project first:

   ```bash
   python migrate-ls-to-ls.py --project-ids 12 \
       --src-url "$LABEL_STUDIO_URL" --src-key "$LABEL_STUDIO_API_KEY" \
       --dst-url "$DEST_LABEL_STUDIO_URL" --dst-key "$DEST_LABEL_STUDIO_API_KEY" \
       --dest-workspace <workspace-id>
   ```

6. Read the final line of the log. A project whose export fails is skipped, not fatal — the run continues and reports only `N successful and M total` at the end. That line and the log are the completion check.

7. Keep `project_mapping.json`. Phase 3 and Phase 4 both need it, and a later run overwrites entries for the same source project.

8. **If a project fails, delete the target project before retrying.** The script has no idempotency: every run creates new projects, so a retry without cleanup leaves two copies.

### Phase 3. Settings

9. Copy the enterprise settings the migration left behind, previewing first:

   ```bash
   python copy_project_settings.py --dry-run
   python copy_project_settings.py
   ```

   It reads `project_mapping.json`, copies the LseProject settings, review settings and assignment settings from each source project to its new counterpart, and rebuilds per-task completion state. That last step matters: the import marks a task complete by counting distinct authors *including* skipped annotations, so a task holding one submission and one skip from another person imports as already done and is never served again.

10. Read what the script reports as not copied. `agreement_includes_missing_controls` has no API and must be set by hand; the agreement metric fields use a separate endpoint.

### Phase 4. What neither script does

11. **Connect cloud storage, unsynced.** Define the connection on each target project and do not sync it. Tasks are already there.
12. **Re-establish project membership.** Organization membership alone does not distribute tasks.
13. **Rebuild the SCIM project-level group mappings.** They are recorded against a specific project ID, and the target projects are new projects with new IDs, so group membership that granted project-level roles in the source grants nothing in the target. `project_mapping.json` is the old-to-new mapping; reuse the same group names so the intent is unchanged. Workspace and organization-role mappings are unaffected.
14. Let the background queue drain before validating. Each import and each settings change dispatches jobs, and validation run against a moving project produces results that change under you.

### Phase 5. Validate

15. Run the mechanical checks:

    ```bash
    python preflight_check.py --verify project_mapping.json
    ```

    This compares the target against the Phase 1 baseline: task count, annotation count, annotations per annotator, and the spread of tasks by distinct annotator count. A task count below baseline is the signal that the chunked export stopped short.

16. Then the checks a script cannot make:

| # | Check | Method | Pass |
|---|---|---|---|
| 1 | Counts and authorship | `preflight_check.py --verify` reports PASSED | ☐ |
| 2 | Author reattribution | The account that ran the migration holds no annotations in the target beyond any it genuinely authored | ☐ |
| 3 | Distinct annotator rule | Sign in as an annotator who already annotated a partially annotated task, confirm it is not offered to them | ☐ |
| 4 | Distinct annotator rule, positive case | Sign in as an annotator who has not touched that task, confirm it is offered | ☐ |
| 5 | Completed tasks | Confirm 3 tasks at the full annotation count are not offered in any queue | ☐ |
| 6 | Labeling configuration | Compare against the source, and open 3 tasks to confirm annotations render against it | ☐ |
| 7 | Media | Confirm task media loads in those same tasks | ☐ |
| 8 | Settings parity | Spot-check review, assignment and agreement settings against the source | ☐ |
| 9 | Project access | Sign in as a member of each mapped group, confirm the expected project role applies | ☐ |
| 10 | No duplicate tasks | Confirm the task count has not doubled, which is what a storage sync would do | ☐ |
| 11 | Target unaffected | Spot-check two projects that already existed in the target, confirm unchanged | ☐ |

Checks 2 to 5 are the ones that confirm consensus behaviour survived the move. Counts alone will pass even when authorship has been lost.

### Phase 6. Release

17. Release the projects to annotators and notify them.
18. Leave the source running in read-only state. Do not decommission it yet. Resume identity provider synchronisation against both environments once the window closes, and leave the source application in place: removing it while the source is still a fallback can deprovision the accounts you would need to fall back onto.

## 8. What does not migrate

| | |
|---|---|
| Unsubmitted drafts | Annotators submit or discard before the freeze |
| Review decisions and review history | Complete outstanding reviews before the freeze, or export as a record and re-review on the target |
| Comments | Export as a record if they carry operational meaning |
| Manual task assignments | Export the assignment list before the freeze and recreate it |
| Annotation history, activity and audit logs | Retained on the source for the fallback period |
| Webhooks and ML backends | Recreate on the target |
| Task, annotation and inner IDs | Renumbered. Confirm no external system references them |
| Cached agreement scores | Recomputed after import; dashboards show a one-off change |

## 9. Fallback

**Trigger:** counts do not reconcile, authorship is wrong, media does not render, or queues serve the wrong tasks.

**Action:** unpublish or pause the target projects, resume annotation in the source, and notify annotators. Leave the group mappings alone; rolling back through them only creates state to reconcile once synchronisation resumes. Because the migration is additive, rolling back means deleting the imported projects from the target. Nothing else in the target is affected.

Reattributed authorship is the one failure that cannot be repaired in place. There is no supported way to reassign an imported annotation to its original author afterwards, so the response is to delete the imported project, close the account gap, and migrate again. The source being quiesced is what makes that cheap: a second attempt inside the same window loses nothing.

**Decommission:** retire the source only after an agreed period of clean operation in the target. Set that period during pre-flight step 6.6. Remove the source SCIM application from the identity provider as part of decommissioning, not before.

## 10. Communicate to annotators before the freeze

- Anything started but not submitted before the stop time will not carry over. Submit or discard.
- Project links change. Existing bookmarks to the source environment will not work.
- Submitted annotations, and who made them, carry across in full.
- Comments, review history and activity history do not carry across.
