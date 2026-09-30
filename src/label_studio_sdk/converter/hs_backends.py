"""Shared hs-rust backend selection, load, and dual-mode helpers.

Owned by the SDK so LSE and standalone ``decode_rle`` share one resolver.
Django-free: only ``os.environ`` (with the same ``LABEL_STUDIO_`` / ``HEARTEX_``
prefix order as ``label_studio.core.utils.params.get_env``).

Ops sets one global knob:

* ``HS_RUST_BACKEND`` — default ``python``

``dual`` is local-dev only and requires ``HS_RUST_ALLOW_DUAL`` truthy.
Unknown / malformed values fail closed to ``python`` / ``False``.

Call sites share:

* ``load_hs_rust`` / ``require_hs_rust`` — extension import (success cached)
* ``env_truthy`` / ``profile_timed`` — profile flags and timing
* ``run_hs_backend`` — python | rust | dual dispatch with optional compare
* ``assert_optional_floats_close`` — dual score maps / scalars
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Optional, TypeVar

logger = logging.getLogger(__name__)

HS_BACKEND_CHOICES = frozenset({"python", "rust", "dual"})
HS_RUST_BACKEND_ENV = "HS_RUST_BACKEND"
HS_RUST_ALLOW_DUAL_ENV = "HS_RUST_ALLOW_DUAL"

# Per-surface dual-profile knobs (all go through env_truthy).
HS_BRUSH_PROFILE_ENV = "HS_BRUSH_PROFILE"
HS_AGREEMENT_PROFILE_ENV = "HS_AGREEMENT_PROFILE"
HS_VALUE_COUNTS_PROFILE_ENV = "HS_VALUE_COUNTS_PROFILE"
HS_GT_AGREEMENT_PROFILE_ENV = "HS_GT_AGREEMENT_PROFILE"

_ENV_TRUTHY = frozenset({"1", "true", "yes", "on"})

# Same lookup order as label_studio.core.utils.params.get_env / has_env
_ENV_PREFIXES = ("LABEL_STUDIO_", "HEARTEX_", "")

# Cached only after a successful import. Failed imports are not sticky so a
# later ``maturin develop`` in the same process can succeed without restart.
_HS_RUST_MODULE: Any | None = None

_HS_RUST_MISSING_MSG = (
    "HS_RUST_BACKEND=rust|dual requires the hs_rust extension. "
    "From repo root: cd libs/hs-rust && maturin develop --release "
    "(into the same venv as the running process; no restart needed after a successful build)."
)

T = TypeVar("T")
S = TypeVar("S")


def normalize_hs_backend(name: str, raw: Optional[str]) -> str:
    """Return a valid backend token; unknown / empty values become ``python``."""
    value = (raw or "python").strip().lower()
    if value not in HS_BACKEND_CHOICES:
        logger.warning("Unknown %s=%r; falling back to python", name, raw)
        return "python"
    return value


def raw_hs_env(name: str) -> Optional[str]:
    """Return the env value when the var is set (incl. LABEL_STUDIO_/HEARTEX_ prefixes)."""
    for prefix in _ENV_PREFIXES:
        key = prefix + name
        if key in os.environ:
            return os.environ[key]
    return None


def env_truthy(name: str) -> bool:
    """True when ``name`` (with LABEL_STUDIO_/HEARTEX_ prefixes) is 1/true/yes/on."""
    raw = raw_hs_env(name)
    if raw is None:
        return False
    return raw.strip().lower() in _ENV_TRUTHY


def hs_rust_allow_dual() -> bool:
    """``dual`` is local-dev only; requires an explicit allow flag."""
    return env_truthy(HS_RUST_ALLOW_DUAL_ENV)


def resolve_hs_backend_value(source: str, raw: Optional[str]) -> str:
    """Normalize a raw env value and apply the dual allow-gate."""
    value = normalize_hs_backend(source, raw)
    if value == "dual" and not hs_rust_allow_dual():
        logger.warning(
            "%s=%r requested dual, but %s is not enabled; falling back to python (dual is local-dev only)",
            source,
            raw,
            HS_RUST_ALLOW_DUAL_ENV,
        )
        return "python"
    return value


def hs_rust_backend() -> str:
    """Resolve ``HS_RUST_BACKEND`` (default ``python``; dual gated)."""
    raw = raw_hs_env(HS_RUST_BACKEND_ENV)
    if raw is None:
        return "python"
    return resolve_hs_backend_value(HS_RUST_BACKEND_ENV, raw)


def load_hs_rust() -> Any | None:
    """Return the ``hs_rust`` module, or ``None`` if it is not importable.

    Successful imports are cached for the process lifetime. Failed imports are
    **not** cached so ``maturin develop`` is picked up without restart.
    """
    global _HS_RUST_MODULE
    if _HS_RUST_MODULE is not None:
        return _HS_RUST_MODULE
    try:
        import hs_rust as native  # type: ignore[import-not-found]
    except ImportError:
        return None
    _HS_RUST_MODULE = native
    return _HS_RUST_MODULE


def require_hs_rust() -> Any:
    """Return ``hs_rust`` or raise if ``HS_RUST_BACKEND=rust|dual`` needs it."""
    native = load_hs_rust()
    if native is None:
        raise RuntimeError(_HS_RUST_MISSING_MSG)
    return native


def clear_hs_rust_module_cache() -> None:
    """Drop the cached module (tests / rare local reload). Not needed in prod."""
    global _HS_RUST_MODULE
    _HS_RUST_MODULE = None


def profile_timed(enabled: bool, fn: Callable[[], T]) -> tuple[T, float]:
    """Run ``fn``; measure wall time only when profiling is enabled."""
    if not enabled:
        return fn(), 0.0
    started = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - started


@dataclass(frozen=True)
class DualTimings:
    """Wall times from ``run_hs_backend`` dual mode (seconds)."""

    python: float = 0.0
    rust: float = 0.0
    rust_setup: float = 0.0


def assert_optional_floats_close(
    python_value: float | None,
    rust_value: float | None,
    *,
    atol: float,
    message: str,
) -> None:
    """Raise ``AssertionError`` when optional floats disagree beyond ``atol``."""
    if python_value is None or rust_value is None:
        if python_value != rust_value:
            raise AssertionError(message)
    elif abs(python_value - rust_value) > atol:
        raise AssertionError(message)


def assert_optional_float_maps_close(
    python_map: Mapping[Any, float | None],
    rust_map: Mapping[Any, float | None],
    keys: Iterable[Any],
    *,
    atol: float,
    message_fmt: str,
) -> None:
    """Compare optional-float maps for ``keys``.

    ``message_fmt`` may use ``{key}``, ``{python}``, ``{rust}``.
    """
    for key in keys:
        python_value = python_map[key]
        rust_value = rust_map[key]
        assert_optional_floats_close(
            python_value,
            rust_value,
            atol=atol,
            message=message_fmt.format(key=key, python=python_value, rust=rust_value),
        )


def run_hs_backend(
    python_fn: Callable[[], T],
    rust_fn: Callable[..., T],
    *,
    compare: Callable[[T, T], None] | None = None,
    profile_env: str | None = None,
    on_profile: Callable[[DualTimings, T, T], None] | None = None,
    rust_setup: Callable[[], S] | None = None,
) -> T:
    """Dispatch ``python`` | ``rust`` | ``dual`` for an hs-rust callsite.

    * ``rust`` / ``dual``: optional ``rust_setup`` runs first (Vipere pool init);
      its result is passed as the sole argument to ``rust_fn``. Without setup,
      ``rust_fn`` is called with no arguments.
    * ``dual``: runs python then rust, calls ``compare(py, rust)`` if given,
      optionally profiles when ``profile_env`` is truthy, returns the rust result.
    """
    backend = hs_rust_backend()
    if backend == "python":
        return python_fn()

    profile = backend == "dual" and bool(profile_env) and env_truthy(profile_env)

    setup: Any = None
    t_setup = 0.0
    if rust_setup is not None:
        setup, t_setup = profile_timed(profile, rust_setup)

    def _rust() -> T:
        return rust_fn(setup) if rust_setup is not None else rust_fn()

    if backend == "rust":
        return _rust()

    # dual
    python_out, t_py = profile_timed(profile, python_fn)
    rust_out, t_rust = profile_timed(profile, _rust)
    if compare is not None:
        compare(python_out, rust_out)
    if profile and on_profile is not None:
        on_profile(DualTimings(python=t_py, rust=t_rust, rust_setup=t_setup), python_out, rust_out)
    return rust_out
