from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import time
import urllib.parse
import uuid
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

import appdirs
import httpx
import jwt
import typer

SIDECAR_SUFFIX = ".ls-interface.json"
DEFAULT_BASE_URL = "https://app.humansignal.com"
VALIDATOR_PACKAGE = "label_studio_sdk._extensions.interface.validator"
VALIDATOR_ASSETS = ("package.json", "package-lock.json", "validate.mjs", "scenario-runner.mjs")
INTERFACE_FILE_CANDIDATES = ("Screen.jsx", "Interface.jsx", "interface.jsx", "index.jsx")
TASK_FILE_CANDIDATES = ("task.json", "sample.json", "example-task.json", "example_task.json")
SCENARIO_FILE_CANDIDATES = ("scenarios.js", "scenario.js")
PARAMS_FILE_CANDIDATES = ("params.json", "parameters.json")

app = typer.Typer(
    help="Develop Label Studio custom interfaces.",
    context_settings={"help_option_names": ["--help"]},
)


@dataclass
class SyncResult:
    interface_id: int
    title: str
    status: str
    base_url: str
    source_hash: str
    source_version: int | None = None
    workspace_id: int | None = None

    @property
    def interface_url(self) -> str:
        return f"{self.base_url}/interfaces/{self.interface_id}/overview"


def _is_record(value: Any) -> bool:
    return isinstance(value, dict)


def _context_obj(ctx: typer.Context | None) -> dict[str, Any]:
    current = ctx
    while current is not None:
        if isinstance(current.obj, dict):
            return current.obj
        current = current.parent
    return {}


def _resolve_base_url(ctx: typer.Context | None, explicit: str | None = None) -> str:
    ctx_obj = _context_obj(ctx)
    return (
        explicit or ctx_obj.get("base_url") or os.getenv("LABEL_STUDIO_URL") or os.getenv("LS_URL") or DEFAULT_BASE_URL
    ).rstrip("/")


def _resolve_token(ctx: typer.Context | None, explicit: str | None = None) -> str | None:
    ctx_obj = _context_obj(ctx)
    return explicit or ctx_obj.get("api_key") or os.getenv("LABEL_STUDIO_API_KEY")


def _jwt_claims(token: str) -> dict[str, Any] | None:
    if token.count(".") != 2:
        return None
    try:
        claims = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except jwt.InvalidTokenError:
        return None
    return claims if isinstance(claims, dict) else None


