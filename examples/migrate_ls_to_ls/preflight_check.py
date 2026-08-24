#!/usr/bin/env python3
"""Pre-flight and validation checks around a migrate-ls-to-ls.py migration.

Two modes.

Pre-flight (default) reads the source projects and answers the one question
that decides whether the migration succeeds or silently corrupts authorship:
does every annotator who has created work in these projects already exist in
the target organization, under the same address? It also records the counts to
validate against afterwards.

    python preflight_check.py --project-ids 12,15,18 \
        --src-url https://source --src-key <src-token> \
        --dst-url https://target --dst-key <dst-token>

Validation (--verify) re-reads the migrated projects on the target and compares
them against those recorded counts, per project and per annotator.

    python preflight_check.py --verify project_mapping.json \
        --src-url https://source --src-key <src-token> \
        --dst-url https://target --dst-key <dst-token>

Authors are derived from the annotations themselves, not from the project
member list: someone who annotated months ago and has since left the group is
no longer a member, but their work still needs an account to attach to.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

import requests

TIMEOUT = 120
PAGE_SIZE = 200


class Instance:
    def __init__(self, url, token):
        self.url = url.rstrip('/')
        self.headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

    def sweep_project(self, project_id):
        """Task and annotation counts, and annotation authors, for one project."""
        per_annotator = Counter()
        by_author_count = Counter()
        tasks = annotations = 0
        page = 1

        while True:
            r = requests.get(
                f'{self.url}/api/tasks',
                headers=self.headers,
                params={'project': project_id, 'page': page, 'page_size': PAGE_SIZE, 'fields': 'all'},
                timeout=TIMEOUT,
            )
            if r.status_code == 404:  # paged past the end
                break
            r.raise_for_status()
            payload = r.json()
            batch = payload.get('tasks', payload) if isinstance(payload, dict) else payload
            if not batch:
                break

            for task in batch:
                tasks += 1
                authors = set()
                for annotation in task.get('annotations', []):
                    if annotation.get('was_cancelled'):
                        continue
                    annotations += 1
                    author = annotation.get('completed_by')
                    if isinstance(author, dict):
                        identity = author.get('email') or author.get('username')
                    else:
                        identity = f'unresolved:{author}'
                    if not identity:
                        identity = f'unresolved:{author}'
                    per_annotator[identity] += 1
                    authors.add(identity)
                by_author_count[len(authors)] += 1
            page += 1

        return {
            'project_id': int(project_id),
            'total_tasks': tasks,
            'total_annotations': annotations,
            'tasks_by_distinct_annotator_count': dict(sorted(by_author_count.items())),
            'annotations_per_annotator': dict(sorted(per_annotator.items())),
        }

    def org_identities(self, org_id=None):
        """Emails in the organization, in the casing it stores.

        Casing is preserved deliberately: the import matches an annotation's
        author address as an exact string, so a case-only difference is a real
        gap that a case-insensitive check would hide.
        """
        if not org_id:
            r = requests.get(f'{self.url}/api/organizations/', headers=self.headers, timeout=TIMEOUT)
            r.raise_for_status()
            payload = r.json()
            orgs = payload.get('results', payload) if isinstance(payload, dict) else payload
            if not orgs:
                raise SystemExit('No organization found in the target environment.')
            if len(orgs) > 1:
                raise SystemExit('The target has more than one organization. Set LS_TARGET_ORG_ID.')
            org_id = orgs[0]['id']

        identities, page = set(), 1
        while True:
            r = requests.get(
                f'{self.url}/api/organizations/{org_id}/memberships',
                headers=self.headers, params={'page': page, 'page_size': 100}, timeout=TIMEOUT,
            )
            r.raise_for_status()
            payload = r.json()
            for membership in payload.get('results', []):
                user = membership.get('user') or {}
                email = user.get('email') or user.get('username')
                if email:
                    identities.add(email)
            if not payload.get('next'):
                return identities
            page += 1


def write_reconciliation(baselines, present, out_dir):
    """One row per annotation author, checked against the target organization."""
    authors = {}
    for baseline in baselines:
        for identity, count in baseline['annotations_per_annotator'].items():
            entry = authors.setdefault(identity, {'annotations': 0, 'projects': []})
            entry['annotations'] += count
            entry['projects'].append(str(baseline['project_id']))

    folded = {identity.lower(): identity for identity in present}
    missing = mismatched = unresolved = 0

    with (out_dir / 'annotator-reconciliation.csv').open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['identity', 'annotations', 'projects', 'present_in_target', 'target_identity'])
        for identity in sorted(authors):
            target_identity = ''
            if identity.startswith('unresolved:'):
                status = 'no_author_detail'
                unresolved += 1
            elif identity in present:
                status, target_identity = 'yes', identity
            elif identity.lower() in folded:
                status, target_identity = 'case_mismatch', folded[identity.lower()]
                mismatched += 1
            else:
                status = 'no'
                missing += 1
            writer.writerow([
                identity, authors[identity]['annotations'],
                ' '.join(authors[identity]['projects']), status, target_identity,
            ])

    return len(authors), missing, mismatched, unresolved


def preflight(src, dst, project_ids, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    baselines = []

    for project_id in project_ids:
        print(f'project {project_id}: reading')
        baseline = src.sweep_project(project_id)
        baselines.append(baseline)
        (out_dir / f'baseline-{project_id}.json').write_text(
            json.dumps(baseline, indent=2), encoding='utf-8'
        )
        print(f"  tasks:       {baseline['total_tasks']}")
        print(f"  annotations: {baseline['total_annotations']}")
        print(f"  by distinct annotator count: {baseline['tasks_by_distinct_annotator_count']}")
        print(f"  annotators:  {len(baseline['annotations_per_annotator'])}")

    total, missing, mismatched, unresolved = write_reconciliation(
        baselines, dst.org_identities(os.getenv('LS_TARGET_ORG_ID')), out_dir
    )

    print(f'\n{total} annotation authors across {len(baselines)} project(s).')
    if unresolved:
        print(f'{unresolved} author(s) came back without an email. Do not migrate these projects.')
    if missing:
        print(f'{missing} author(s) are NOT present in the target organization.')
    if mismatched:
        print(f'{mismatched} author(s) match the target only when case is ignored.')
        print('The import matches the address exactly, so these will be reattributed. Treat them as missing.')
    if missing or mismatched or unresolved:
        print(f"\nDo not migrate until every row reads yes. See {out_dir / 'annotator-reconciliation.csv'}.")
        return 1

    print('Every annotation author is present in the target, with matching case.')
    return 0


def verify(src, dst, mapping, out_dir):
    failures = 0

    for source_id, target_id in sorted(mapping.items(), key=lambda kv: int(kv[0])):
        path = out_dir / f'baseline-{source_id}.json'
        if not path.exists():
            print(f'project {source_id}: no baseline at {path}, skipping')
            failures += 1
            continue

        baseline = json.loads(path.read_text(encoding='utf-8'))
        actual = dst.sweep_project(target_id)
        print(f'\nproject {source_id} -> {target_id}')

        problems = []
        for key in ('total_tasks', 'total_annotations'):
            if baseline[key] != actual[key]:
                problems.append(f"{key}: expected {baseline[key]}, found {actual[key]}")
            else:
                print(f"  {key}: {actual[key]}")

        expected_authors = baseline['annotations_per_annotator']
        actual_authors = actual['annotations_per_annotator']
        for identity in sorted(set(expected_authors) | set(actual_authors)):
            want, got = expected_authors.get(identity, 0), actual_authors.get(identity, 0)
            if want != got:
                problems.append(f'{identity}: expected {want} annotation(s), found {got}')

        # Keys are compared as strings: the baseline has been through JSON, which
        # turns the integer counts into strings, while a fresh sweep has integers.
        expected_spread = {str(k): v for k, v in baseline['tasks_by_distinct_annotator_count'].items()}
        actual_spread = {str(k): v for k, v in actual['tasks_by_distinct_annotator_count'].items()}
        if expected_spread != actual_spread:
            problems.append(f'distinct annotator spread: expected {expected_spread}, found {actual_spread}')

        if problems:
            failures += 1
            for problem in problems:
                print(f'  MISMATCH {problem}')
        else:
            print('  counts and authorship match the baseline')

    print(f"\n{'FAILED' if failures else 'PASSED'}: {failures} project(s) with mismatches.")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description='Pre-flight and validation for an LSE project migration')
    parser.add_argument('--src-url', default=os.getenv('LABEL_STUDIO_URL', ''))
    parser.add_argument('--src-key', default=os.getenv('LABEL_STUDIO_API_KEY', ''))
    parser.add_argument('--dst-url', default=os.getenv('DEST_LABEL_STUDIO_URL', ''))
    parser.add_argument('--dst-key', default=os.getenv('DEST_LABEL_STUDIO_API_KEY', ''))
    parser.add_argument('--project-ids', default=None, help='Source project ids, comma separated')
    parser.add_argument('--verify', default=None, metavar='MAPPING',
                        help='Validate a completed migration against the baselines, using project_mapping.json')
    parser.add_argument('--out-dir', default='./preflight', help='Where baselines and the reconciliation are written')
    args = parser.parse_args()

    for name, value in (('--src-url', args.src_url), ('--src-key', args.src_key),
                        ('--dst-url', args.dst_url), ('--dst-key', args.dst_key)):
        if not value:
            raise SystemExit(f'{name} is required')

    src, dst = Instance(args.src_url, args.src_key), Instance(args.dst_url, args.dst_key)
    out_dir = Path(args.out_dir)

    if args.verify:
        with open(args.verify, encoding='utf-8') as fh:
            mapping = json.load(fh)
        if not mapping:
            raise SystemExit(f'{args.verify} is empty; run migrate-ls-to-ls.py first')
        sys.exit(verify(src, dst, mapping, out_dir))

    if not args.project_ids:
        raise SystemExit('--project-ids is required for a pre-flight run')
    sys.exit(preflight(src, dst, [int(i) for i in args.project_ids.split(',')], out_dir))


if __name__ == '__main__':
    main()
