#!/usr/bin/env python3
"""Copy Label Studio Enterprise project settings that migrate-ls-to-ls.py leaves behind.

migrate-ls-to-ls.py copies a fixed allowlist of core project fields and nothing
else, so every enterprise setting -- agreement, annotator evaluation, review and
assignment configuration -- is left at its default on the target. This script
closes that gap, and also corrects the per-task completion state the import
leaves behind.

It is driven by `project_mapping.json`, the old-id -> new-id file that
migrate-ls-to-ls.py writes as it goes, so it must run *after* the migration.

Usage:
    python copy_project_settings.py \
        --src-url https://source --src-key <src-token> \
        --dst-url https://target --dst-key <dst-token> \
        --mapping project_mapping.json --dry-run

Run it with --dry-run first: it prints the settings it would change on each
target project and writes nothing.
"""
import argparse
import json
import os
import sys
import time

import requests

TIMEOUT = 120

# Enterprise settings held on LseProject. These are exposed on the project
# resource itself (the serializer flattens them with source='lse_project.*'),
# so they can be written with an ordinary project PATCH.
LSE_PROJECT_FIELDS = [
    'require_comment_on_skip',
    'strict_task_overlap',
    'show_unused_data_columns_to_annotators',
    'agreement_methodology',
    'agreement_threshold',
    'max_additional_annotators_assignable',
    'annotation_limit_count',
    'annotation_limit_percent',
    'annotator_evaluation_metric',
    'pause_on_failed_annotator_evaluation',
    'annotator_evaluation_minimum_score',
    'annotator_evaluation_minimum_tasks',
    'annotator_evaluation_onboarding_tasks',
    'annotator_evaluation_continuous_tasks',
    'custom_script',
    'comment_classification_config',
    'use_custom_interface',
    'custom_interface_code',
    'custom_interface_compiled',
    'custom_interface_params',
    'input_schema',
    'output_schema',
]

# A few of the fields above are also in migrate-ls-to-ls.py's create payload,
# require_comment_on_skip among them. They are re-applied here deliberately:
# the project serializer applies the flattened lse_project fields on update,
# while create only handles the custom-interface ones explicitly, so a value
# sent at creation does not necessarily land.

# Core project fields that migrate-ls-to-ls.py does not carry.
CORE_FIELDS = [
    'annotator_evaluation_enabled',
    'custom_task_lock_ttl',
]

# Nested settings objects, and the keys to strip from each before sending them
# on. Both are ModelSerializers over `fields = '__all__'` on models with a
# project relation, so a round-tripped payload carries the *source* project id.
# requeue_rejected_tasks_to_annotator is read-only and derived from
# requeue_rejected_tasks_mode, so it is dropped and the mode carries it.
NESTED_SETTINGS = {
    'review_settings': {'id', 'project', 'requeue_rejected_tasks_to_annotator'},
    'assignment_settings': {'id', 'project'},
}

# Settings on a second endpoint: POST /api/projects/<id>/project-extra-params/
EXTRA_PARAMS_FIELDS = ['use_kappa', 'annotator_params']

# Reported at the end so nothing is silently assumed to have travelled.
NOT_COPIED = [
    ('agreement_includes_missing_controls', 'no API exposure -- set it on the target by hand'),
    ('metric_name, metric_params', 'separate agreement-metric endpoint, not attempted here'),
    ('source_interface_id, source_interface_version', 'organization-scoped; the compiled interface code is copied instead'),
    ('project members and roles', 'separate resource'),
    ('webhooks, ML backends', 'separate resources'),
]