def _refresh_access_token(base_url: str, refresh_token: str) -> str:
    with httpx.Client(timeout=30.0) as client:
        try:
            response = client.post(
                f"{base_url}/api/token/refresh/",
                json={"refresh": refresh_token},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            _surface_http_error(exc)
            raise typer.Exit(code=1) from None
        except httpx.HTTPError as exc:
            typer.echo(f"error: failed to refresh API token: {exc}", err=True)
            raise typer.Exit(code=1) from None

    data = response.json()
    access_token = data.get("access") if isinstance(data, dict) else None
    if not isinstance(access_token, str) or not access_token:
        typer.echo("error: token refresh response did not include an access token", err=True)
        raise typer.Exit(code=1)
    return access_token


def _auth_headers(token: str, *, base_url: str | None = None) -> dict[str, str]:
    claims = _jwt_claims(token)
    if base_url is not None and claims and claims.get("token_type") == "refresh":
        token = _refresh_access_token(base_url, token)
        claims = _jwt_claims(token)
    scheme = "Bearer" if claims else "Token"
    return {"Authorization": f"{scheme} {token}"}


def _load_json_file(path: Path | None, *, label: str) -> Any:
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        typer.echo(f"error: could not read {label} {path}: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except json.JSONDecodeError as exc:
        typer.echo(f"error: {label} is not valid JSON: {exc}", err=True)
        raise typer.Exit(code=2) from None


def _load_task(task_path: Path | None) -> dict[str, Any] | None:
    task = _load_json_file(task_path, label="task file")
    if task is not None and not isinstance(task, dict):
        typer.echo("error: --task must decode to a JSON object", err=True)
        raise typer.Exit(code=2)
    return task


def _resolve_bundle_file(
    bundle: Path,
    explicit: Path | None,
    candidates: tuple[str, ...],
) -> Path | None:
    if explicit is not None or not bundle.is_dir():
        return explicit
    for name in candidates:
        candidate = bundle / name
        if candidate.is_file():
            return candidate
    return None


def _resolve_interface_file(path: Path) -> Path:
    if path.is_file():
        return path
    if not path.is_dir():
        typer.echo(f"error: interface path does not exist: {path}", err=True)
        raise typer.Exit(code=2)

    for name in INTERFACE_FILE_CANDIDATES:
        candidate = path / name
        if candidate.is_file():
            return candidate

    jsx_files = sorted(candidate for candidate in path.glob("*.jsx") if candidate.is_file())
    if len(jsx_files) == 1:
        return jsx_files[0]
    if jsx_files:
        names = ", ".join(candidate.name for candidate in jsx_files)
        expected = ", ".join(INTERFACE_FILE_CANDIDATES)
        typer.echo(
            f"error: multiple JSX files in {path}: {names}. Rename one to one of: {expected}",
            err=True,
        )
        raise typer.Exit(code=2)

    expected = ", ".join(INTERFACE_FILE_CANDIDATES)
    typer.echo(f"error: no interface file found in {path}. Expected one of: {expected}", err=True)
    raise typer.Exit(code=2)


def _post_preview(client: httpx.Client, push_url: str, *, code: str, task: dict[str, Any] | None) -> bool:
    payload: dict[str, Any] = {"code": code}
    if task is not None:
        payload["task"] = task
    try:
        resp = client.post(push_url, json=payload, timeout=10.0)
    except httpx.HTTPError as exc:
        typer.echo(f"  preview sync failed: {exc}", err=True)
        return False
    if resp.status_code >= 400:
        typer.echo(f"  preview sync failed: HTTP {resp.status_code} {resp.text[:200]}", err=True)
        return False
    return True


def _validator_cache_dir() -> Path:
    return Path(appdirs.user_cache_dir("label-studio-sdk", "HumanSignal")) / "interface-validator"


def _copy_asset_if_needed(source: resources.abc.Traversable, target: Path) -> bool:
    data = source.read_bytes()
    if target.exists() and target.read_bytes() == data:
        return False
    target.write_bytes(data)
    return True


def _ensure_validator_assets(cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    package_files = resources.files(VALIDATOR_PACKAGE)
    changed = False
    for name in VALIDATOR_ASSETS:
        changed = _copy_asset_if_needed(package_files.joinpath(name), cache_dir / name) or changed
    if changed and (cache_dir / "node_modules").exists():
        shutil.rmtree(cache_dir / "node_modules")


def _ensure_validator_ready(*, require_scenario: bool = False) -> Path:
    if shutil.which("node") is None:
        typer.echo("error: `node` is required for interface validation. Install Node.js, then retry.", err=True)
        raise typer.Exit(code=2)

    cache_dir = _validator_cache_dir()
    _ensure_validator_assets(cache_dir)

    required_deps = ["sucrase"]
    if require_scenario:
        required_deps.extend(["playwright", "react", "react-dom"])
    missing = [dep for dep in required_deps if not (cache_dir / "node_modules" / dep).exists()]
    if missing:
        if shutil.which("npm") is None:
            typer.echo("error: `npm` is required to install validator dependencies.", err=True)
            raise typer.Exit(code=2)
        typer.echo(f"installing interface validator deps (one-time): {', '.join(missing)}", err=True)
        result = subprocess.run(
            ["npm", "install", "--silent", "--no-audit", "--no-fund"],
            cwd=cache_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            typer.echo(f"npm install failed:\n{result.stderr}", err=True)
            raise typer.Exit(code=2)
    return cache_dir


def _run_node_json(args: list[str], *, timeout: int, timeout_label: str) -> dict[str, Any]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        typer.echo(f"error: {timeout_label} timed out after {timeout}s", err=True)
        raise typer.Exit(code=2) from None

    if not result.stdout.strip():
        typer.echo(f"error: {timeout_label} returned no output", err=True)
        if result.stderr:
            typer.echo(result.stderr, err=True)
        raise typer.Exit(code=2)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        typer.echo(f"error: {timeout_label} returned invalid JSON: {exc}", err=True)
        if result.stdout:
            typer.echo(result.stdout, err=True)
        if result.stderr:
            typer.echo(result.stderr, err=True)
        raise typer.Exit(code=2) from None


def _run_validator(file: Path) -> dict[str, Any]:
    cache_dir = _ensure_validator_ready()
    return _run_node_json(
        ["node", str(cache_dir / "validate.mjs"), str(file.resolve())],
        timeout=15,
        timeout_label="validator",
    )


def _run_scenarios(file: Path, scenario: Path) -> dict[str, Any]:
    if scenario.suffix != ".js":
        typer.echo(f"error: --scenario expects a .js scenario module, got {scenario}", err=True)
        raise typer.Exit(code=2)
    cache_dir = _ensure_validator_ready(require_scenario=True)
    return _run_node_json(
        ["node", str(cache_dir / "scenario-runner.mjs"), str(file.resolve()), str(scenario.resolve())],
        timeout=45,
        timeout_label="scenario runner",
    )


def _print_static_report(file: Path, report: dict[str, Any], *, overall_ok: bool) -> None:
    if overall_ok:
        typer.echo(typer.style(f"OK {file.name} valid", fg=typer.colors.GREEN, bold=True))
    else:
        typer.echo(typer.style(f"FAIL {file.name} invalid", fg=typer.colors.RED, bold=True))

    for entry in report.get("errors") or []:
        line = f"  error [{entry.get('stage', '?')}]: {entry.get('message', '')}"
        typer.echo(typer.style(line, fg=typer.colors.RED), err=True)
    for entry in report.get("warnings") or []:
        line = f"  warn  [{entry.get('stage', '?')}]: {entry.get('message', '')}"
        typer.echo(typer.style(line, fg=typer.colors.YELLOW))

    exports = report.get("exports") or []
    if exports:
        typer.echo(f"  exports: {', '.join(exports)}")
    metadata = report.get("metadata") or {}
    if metadata.get("specVersion"):
        typer.echo(f"  specVersion: {metadata['specVersion']}")


def _print_scenario_report(report: dict[str, Any]) -> None:
    scenario_count = len(report.get("scenarios") or [])
    if scenario_count:
        typer.echo(f"  scenarios: {scenario_count}")
    for entry in report.get("errors") or []:
        line = f"  error [{entry.get('stage', 'scenario')}]: {entry.get('message', '')}"
        typer.echo(typer.style(line, fg=typer.colors.RED), err=True)
    for scenario in report.get("scenarios") or []:
        name = scenario.get("name") or "<unnamed>"
        color = typer.colors.GREEN if scenario.get("ok") else typer.colors.RED
        typer.echo(typer.style(f"    {'OK' if scenario.get('ok') else 'FAIL'} {name}", fg=color))
        for error in scenario.get("errors") or []:
            stage = error.get("stage", "scenario") if isinstance(error, dict) else "scenario"
            message = error.get("message", "") if isinstance(error, dict) else str(error)
            typer.echo(typer.style(f"      error [{stage}]: {message}", fg=typer.colors.RED), err=True)
        for warning in scenario.get("warnings") or []:
            stage = warning.get("stage", "scenario") if isinstance(warning, dict) else "scenario"
            message = warning.get("message", "") if isinstance(warning, dict) else str(warning)
            typer.echo(typer.style(f"      warn  [{stage}]: {message}", fg=typer.colors.YELLOW))


def _default_title(file: Path) -> str:
    parts = re.split(r"[-_\s]+", file.stem)
    return " ".join(part.capitalize() for part in parts if part) or file.stem


def _sidecar_path(file: Path) -> Path:
    return file.with_name(file.name + SIDECAR_SUFFIX)


def _read_sidecar(file: Path) -> dict[str, Any]:
    sidecar = _sidecar_path(file)
    if not sidecar.exists():
        return {}
    try:
        return json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"error: sidecar {sidecar.name} is not valid JSON: {exc}", err=True)
        raise typer.Exit(code=2) from None


def _write_sidecar(file: Path, data: dict[str, Any]) -> Path:
    sidecar = _sidecar_path(file)
    sidecar.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar


def _resolve_workspace(
    client: httpx.Client,
    base: str,
    workspace_id: int | None,
    workspace_title: str | None,
) -> int | None:
    if workspace_id is not None:
        return workspace_id
    if not workspace_title:
        return None
    resp = client.get(f"{base}/api/workspaces/")
    resp.raise_for_status()
    workspaces = resp.json()
    items = workspaces.get("results", workspaces) if isinstance(workspaces, dict) else workspaces
    matches = [workspace for workspace in items if workspace.get("title") == workspace_title]
    if not matches:
        typer.echo(f'error: no workspace with title "{workspace_title}"', err=True)
        raise typer.Exit(code=2)
    if len(matches) > 1:
        ids = ", ".join(str(workspace.get("id")) for workspace in matches)
        typer.echo(
            f'error: multiple workspaces titled "{workspace_title}" (ids: {ids}). Pass --workspace ID.', err=True
        )
        raise typer.Exit(code=2)
    return matches[0].get("id")


def _surface_http_error(exc: httpx.HTTPStatusError) -> None:
    body = exc.response.text
    try:
        body = json.dumps(exc.response.json(), indent=2)
    except ValueError:
        pass
    typer.echo(f"error: HTTP {exc.response.status_code} from {exc.request.url}\n{body}", err=True)


def _prepare_source(file: Path, *, no_validate: bool) -> tuple[str, str, str, dict[str, Any]]:
    report = _run_validator(file)
    if not no_validate and not report.get("ok"):
        typer.echo(
            typer.style(f"FAIL {file.name} invalid; refusing to sync.", fg=typer.colors.RED, bold=True), err=True
        )
        for entry in report.get("errors") or []:
            typer.echo(f"  error [{entry.get('stage', '?')}]: {entry.get('message', '')}", err=True)
        raise typer.Exit(code=1)

    compiled = report.get("compiled")
    if not compiled:
        typer.echo("error: source did not compile, so the API's required `compiled` field cannot be set.", err=True)
        for entry in report.get("errors") or []:
            typer.echo(f"  error [{entry.get('stage', '?')}]: {entry.get('message', '')}", err=True)
        raise typer.Exit(code=1)

    source = file.read_text(encoding="utf-8").rstrip()
    source_hash = _source_hash(source)
    return source, compiled, source_hash, report


def _new_version(source: str, compiled: str, report: dict[str, Any], *, publish: bool) -> dict[str, Any]:
    metadata = report.get("metadata") or {}
    version = {
        "code": source,
        "compiled": compiled,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "op": "api_push",
    }
    if not publish:
        version["unpublished"] = True
    for report_key, version_key in (
        ("inputSchema", "inputSchema"),
        ("outputSchema", "outputSchema"),
        ("paramsSchema", "paramsSchema"),
    ):
        value = metadata.get(report_key)
        if value not in (None, {}):
            version[version_key] = value
    return version


def _append_version_payload(version: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in version.items() if key not in {"id", "createdAt", "createdBy"}}


def _source_hash(source: str) -> str:
    return hashlib.sha256(source.rstrip().encode("utf-8")).hexdigest()


def _version_id(version: dict[str, Any], index: int) -> int:
    value = version.get("id")
    if isinstance(value, int) and value >= 0 and not isinstance(value, bool):
        return value
    return index


def _find_version(versions: list[dict[str, Any]], version_id: int | None) -> tuple[int, dict[str, Any]] | None:
    if not versions:
        return None
    if version_id is None:
        index = len(versions) - 1
        return _version_id(versions[index], index), versions[index]
    for index, version in enumerate(versions):
        if _version_id(version, index) == version_id:
            return version_id, version
    return None


def _latest_version_id(versions: list[dict[str, Any]]) -> int | None:
    if not versions:
        return None
    return _version_id(versions[-1], len(versions) - 1)


def _latest_published_version_id_for_source(versions: list[dict[str, Any]], source_hash: str) -> int | None:
    for index in range(len(versions) - 1, -1, -1):
        version = versions[index]
        if not _is_record(version) or version.get("unpublished"):
            continue
        code = version.get("code")
        if isinstance(code, str) and _source_hash(code) == source_hash:
            return _version_id(version, index)
    return None


def _build_history_entry(
    file: Path, source: str, compiled: str, message: str | None
) -> tuple[dict[str, Any], dict[str, Any]]:
    now_iso = datetime.now(timezone.utc).isoformat()
    message_id = str(uuid.uuid4())
    content = message or "Synced via label-studio-sdk interface CLI"
    chat_message = {
        "id": message_id,
        "role": "user",
        "content": content,
        "isManualEdit": True,
        "timestamp": now_iso,
    }
    artifact = {
        "code": source,
        "compiled": compiled,
        "createdAt": now_iso,
        "op": "api_push",
        "messageId": message_id,
        "description": message or f"Synced via label-studio-sdk interface CLI ({file.name})",
    }
    return chat_message, artifact


def _interface_schema_payload(report: dict[str, Any]) -> dict[str, Any]:
    metadata = report.get("metadata") or {}
    payload = {}
    if metadata.get("inputSchema") is not None:
        payload["input_schema"] = metadata["inputSchema"]
    if metadata.get("outputSchema") is not None:
        payload["output_schema"] = metadata["outputSchema"]
    extra_metadata = {}
    for key in ("paramsSchema", "regionSchema", "specVersion"):
        if metadata.get(key) not in (None, {}):
            extra_metadata[key] = metadata[key]
    if extra_metadata:
        payload["metadata"] = extra_metadata
    return payload


def _schema_defaults(schema: Any) -> dict[str, Any]:
    if not _is_record(schema) or not _is_record(schema.get("properties")):
        return {}
    defaults: dict[str, Any] = {}
    for key, value in schema["properties"].items():
        if _is_record(value) and "default" in value:
            defaults[key] = value["default"]
    return defaults


def _write_bundle_file(path: Path, contents: str, *, force: bool) -> None:
    if path.exists() and not force:
        typer.echo(f"error: refusing to overwrite {path}. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)
    path.write_text(contents, encoding="utf-8")
    typer.echo(f"wrote {path}")


def _json_file_contents(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sync_interface(
    *,
    ctx: typer.Context | None,
    file: Path,
    interface_id: int | None,
    title: str | None,
    workspace_id: int | None,
    workspace_title: str | None,
    token: str | None,
    lse_url: str | None,
    no_validate: bool,
    force: bool,
    dry_run: bool,
    message: str | None,
    publish: bool,
) -> SyncResult | None:
    resolved_token = _resolve_token(ctx, token)
    if not resolved_token:
        typer.echo("error: --token or LABEL_STUDIO_API_KEY is required", err=True)
        raise typer.Exit(code=2)

    file = file.resolve()
    base = _resolve_base_url(ctx, lse_url)
    source, compiled, source_hash, report = _prepare_source(file, no_validate=no_validate)
    sidecar = _read_sidecar(file)
    sidecar_entry = sidecar.get(base) if isinstance(sidecar, dict) else None

    if interface_id is not None:
        target_id = interface_id
    elif sidecar_entry and sidecar_entry.get("interface_id"):
        target_id = int(sidecar_entry["interface_id"])
    else:
        target_id = None

    chosen_title = title or (sidecar_entry or {}).get("title") or _default_title(file)
    action = "create" if target_id is None else "update"
    if (
        not publish
        and not force
        and target_id is not None
        and sidecar_entry
        and sidecar_entry.get("last_pushed_hash") == source_hash
    ):
        action = "skip"

    if dry_run:
        typer.echo(
            json.dumps(
                {
                    "action": action,
                    "base_url": base,
                    "file": str(file),
                    "interface_id": target_id,
                    "title": chosen_title,
                    "workspace": workspace_id,
                    "workspace_title": workspace_title,
                    "source_hash": source_hash,
                    "publish": publish,
                },
                indent=2,
            )
        )
        return None

    if action == "skip" and target_id is not None:
        typer.echo(f"no changes (hash {source_hash[:8]}), skipping. Use --force to sync anyway.")
        return SyncResult(
            interface_id=target_id,
            title=chosen_title,
            status="skipped",
            base_url=base,
            source_hash=source_hash,
            source_version=(sidecar_entry or {}).get("source_version"),
            workspace_id=(sidecar_entry or {}).get("workspace"),
        )

    headers = _auth_headers(resolved_token, base_url=base)
    new_version = _new_version(source, compiled, report, publish=publish)
    history_message, artifact = _build_history_entry(file, source, compiled, message)
    schema_payload = _interface_schema_payload(report)

    with httpx.Client(headers=headers, timeout=30.0) as client:
        try:
            if target_id is not None:
                existing_resp = client.get(f"{base}/api/interfaces/{target_id}/")
                existing_resp.raise_for_status()
                existing = existing_resp.json()
                prev_versions = existing.get("versions") or []
                if not force:
                    existing_hash = _source_hash(existing.get("code") or "")
                    if existing_hash == source_hash:
                        if publish:
                            published_source_version = _latest_published_version_id_for_source(
                                prev_versions, source_hash
                            )
                            if published_source_version is not None:
                                typer.echo(
                                    f"no changes vs published interface #{target_id}, skipping. "
                                    "Use --force to sync anyway."
                                )
                                return SyncResult(
                                    interface_id=target_id,
                                    title=existing.get("title") or chosen_title,
                                    status="skipped",
                                    base_url=base,
                                    source_hash=source_hash,
                                    source_version=published_source_version,
                                    workspace_id=existing.get("workspace"),
                                )
                        else:
                            typer.echo(f"no changes vs interface #{target_id}, skipping. Use --force to sync anyway.")
                            return SyncResult(
                                interface_id=target_id,
                                title=existing.get("title") or chosen_title,
                                status="skipped",
                                base_url=base,
                                source_hash=source_hash,
                                source_version=(sidecar_entry or {}).get("source_version"),
                                workspace_id=existing.get("workspace"),
                            )

                payload: dict[str, Any] = {
                    "code": source,
                    "compiled": compiled,
                    "versions": [_append_version_payload(new_version)],
                    "messages": [*(existing.get("messages") or []), history_message],
                    "artifacts": [*(existing.get("artifacts") or []), artifact],
                }
                if title:
                    payload["title"] = title
                payload.update({key: value for key, value in schema_payload.items() if key != "metadata"})
                if schema_payload.get("metadata"):
                    payload["metadata"] = {**(existing.get("metadata") or {}), **schema_payload["metadata"]}
                resp = client.post(f"{base}/api/interfaces/{target_id}/append_versions/", json=payload)
                resp.raise_for_status()
                data = resp.json()
                source_version = _latest_version_id(data.get("versions") or prev_versions)
                status = "updated"
                typer.echo(
                    typer.style(f"updated interface #{data['id']} ({data.get('title', '')})", fg=typer.colors.GREEN)
                )
            else:
                resolved_workspace_id = _resolve_workspace(client, base, workspace_id, workspace_title)
                payload = {
                    "title": chosen_title,
                    "code": source,
                    "compiled": compiled,
                    "versions": [new_version],
                    "messages": [history_message],
                    "artifacts": [artifact],
                    **schema_payload,
                }
                if resolved_workspace_id is not None:
                    payload["workspace"] = resolved_workspace_id
                resp = client.post(f"{base}/api/interfaces/", json=payload)
                resp.raise_for_status()
                data = resp.json()
                target_id = int(data["id"])
                source_version = 0
                status = "created"
                typer.echo(typer.style(f"created interface #{target_id} ({chosen_title!r})", fg=typer.colors.GREEN))
        except httpx.HTTPStatusError as exc:
            _surface_http_error(exc)
            raise typer.Exit(code=1) from None

    sidecar = sidecar if isinstance(sidecar, dict) else {}
    sidecar[base] = {
        "interface_id": target_id,
        "title": data.get("title") or chosen_title,
        "workspace": data.get("workspace"),
        "source_version": source_version,
        "last_pushed_hash": source_hash,
        "last_pushed_at": datetime.now(timezone.utc).isoformat(),
    }
    sidecar_path = _write_sidecar(file, sidecar)
    typer.echo(f"wrote {sidecar_path.name}")

    return SyncResult(
        interface_id=target_id,
        title=data.get("title") or chosen_title,
        status=status,
        base_url=base,
        source_hash=source_hash,
        source_version=source_version,
        workspace_id=data.get("workspace"),
    )


@app.command()
def preview(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the .jsx module or interface directory.",
    ),
    task: Path | None = typer.Option(
        None, "--task", exists=True, dir_okay=False, readable=True, help="Task data JSON."
    ),
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open the browser."),
) -> None:
    """Open the playground and live-sync local changes."""
    try:
        from watchfiles import watch
    except ImportError:
        typer.echo("error: `watchfiles` is required for preview. Reinstall label-studio-sdk dependencies.", err=True)
        raise typer.Exit(code=2) from None

    source_path = file
    task = _resolve_bundle_file(source_path, task, TASK_FILE_CANDIDATES)
    task_data = _load_task(task)
    file = _resolve_interface_file(source_path).resolve()
    task = task.resolve() if task is not None else None
    base = _resolve_base_url(ctx, lse_url)
    token = secrets.token_urlsafe(16)
    push_url = f"{base}/api/interfaces/playground/{token}/push/"
    playground_url = f"{base}/interfaces/playground?s={urllib.parse.quote(token)}&file={urllib.parse.quote(file.name)}"

    typer.echo(f"playground: {playground_url}")
    typer.echo(f"watching:   {file}")
    if task_data is not None:
        typer.echo(f"task data:  {task}")

    with httpx.Client() as client:
        code = file.read_text(encoding="utf-8")
        last_pushed_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if _post_preview(client, push_url, code=code, task=task_data):
            typer.echo("  pushed initial code")
        else:
            last_pushed_hash = ""

        if not no_open:
            webbrowser.open(playground_url)

        try:
            watch_paths = [file]
            if task is not None:
                watch_paths.append(task)
            for changes in watch(*watch_paths, step=200, recursive=False):
                changed_paths = {Path(path).resolve() for _, path in changes}
                task_changed = task is not None and task in changed_paths
                if file not in changed_paths and not task_changed:
                    continue
                try:
                    code = file.read_text(encoding="utf-8")
                except OSError as exc:
                    typer.echo(f"  read failed: {exc}", err=True)
                    continue
                source_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
                if source_hash == last_pushed_hash and not task_changed:
                    continue
                task_update = _load_task(task) if task_changed else None
                stamp = time.strftime("%H:%M:%S")
                if _post_preview(client, push_url, code=code, task=task_update):
                    last_pushed_hash = source_hash
                    suffix = " and task data" if task_changed else ""
                    typer.echo(f"  [{stamp}] pushed {len(code)} bytes{suffix}")
        except KeyboardInterrupt:
            typer.echo("\nbye")


@app.command()
def validate(
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the .jsx module or interface directory.",
    ),
    scenario: Path | None = typer.Option(
        None,
        "--scenario",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Interaction scenario JS module.",
    ),
    as_json: bool = typer.Option(False, "--json", help="Print the raw JSON report."),
) -> None:
    """Validate an interface offline."""
    source_path = file
    scenario = _resolve_bundle_file(source_path, scenario, SCENARIO_FILE_CANDIDATES)
    file = _resolve_interface_file(source_path)
    report = _run_validator(file)
    scenario_report = None
    if scenario is not None:
        if report.get("ok"):
            scenario_report = _run_scenarios(file, scenario)
        else:
            scenario_report = {
                "ok": False,
                "skipped": True,
                "scenarioFile": str(scenario.resolve()),
                "errors": [{"stage": "scenario", "message": "Skipped because static validation failed."}],
                "scenarios": [],
            }
        report["scenario"] = scenario_report

    overall_ok = bool(report.get("ok")) and (scenario_report is None or bool(scenario_report.get("ok")))
    if as_json:
        typer.echo(json.dumps(report, indent=2))
    else:
        _print_static_report(file, report, overall_ok=overall_ok)
        if scenario_report is not None:
            _print_scenario_report(scenario_report)
    raise typer.Exit(code=0 if overall_ok else 1)


@app.command()
def sync(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the .jsx module or interface directory.",
    ),
    interface_id: int | None = typer.Option(None, "--id", help="Existing interface id. Defaults to sidecar lookup."),
    title: str | None = typer.Option(None, "--title", help="Interface title. Defaults to the filename."),
    workspace_id: int | None = typer.Option(None, "--workspace", help="Workspace id for a newly created interface."),
    workspace_title: str | None = typer.Option(
        None, "--workspace-title", help="Workspace title for a newly created interface."
    ),
    token: str | None = typer.Option(None, "--token", envvar="LABEL_STUDIO_API_KEY", help="Label Studio API token."),
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
    no_validate: bool = typer.Option(
        False, "--no-validate", help="Skip validation gate; compilation is still required."
    ),
    force: bool = typer.Option(False, "--force", help="Sync even when the source hash is unchanged."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen without writing to the server."),
    message: str | None = typer.Option(None, "--message", help="History message for this synced version."),
    publish: bool = typer.Option(False, "--publish", help="Create a published version instead of a local draft."),
) -> None:
    """Create or update a saved interface from a local file."""
    file = _resolve_interface_file(file)
    _sync_interface(
        ctx=ctx,
        file=file,
        interface_id=interface_id,
        title=title,
        workspace_id=workspace_id,
        workspace_title=workspace_title,
        token=token,
        lse_url=lse_url,
        no_validate=no_validate,
        force=force,
        dry_run=dry_run,
        message=message,
        publish=publish,
    )


@app.command()
def pull(
    ctx: typer.Context,
    directory: Path = typer.Argument(Path("."), file_okay=False, help="Directory to write the interface bundle into."),
    interface_id: int = typer.Option(..., "--id", help="Saved interface id."),
    version_id: int | None = typer.Option(
        None, "--version", min=0, help="Stable version id to pull. Defaults to the latest version."
    ),
    token: str | None = typer.Option(None, "--token", envvar="LABEL_STUDIO_API_KEY", help="Label Studio API token."),
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing local bundle files."),
) -> None:
    """Pull a saved interface into a local bundle."""
    resolved_token = _resolve_token(ctx, token)
    if not resolved_token:
        typer.echo("error: --token or LABEL_STUDIO_API_KEY is required", err=True)
        raise typer.Exit(code=2)

    base = _resolve_base_url(ctx, lse_url)
    headers = _auth_headers(resolved_token, base_url=base)
    with httpx.Client(headers=headers, timeout=30.0) as client:
        try:
            resp = client.get(f"{base}/api/interfaces/{interface_id}/")
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            _surface_http_error(exc)
            raise typer.Exit(code=1) from None

    if not _is_record(data):
        typer.echo("error: interface API response was not a JSON object", err=True)
        raise typer.Exit(code=1)

    versions = [version for version in data.get("versions") or [] if _is_record(version)]
    selected = _find_version(versions, version_id)
    if selected is None and version_id is not None:
        typer.echo(f"error: interface #{interface_id} has no version {version_id}", err=True)
        raise typer.Exit(code=2)

    source_version: int | None
    selected_version: dict[str, Any] | None
    if selected is None:
        source_version = None
        selected_version = None
    else:
        source_version, selected_version = selected

    source = selected_version.get("code") if selected_version is not None else None
    if not isinstance(source, str) or not source:
        source = data.get("code")
    if not isinstance(source, str) or not source:
        typer.echo("error: interface response did not include source code", err=True)
        raise typer.Exit(code=1)

    params_schema = selected_version.get("paramsSchema") if selected_version is not None else None
    if not _is_record(params_schema):
        metadata = data.get("metadata")
        params_schema = metadata.get("paramsSchema") if _is_record(metadata) else None
    params_defaults = _schema_defaults(params_schema)

    task_data = data.get("data_sample")
    if not _is_record(task_data):
        task_data = {}

    directory = directory.resolve()
    screen_path = directory / "Screen.jsx"
    task_path = directory / "task.json"
    params_path = directory / "params.json"
    planned_files = [screen_path, task_path, _sidecar_path(screen_path)]
    if params_defaults:
        planned_files.append(params_path)

    existing = [path for path in planned_files if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        typer.echo(f"error: refusing to overwrite existing files: {names}. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    directory.mkdir(parents=True, exist_ok=True)
    source_to_write = source.rstrip() + "\n"
    _write_bundle_file(screen_path, source_to_write, force=force)
    _write_bundle_file(task_path, _json_file_contents(task_data), force=force)
    if params_defaults:
        _write_bundle_file(params_path, _json_file_contents(params_defaults), force=force)

    source_hash = _source_hash(source)
    sidecar = {
        base: {
            "interface_id": interface_id,
            "title": data.get("title"),
            "workspace": data.get("workspace"),
            "source_version": source_version,
            "last_pushed_hash": source_hash,
            "last_pushed_at": datetime.now(timezone.utc).isoformat(),
        }
    }
    sidecar_path = _write_sidecar(screen_path, sidecar)
    typer.echo(f"wrote {sidecar_path}")
    typer.echo(typer.style(f"pulled interface #{interface_id} ({data.get('title', '')})", fg=typer.colors.GREEN))


def _create_project(
    *,
    api_key: str,
    base_url: str,
    title: str,
    description: str,
    workspace_id: int | None,
    interface_id: int,
    source_version: int | None,
    params: Any,
) -> Any:
    from label_studio_sdk import LabelStudio

    client = LabelStudio(api_key=api_key, base_url=base_url)
    return client.projects.create(
        title=title,
        description=description,
        workspace=workspace_id,
        is_draft=False,
        label_config="<View></View>",
        use_custom_interface=True,
        source_interface_id=interface_id,
        source_interface_version=source_version,
        custom_interface_params=params,
    )


def _project_id(project: Any) -> int | None:
    if isinstance(project, dict):
        return project.get("id")
    return getattr(project, "id", None)


@app.command()
def start(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the .jsx module or interface directory.",
    ),
    project_title: str | None = typer.Option(
        None, "--project-title", help="Project title. Defaults to interface title."
    ),
    description: str = typer.Option("", "--description", help="Project description."),
    params: Path | None = typer.Option(
        None,
        "--params",
        exists=True,
        dir_okay=False,
        readable=True,
        help="JSON file with custom interface params for the project.",
    ),
    interface_id: int | None = typer.Option(None, "--id", help="Existing interface id. Defaults to sidecar lookup."),
    interface_title: str | None = typer.Option(None, "--title", help="Interface title when creating a new interface."),
    workspace_id: int | None = typer.Option(None, "--workspace", help="Workspace id for the interface/project."),
    workspace_title: str | None = typer.Option(None, "--workspace-title", help="Workspace title for the interface."),
    token: str | None = typer.Option(None, "--token", envvar="LABEL_STUDIO_API_KEY", help="Label Studio API token."),
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
    no_validate: bool = typer.Option(
        False, "--no-validate", help="Skip validation gate; compilation is still required."
    ),
    force: bool = typer.Option(False, "--force", help="Sync even when the source hash is unchanged."),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open the created project."),
) -> None:
    """Sync an interface, then create a project from it."""
    resolved_token = _resolve_token(ctx, token)
    if not resolved_token:
        typer.echo("error: --token or LABEL_STUDIO_API_KEY is required", err=True)
        raise typer.Exit(code=2)

    source_path = file
    params = _resolve_bundle_file(source_path, params, PARAMS_FILE_CANDIDATES)
    file = _resolve_interface_file(source_path)
    sync_result = _sync_interface(
        ctx=ctx,
        file=file,
        interface_id=interface_id,
        title=interface_title,
        workspace_id=workspace_id,
        workspace_title=workspace_title,
        token=resolved_token,
        lse_url=lse_url,
        no_validate=no_validate,
        force=force,
        dry_run=False,
        message=None,
        publish=True,
    )
    if sync_result is None:
        raise typer.Exit(code=2)

    project_params = _load_json_file(params, label="params file") if params else None
    base = _resolve_base_url(ctx, lse_url)
    title = project_title or f"{sync_result.title} Project"
    project = _create_project(
        api_key=resolved_token,
        base_url=base,
        title=title,
        description=description,
        workspace_id=workspace_id or sync_result.workspace_id,
        interface_id=sync_result.interface_id,
        source_version=sync_result.source_version,
        params=project_params,
    )
    project_id = _project_id(project)
    if project_id is None:
        typer.echo("created project, but the SDK response did not include an id", err=True)
        return
    project_url = f"{base}/projects/{project_id}/data"
    typer.echo(typer.style(f"created project #{project_id} ({title!r})", fg=typer.colors.GREEN))
    typer.echo(f"project: {project_url}")
    if not no_open:
        webbrowser.open(project_url)


SCREEN_TEMPLATE = """const labels = ["Positive", "Negative"];

function Screen({ task, regions, setRegions }) {
  const text = task.data?.text ?? "Add text in task.json";

  const choose = (label) => {
    const region = {
      id: crypto.randomUUID(),
      type: "choices",
      from_name: "sentiment",
      to_name: "text",
      value: { choices: [label] },
    };
    setRegions([region]);
  };

  return (
    <div style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <p>{text}</p>
      <div style={{ display: "flex", gap: 8 }}>
        {labels.map((label) => (
          <button key={label} type="button" onClick={() => choose(label)}>
            {label}
          </button>
        ))}
      </div>
      <pre>{JSON.stringify(regions, null, 2)}</pre>
    </div>
  );
}

function getResults(regions) {
  return regions;
}

function parseResults(results) {
  return { regions: results };
}

({
  default: Screen,
  getResults,
  parseResults,
  inputSchema: {
    type: "object",
    properties: {
      text: { type: "dataField", default: "text" },
    },
  },
  outputSchema: {
    type: "object",
    properties: {
      sentiment: { type: "string", enum: labels },
    },
  },
});
"""

TASK_TEMPLATE = """{
  "text": "The interface CLI is ready to use."
}
"""

SCENARIO_TEMPLATE = """export default [
  {
    name: "selects a label",
    task: {
      data: {
        text: "The interface CLI is ready to use."
      }
    },
    async run({ page }) {
      await page.getByRole("button", { name: "Positive" }).click();
    },
    expect: {
      visibleText: ["The interface CLI is ready to use."],
      results: [
        {
          from_name: "sentiment",
          type: "choices",
          value: { choices: ["Positive"] }
        }
      ]
    }
  }
];
"""


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), file_okay=False, help="Directory to scaffold into."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing scaffold files."),
) -> None:
    """Create starter interface files."""
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    files = {
        directory / "Screen.jsx": SCREEN_TEMPLATE,
        directory / "task.json": TASK_TEMPLATE,
        directory / "scenarios.js": SCENARIO_TEMPLATE,
    }
    existing = [path for path in files if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        typer.echo(f"error: refusing to overwrite existing files: {names}. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    for path, contents in files.items():
        path.write_text(contents, encoding="utf-8")
        typer.echo(f"wrote {path}")


@app.command()
def open(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the .jsx module or interface directory.",
    ),
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
    no_open: bool = typer.Option(False, "--no-open", help="Only print the URL."),
) -> None:
    """Open the saved interface from this file's sidecar."""
    file = _resolve_interface_file(file)
    base = _resolve_base_url(ctx, lse_url)
    sidecar_entry = _read_sidecar(file.resolve()).get(base)
    if not sidecar_entry or not sidecar_entry.get("interface_id"):
        typer.echo(f"error: no sidecar entry for {base}. Run `label-studio-sdk interface sync` first.", err=True)
        raise typer.Exit(code=2)
    url = f"{base}/interfaces/{sidecar_entry['interface_id']}/overview"
    typer.echo(url)
    if not no_open:
        webbrowser.open(url)


@app.command()
def doctor(
    ctx: typer.Context,
    lse_url: str | None = typer.Option(
        None,
        "--lse-url",
        "--base-url",
        envvar="LABEL_STUDIO_URL",
        help="Base URL of the Label Studio instance.",
    ),
) -> None:
    """Check local interface development prerequisites."""
    checks: list[tuple[str, bool, str]] = []
    checks.append(("node", shutil.which("node") is not None, shutil.which("node") or "missing"))
    checks.append(("npm", shutil.which("npm") is not None, shutil.which("npm") or "missing"))
    token = _resolve_token(ctx)
    checks.append(("LABEL_STUDIO_API_KEY", bool(token), "set" if token else "missing"))

    try:
        cache_dir = _ensure_validator_ready(require_scenario=True)
        checks.append(("validator cache", True, str(cache_dir)))
    except typer.Exit:
        checks.append(("validator cache", False, "not ready"))

    base = _resolve_base_url(ctx, lse_url)
    try:
        response = httpx.get(base, timeout=5.0)
        checks.append(("Label Studio URL", response.status_code < 500, f"{base} -> HTTP {response.status_code}"))
    except httpx.HTTPError as exc:
        checks.append(("Label Studio URL", False, f"{base} -> {exc}"))

    ok = True
    for name, passed, detail in checks:
        ok = ok and passed
        typer.echo(f"{'OK' if passed else 'FAIL'} {name}: {detail}")
    raise typer.Exit(code=0 if ok else 1)
