"""Tests for the per-surface call observer in ``run_hs_backend`` (rust mode fails loudly)."""

import pytest

from label_studio_sdk.converter.hs_backends import (
    HS_RUST_ALLOW_DUAL_ENV,
    HS_RUST_BACKEND_ENV,
    run_hs_backend,
    set_hs_rust_call_observer,
)


@pytest.fixture(autouse=True)
def calls(monkeypatch):
    for name in (HS_RUST_BACKEND_ENV, HS_RUST_ALLOW_DUAL_ENV):
        for prefix in ("", "LABEL_STUDIO_", "HEARTEX_"):
            monkeypatch.delenv(prefix + name, raising=False)
    monkeypatch.setenv(HS_RUST_BACKEND_ENV, "rust")
    observed = []
    set_hs_rust_call_observer(lambda surface, outcome: observed.append((surface, outcome)))
    yield observed
    set_hs_rust_call_observer(None)


def _boom(*_args):
    raise RuntimeError("pgbouncer rejected startup option")


def test_rust_success_reports_ok(calls):
    assert run_hs_backend(lambda: "py", lambda: "ru", surface="s") == "ru"
    assert calls == [("s", "ok")]


@pytest.mark.parametrize("where", ["setup", "fn"])
def test_rust_failure_raises_and_reports_error(calls, where):
    python_calls = []

    def py():
        python_calls.append(1)
        return "py"

    kwargs = {"rust_setup": _boom} if where == "setup" else {"rust_setup": lambda: "pool"}
    rust_fn = (lambda setup: "ru") if where == "setup" else _boom
    with pytest.raises(RuntimeError, match="pgbouncer"):
        run_hs_backend(py, rust_fn, surface="s", **kwargs)
    assert python_calls == []
    assert calls == [("s", "error")]


def test_every_failure_raises(calls):
    """No breaker: a broken environment fails on every call, not just the first."""
    for _ in range(5):
        with pytest.raises(RuntimeError):
            run_hs_backend(lambda: "py", _boom, surface="s")
    assert calls == [("s", "error")] * 5


def test_observer_errors_never_reach_the_caller(calls):
    def broken_observer(_surface, _outcome):
        raise RuntimeError("statsd down")

    set_hs_rust_call_observer(broken_observer)
    assert run_hs_backend(lambda: "py", lambda: "ru", surface="s") == "ru"
    with pytest.raises(RuntimeError, match="pgbouncer"):
        run_hs_backend(lambda: "py", _boom, surface="s")


def test_python_backend_skips_rust_and_observer(calls, monkeypatch):
    monkeypatch.setenv(HS_RUST_BACKEND_ENV, "python")
    assert run_hs_backend(lambda: "py", _boom, surface="s") == "py"
    assert calls == []


def test_dual_mode_is_not_observed(calls, monkeypatch):
    monkeypatch.setenv(HS_RUST_BACKEND_ENV, "dual")
    monkeypatch.setenv(HS_RUST_ALLOW_DUAL_ENV, "1")
    assert run_hs_backend(lambda: "py", lambda: "ru", surface="s") == "ru"
    with pytest.raises(RuntimeError, match="pgbouncer"):
        run_hs_backend(lambda: "py", _boom, surface="s")
    assert calls == []
