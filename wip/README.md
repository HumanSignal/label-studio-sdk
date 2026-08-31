# Tab intersection analysis — project 280769, tabs 583304 vs 584750

## Status: blocked on network egress

The analysis could not be run from this session. `app.humansignal.com:443` is
denied by the organization's egress policy on the agent proxy:

```
{"kind": "connect_rejected",
 "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
 "host": "app.humansignal.com:443"}
```

This is a policy denial, not a credential problem — no API key was present in the
session either. The host has to be allowlisted for the environment (or the script
run somewhere with access) before real numbers can be produced.

## What is here

`tab_intersection.py` does the analysis and is validated end-to-end against a
mock of the two API endpoints (`mock_server.py`).

A "tab" in the Data Manager UI is a **View**. Listing tasks with `view=<tab_id>`
makes the server apply that tab's saved filters, so the task IDs returned for a
tab are exactly the tasks the tab shows. The script fetches both ID sets and
compares them.

## Running it

```bash
export LABEL_STUDIO_API_KEY=<personal access token>
python wip/tab_intersection.py --project 280769 --tab 583304 --tab 584750
```

It prints each tab's title and filter definition, then:

- total tasks per tab
- size of the intersection, as a count and as a % of each tab
- tasks only in one tab, union, Jaccard overlap

Full task ID lists are written to `wip/intersection_result.json`.

Notes:
- `fields="task_only"` is used, so annotations/predictions are not transferred —
  only IDs are needed.
- The script asserts both tabs belong to the given project and exits if not.
- `--page-size` (default 500) and `--base-url` are adjustable; the default base
  URL is `https://app.humansignal.com`.

## Validating the logic offline

```bash
python wip/mock_server.py &          # tab A = tasks 1..120, tab B = tasks 100..219
LABEL_STUDIO_API_KEY=dummy python wip/tab_intersection.py \
  --project 280769 --tab 583304 --tab 584750 \
  --base-url http://127.0.0.1:8931 --page-size 50
```

Expected: 120 tasks per tab, intersection 21, union 219.
