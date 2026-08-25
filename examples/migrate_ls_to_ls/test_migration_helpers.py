"""Offline tests for the migration helper scripts.

No network: the HTTP layer is stubbed, so these exercise the logic that decides
what gets written and what gets reported, which is where the risk sits.
"""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope='module')
def settings_module():
    return _load('copy_project_settings')


@pytest.fixture(scope='module')
def preflight_module():
    return _load('preflight_check')


# --- copy_project_settings.build_payload ------------------------------------


@pytest.fixture
def source_project():
    return {
        'id': 12,
        'agreement_threshold': '0.75',
        'strict_task_overlap': True,
        'annotator_evaluation_enabled': True,
        'custom_task_lock_ttl': 3600,
        'max_additional_annotators_assignable': 2,
        'review_settings': {
            'id': 5, 'project': 12, 'review_criteria': 'all',
            'requeue_rejected_tasks_mode': 'requeue',
            'requeue_rejected_tasks_to_annotator': True,
            'require_comment_on_reject': True,
        },
        'assignment_settings': {'id': 9, 'project': 12, 'label_stream_task_distribution': 'manual'},
    }


@pytest.fixture
def target_project():
    return {
        'id': 88,
        'agreement_threshold': '0.0',
        'strict_task_overlap': True,          # same as source
        'annotator_evaluation_enabled': False,
        'custom_task_lock_ttl': None,
        'max_additional_annotators_assignable': 2,  # same as source
        'review_settings': {
            'id': 7, 'project': 88, 'review_criteria': 'sampled',
            'requeue_rejected_tasks_mode': 'remove',
            'requeue_rejected_tasks_to_annotator': False,
            'require_comment_on_reject': True,
        },
        'assignment_settings': {'id': 4, 'project': 88, 'label_stream_task_distribution': 'auto'},
    }


def test_only_differing_fields_are_sent(settings_module, source_project, target_project):
    payload, _ = settings_module.build_payload(source_project, target_project)
    assert payload['agreement_threshold'] == '0.75'
    assert payload['annotator_evaluation_enabled'] is True
    assert payload['custom_task_lock_ttl'] == 3600
    assert 'strict_task_overlap' not in payload
    assert 'max_additional_annotators_assignable' not in payload


def test_nested_settings_drop_identity_and_read_only_keys(settings_module, source_project, target_project):
    payload, _ = settings_module.build_payload(source_project, target_project)
    review = payload['review_settings']
    # id/project would point the payload back at the *source* project.
    assert 'id' not in review and 'project' not in review
    # Read-only, derived from requeue_rejected_tasks_mode by the serializer.
    assert 'requeue_rejected_tasks_to_annotator' not in review
    assert review['requeue_rejected_tasks_mode'] == 'requeue'
    assert 'id' not in payload['assignment_settings'] and 'project' not in payload['assignment_settings']


def test_nested_settings_are_sent_whole_not_diffed(settings_module, source_project, target_project):
    """The nested serializers are not partial, so unchanged keys must travel too."""
    payload, _ = settings_module.build_payload(source_project, target_project)
    assert payload['review_settings']['require_comment_on_reject'] is True


def test_identical_projects_produce_no_changes(settings_module, source_project):
    payload, changes = settings_module.build_payload(source_project, source_project)
    assert payload == {} and changes == []


# --- copy_project_settings.recalculate_task_states --------------------------


class _RecordingTarget:
    def __init__(self, project):
        self.project, self.patches = project, []

    def get_project(self, project_id):
        return self.project

    def patch_project(self, project_id, payload):
        self.patches.append(payload)
        return {}


def test_recalculation_steps_up_then_back(settings_module):
    dst = _RecordingTarget({'maximum_annotations': 3})
    assert settings_module.recalculate_task_states(dst, 88, 0) == 3
    # Up first: stepping down to 1 would clear the overlap cohort.
    assert dst.patches == [{'maximum_annotations': 4}, {'maximum_annotations': 3}]


def test_recalculation_is_a_noop_when_value_unreadable(settings_module):
    dst = _RecordingTarget({'maximum_annotations': None})
    assert settings_module.recalculate_task_states(dst, 88, 0) is None
    assert dst.patches == []


# --- preflight_check.write_reconciliation -----------------------------------