class Instance:
    def __init__(self, url, token):
        self.url = url.rstrip('/')
        self.headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

    def get_project(self, project_id):
        r = requests.get(f'{self.url}/api/projects/{project_id}/', headers=self.headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    def patch_project(self, project_id, payload):
        r = requests.patch(
            f'{self.url}/api/projects/{project_id}/', headers=self.headers, json=payload, timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()

    def get_extra_params(self, project_id):
        """Returns None when the project has no annotator params (the API answers 204)."""
        r = requests.get(
            f'{self.url}/api/projects/{project_id}/project-extra-params/', headers=self.headers, timeout=TIMEOUT
        )
        if r.status_code == 204:
            return None
        r.raise_for_status()
        return r.json()

    def post_extra_params(self, project_id, payload):
        r = requests.post(
            f'{self.url}/api/projects/{project_id}/project-extra-params/',
            headers=self.headers, json=payload, timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json() if r.content else {}


def build_payload(source, target):
    """Settings present on the source that differ from the target project."""
    payload, changes = {}, []

    for field in LSE_PROJECT_FIELDS + CORE_FIELDS:
        if field not in source:
            continue
        if source[field] != target.get(field):
            payload[field] = source[field]
            changes.append(f'{field}: {target.get(field)!r} -> {source[field]!r}')

    for name, drop in NESTED_SETTINGS.items():
        src_obj = source.get(name)
        if not isinstance(src_obj, dict):
            continue
        # Send the whole object: the nested serializers are not constructed
        # with partial=True, so a subset risks unspecified fields resolving to
        # serializer defaults rather than being left alone.
        cleaned = {k: v for k, v in src_obj.items() if k not in drop}
        tgt_obj = target.get(name) or {}
        differing = [k for k, v in cleaned.items() if v != tgt_obj.get(k)]
        if differing:
            payload[name] = cleaned
            changes.append(f'{name}: {", ".join(sorted(differing))}')

    return payload, changes


def recalculate_task_states(dst, project_id, settle_seconds):
    """Rebuild per-task completion from submitted annotations only.

    The import marks a task complete by counting the distinct authors it
    arrived with, and that tally counts skipped annotations, so a task holding
    one submission and one skip from another person imports as already done.
    Changing annotations-per-task rebuilds completion using submitted
    annotations only.

    The value has to actually change -- writing back the value already stored
    is discarded as a no-op. Stepping *up* and back is deliberate: it keeps
    tasks that already carry an overlap above 1 in the same branch of the
    recalculation, so a project with a cohort below 100% keeps its existing
    cohort. Stepping down to 1 and back would clear every overlap and force the
    cohort to be re-selected from scratch.

    Scope, for a project whose cohort is below 100%: this rebuilds completion
    only for the tasks inside the cohort, because the branch it takes updates
    the tasks carrying an overlap above 1. Tasks outside the cohort are not
    reached. They do not need to be: the import itself rearranges the cohort
    when the percentage is below 100, and that rearrangement ends by rebuilding
    completion across every task in the project. Forcing a second full rebuild
    here by nudging the cohort percentage would re-select the cohort at random,
    which is worse than the problem it would solve.
    """
    project = dst.get_project(project_id)
    maximum = project.get('maximum_annotations')
    if not isinstance(maximum, int):
        return None

    dst.patch_project(project_id, {'maximum_annotations': maximum + 1})
    time.sleep(settle_seconds)
    dst.patch_project(project_id, {'maximum_annotations': maximum})
    time.sleep(settle_seconds)
    return maximum


def main():
    parser = argparse.ArgumentParser(description='Copy LSE project settings after migrate-ls-to-ls.py')
    parser.add_argument('--src-url', default=os.getenv('LABEL_STUDIO_URL', ''), help='Source instance')
    parser.add_argument('--src-key', default=os.getenv('LABEL_STUDIO_API_KEY', ''), help='Source token')
    parser.add_argument('--dst-url', default=os.getenv('DEST_LABEL_STUDIO_URL', ''), help='Target instance')
    parser.add_argument('--dst-key', default=os.getenv('DEST_LABEL_STUDIO_API_KEY', ''), help='Target token')
    parser.add_argument('--mapping', default='project_mapping.json', help='Mapping written by migrate-ls-to-ls.py')
    parser.add_argument('--project-ids', default=None, help='Source project ids to limit to, comma separated')
    parser.add_argument('--dry-run', action='store_true', help='Print what would change and write nothing')
    parser.add_argument(
        '--skip-recalculation', action='store_true',
        help='Do not rebuild per-task completion state (see recalculate_task_states)',
    )
    parser.add_argument('--settle-seconds', type=int, default=10, help='Pause after each write for its background job')
    args = parser.parse_args()

    for name, value in (('--src-url', args.src_url), ('--src-key', args.src_key),
                        ('--dst-url', args.dst_url), ('--dst-key', args.dst_key)):
        if not value:
            raise SystemExit(f'{name} is required')

    with open(args.mapping, encoding='utf-8') as fh:
        mapping = json.load(fh)
    if not mapping:
        raise SystemExit(f'{args.mapping} is empty; run migrate-ls-to-ls.py first')

    wanted = set(args.project_ids.split(',')) if args.project_ids else None
    src, dst = Instance(args.src_url, args.src_key), Instance(args.dst_url, args.dst_key)

    updated = failed = 0
    for source_id, target_id in sorted(mapping.items(), key=lambda kv: int(kv[0])):
        if wanted and str(source_id) not in wanted:
            continue

        print(f'\nproject {source_id} -> {target_id}')
        try:
            source, target = src.get_project(source_id), dst.get_project(target_id)
            payload, changes = build_payload(source, target)

            if not changes:
                print('  settings already match')
            for line in changes:
                print(f'  {line}')

            extra = src.get_extra_params(source_id)
            extra_payload = {f: extra[f] for f in EXTRA_PARAMS_FIELDS if extra and f in extra}
            if extra_payload:
                print(f'  project-extra-params: {", ".join(sorted(extra_payload))}')

            if args.dry_run:
                print('  dry run, nothing written')
                continue

            if payload:
                dst.patch_project(target_id, payload)
            if extra_payload:
                dst.post_extra_params(target_id, extra_payload)

            if not args.skip_recalculation:
                maximum = recalculate_task_states(dst, target_id, args.settle_seconds)
                if maximum is None:
                    print('  annotations-per-task unreadable, completion state NOT rebuilt')
                else:
                    print(f'  completion state rebuilt at annotations-per-task {maximum}')

            updated += 1
        except requests.HTTPError as exc:
            failed += 1
            body = exc.response.text[:400] if exc.response is not None else ''
            print(f'  FAILED: {exc}\n  {body}')

    print(f'\n{updated} project(s) updated, {failed} failed.')
    print('\nNot copied by this script, handle separately:')
    for field, why in NOT_COPIED:
        print(f'  - {field}: {why}')
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
