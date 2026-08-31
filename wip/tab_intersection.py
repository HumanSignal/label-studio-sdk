#!/usr/bin/env python3
"""Analyze how many tasks two Label Studio Data Manager tabs (views) have in common.

Usage:
    export LABEL_STUDIO_API_KEY=<your personal access token>
    python wip/tab_intersection.py --project 280769 --tab 583304 --tab 584750

A "tab" in the Data Manager UI is a View object. Listing tasks with
`view=<tab_id>` applies that tab's saved filters, so the set of task IDs
returned for a tab is exactly what the tab shows.
"""

import argparse
import json
import os
import sys

from label_studio_sdk.client import LabelStudio


def fetch_tab_task_ids(client, project_id, view_id, page_size=500):
    """Return the ordered list of task IDs visible in a tab."""
    ids = []
    pager = client.tasks.list(
        project=project_id,
        view=view_id,
        fields="task_only",   # skip annotations/predictions: we only need IDs
        page_size=page_size,
    )
    for task in pager:
        task_id = getattr(task, "id", None)
        if task_id is not None:
            ids.append(task_id)
    return ids


def describe_view(client, view_id):
    view = client.views.get(str(view_id))
    filter_group = None
    if view.filter_group is not None:
        fg = view.filter_group
        filter_group = fg.dict() if hasattr(fg, "dict") else fg
    data = view.data if isinstance(view.data, dict) else {}
    return {
        "id": view.id,
        "project": view.project,
        "title": data.get("title"),
        "ordering": view.ordering,
        "selected_items": view.selected_items,
        "filter_group": filter_group,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=int, required=True, help="Project ID")
    parser.add_argument("--tab", type=int, action="append", required=True,
                        help="Tab (view) ID; pass twice")
    parser.add_argument("--base-url", default="https://app.humansignal.com")
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--out", default="wip/intersection_result.json")
    args = parser.parse_args()

    if len(args.tab) != 2:
        parser.error("pass exactly two --tab values")

    api_key = os.environ.get("LABEL_STUDIO_API_KEY")
    if not api_key:
        sys.exit("LABEL_STUDIO_API_KEY is not set")

    client = LabelStudio(base_url=args.base_url, api_key=api_key)
    tab_a, tab_b = args.tab

    views = {}
    for tab in (tab_a, tab_b):
        info = describe_view(client, tab)
        views[tab] = info
        if info["project"] != args.project:
            sys.exit(f"tab {tab} belongs to project {info['project']}, not {args.project}")
        print(f"tab {tab}: title={info['title']!r}")
        print(f"  filters: {json.dumps(info['filter_group'], default=str)}")

    ids_a = fetch_tab_task_ids(client, args.project, tab_a, args.page_size)
    ids_b = fetch_tab_task_ids(client, args.project, tab_b, args.page_size)

    set_a, set_b = set(ids_a), set(ids_b)
    both = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    union = set_a | set_b

    def pct(part, whole):
        return round(100.0 * len(part) / len(whole), 2) if whole else 0.0

    result = {
        "project": args.project,
        "tabs": {str(k): v for k, v in views.items()},
        "counts": {
            f"tab_{tab_a}_total": len(set_a),
            f"tab_{tab_b}_total": len(set_b),
            "intersection": len(both),
            f"only_in_{tab_a}": len(only_a),
            f"only_in_{tab_b}": len(only_b),
            "union": len(union),
        },
        "overlap_pct": {
            f"of_tab_{tab_a}": pct(both, set_a),
            f"of_tab_{tab_b}": pct(both, set_b),
            "jaccard": pct(both, union),
        },
        "duplicates_returned": {
            f"tab_{tab_a}": len(ids_a) - len(set_a),
            f"tab_{tab_b}": len(ids_b) - len(set_b),
        },
        "intersection_task_ids": sorted(both),
        f"only_in_{tab_a}_task_ids": sorted(only_a),
        f"only_in_{tab_b}_task_ids": sorted(only_b),
    }

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    print()
    print(f"tab {tab_a}: {len(set_a)} tasks")
    print(f"tab {tab_b}: {len(set_b)} tasks")
    print(f"intersection: {len(both)} tasks "
          f"({result['overlap_pct'][f'of_tab_{tab_a}']}% of tab {tab_a}, "
          f"{result['overlap_pct'][f'of_tab_{tab_b}']}% of tab {tab_b})")
    print(f"only in {tab_a}: {len(only_a)}   only in {tab_b}: {len(only_b)}   union: {len(union)}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