def test_reconciliation_classifies_every_author(preflight_module, tmp_path):
    baselines = [{
        'project_id': 12,
        'annotations_per_annotator': {
            'sam@example.com': 12,        # exact match
            'a.patel@example.com': 40,    # target holds A.Patel@example.com
            'gone@example.com': 3,        # absent
            'unresolved:41': 2,           # export carried no email
        },
    }]
    present = {'sam@example.com', 'A.Patel@example.com'}
    total, missing, mismatched, unresolved = preflight_module.write_reconciliation(baselines, present, tmp_path)
    assert (total, missing, mismatched, unresolved) == (4, 1, 1, 1)

    rows = {
        line.split(',')[0]: line.split(',')[3]
        for line in (tmp_path / 'annotator-reconciliation.csv').read_text().strip().splitlines()[1:]
    }
    assert rows['sam@example.com'] == 'yes'
    # Case-only difference must not read as a match: the import compares exactly.
    assert rows['a.patel@example.com'] == 'case_mismatch'
    assert rows['gone@example.com'] == 'no'
    assert rows['unresolved:41'] == 'no_author_detail'


# --- preflight_check.sweep_project ------------------------------------------


class _StubResponse:
    def __init__(self, body, status_code=200):
        self._body, self.status_code = body, status_code

    def raise_for_status(self):
        pass

    def json(self):
        return self._body


def test_sweep_excludes_cancelled_annotations(preflight_module, monkeypatch):
    pages = {
        1: {'tasks': [
            {'annotations': [{'completed_by': {'email': 'sam@example.com'}},
                             {'completed_by': {'email': 'kim@example.com'}}]},
            {'annotations': [{'completed_by': {'email': 'sam@example.com'}},
                             {'completed_by': {'email': 'kim@example.com'}, 'was_cancelled': True}]},
            {'annotations': []},
        ]},
        2: {'tasks': []},
    }
    monkeypatch.setattr(preflight_module.requests, 'get', lambda url, **kw: _StubResponse(pages[kw['params']['page']]))

    result = preflight_module.Instance('http://x', 't').sweep_project(12)
    assert result['total_tasks'] == 3
    assert result['total_annotations'] == 3  # the cancelled one is not counted
    assert result['annotations_per_annotator'] == {'kim@example.com': 1, 'sam@example.com': 2}
    assert result['tasks_by_distinct_annotator_count'] == {0: 1, 1: 1, 2: 1}


def test_sweep_fails_loudly_on_a_first_page_404(preflight_module, monkeypatch):
    monkeypatch.setattr(preflight_module.requests, 'get', lambda url, **kw: _StubResponse({}, status_code=404))
    with pytest.raises(SystemExit):
        preflight_module.Instance('http://x', 't').sweep_project(999)


# --- preflight_check.verify -------------------------------------------------


@pytest.fixture
def baseline():
    return {
        'project_id': 12, 'total_tasks': 3, 'total_annotations': 3,
        'tasks_by_distinct_annotator_count': {0: 1, 1: 1, 2: 1},
        'annotations_per_annotator': {'kim@example.com': 1, 'sam@example.com': 2},
    }


class _StubTarget:
    def __init__(self, result):
        self.result = result

    def sweep_project(self, project_id):
        return self.result


def test_verify_passes_when_the_target_matches(preflight_module, tmp_path, baseline):
    """A baseline read back from JSON has string keys where a fresh sweep has ints."""
    (tmp_path / 'baseline-12.json').write_text(json.dumps(baseline))
    assert preflight_module.verify(_StubTarget(baseline), {'12': 88}, tmp_path) == 0


def test_verify_reports_count_and_authorship_drift(preflight_module, tmp_path, baseline):
    (tmp_path / 'baseline-12.json').write_text(json.dumps(baseline))
    drifted = json.loads(json.dumps(baseline))
    drifted['total_annotations'] = 2
    drifted['annotations_per_annotator']['sam@example.com'] = 1
    assert preflight_module.verify(_StubTarget(drifted), {'12': 88}, tmp_path) == 1


def test_verify_fails_when_the_baseline_is_missing(preflight_module, tmp_path, baseline):
    assert preflight_module.verify(_StubTarget(baseline), {'12': 88}, tmp_path) == 1
