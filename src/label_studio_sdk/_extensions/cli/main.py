from __future__ import annotations

import inspect
import importlib
import json
import os
import re
from ast import AsyncFunctionDef, ClassDef, FunctionDef, get_docstring, parse as ast_parse, unparse as ast_unparse
from functools import lru_cache
from pathlib import Path
from typing import Any

import click
import typer

from label_studio_sdk.base_client import LabelStudioBase
from label_studio_sdk.version import __version__ as _SDK_VERSION

# Fern/OpenAPI docs embed MDX-style <Card> blocks in some SDK docstrings; plain text for terminal CLI.
_CARD_BLOCK_RE = re.compile(r"<Card\b[^>]*>.*?</Card>", re.IGNORECASE | re.DOTALL)
_P_IN_CARD_RE_COM = re.compile(r"<p\b[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _html_to_plain(fragment: str) -> str:
    plain = _HTML_TAG_RE.sub("", fragment)
    plain = _MD_LINK_RE.sub(r"\1 (\2)", plain)
    return " ".join(plain.split())


def _enterprise_card_to_plain(match: re.Match[str]) -> str:
    block = match.group(0)
    paras = [_html_to_plain(p) for p in _P_IN_CARD_RE_COM.findall(block)]
    paras = [p for p in paras if p]
    if not paras:
        return ""
    paras[0] = f"✨ {paras[0]}"
    return "\n\n" + "\n\n".join(paras) + "\n\n"


_ENTERPRISE_NOTICE_HINT_RE = re.compile(
    r"not available in Label Studio Community",
    re.IGNORECASE,
)


def _join_enterprise_notice_with_following_lede(doc: str) -> str:
    """Keep enterprise text first; merge next short paragraph into the same block for group `help`.

    Click uses only the first \\n\\n-separated paragraph for command-list text; without this,
    the API summary after the notice would disappear from `projects --help`.
    """
    parts = [p.strip() for p in re.split(r"\n\n+", doc.strip()) if p.strip()]
    if (
        len(parts) >= 2
        and _ENTERPRISE_NOTICE_HINT_RE.search(parts[0])
        and not _ENTERPRISE_NOTICE_HINT_RE.search(parts[1])
    ):
        merged = f"{parts[0]} {parts[1]}"
        return "\n\n".join([merged, *parts[2:]])
    return doc


def _sanitize_sdk_docstring_for_cli(doc: str) -> str:
    """Replace enterprise <Card> blocks with their text; flatten remaining Markdown links."""
    if not doc:
        return doc
    text = _CARD_BLOCK_RE.sub(_enterprise_card_to_plain, doc)
    text = _MD_LINK_RE.sub(r"\1 (\2)", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = _join_enterprise_notice_with_following_lede(text.strip())
    return text


app = typer.Typer(
    help=(
        "Auto-generated SDK CLI from the Label Studio Python SDK.\n\n"
        "Endpoint commands (e.g. projects create) accept -h for minimal help "
        "(summary, SDK signature, and options). Use --help for full documentation. "
        "Service groups such as projects only register --help, not -h.\n\n"
        "Use --install-completion to set up tab completion for your shell "
        "(or --show-completion to print the script)."
    ),
    # Leave -h free for per-command minimal help; full docs use --help only.
    context_settings={"help_option_names": ["--help"]},
)


def _discover_services() -> list[str]:
    # Discover SDK service groups from declared @property attributes on base client class
    # without materializing service instances (which imports all service modules).
    service_names: set[str] = set()
    for cls in LabelStudioBase.mro():
        for name, attr in cls.__dict__.items():
            if name.startswith("_") or not isinstance(attr, property):
                continue
            service_names.add(name)
    return sorted(name for name in service_names if not any(ch.isupper() for ch in name))


def _service_client_file(service_name: str) -> Path | None:
    pkg_root = Path(__file__).resolve().parents[2]
    candidate = pkg_root / service_name / "client.py"
    return candidate if candidate.exists() else None


def _service_client_ext_file(service_name: str) -> Path | None:
    pkg_root = Path(__file__).resolve().parents[2]
    candidate = pkg_root / service_name / "client_ext.py"
    return candidate if candidate.exists() else None


@lru_cache(maxsize=1)
def _services_with_label_studio_overrides() -> set[str]:
    pkg_root = Path(__file__).resolve().parents[2]
    client_file = pkg_root / "client.py"
    if not client_file.exists():
        return set()
    module = ast_parse(client_file.read_text(encoding="utf-8"))
    for node in module.body:
        if not isinstance(node, ClassDef) or node.name != "LabelStudio":
            continue
        services: set[str] = set()
        for item in node.body:
            if not isinstance(item, FunctionDef):
                continue
            if any(getattr(dec, "id", None) == "property" for dec in item.decorator_list):
                services.add(item.name)
        return services
    return set()


def _client_class_name(service_name: str, *, ext: bool = False) -> str:
    parts = "".join([part.capitalize() for part in service_name.split("_")])
    return f"{parts}ClientExt" if ext else f"{parts}Client"


def _find_client_class_node(module: Any, service_name: str, *, ext: bool = False) -> ClassDef | None:
    preferred_name = _client_class_name(service_name, ext=ext)
    fallback_suffix = "ClientExt" if ext else "Client"
    class_node = None
    for node in module.body:
        if not isinstance(node, ClassDef):
            continue
        if node.name == preferred_name:
            return node
        if (
            class_node is None
            and node.name.endswith(fallback_suffix)
            and not node.name.startswith(("Async", "Raw"))
        ):
            class_node = node
    return class_node


def _normalize_signature_text(signature: str) -> str:
    # Drop generated OMIT sentinel from displayed signatures.
    signature = re.sub(r"\s*=\s*OMIT", "", signature)
    signature = re.sub(r"\s*=\s*Ellipsis", "", signature)
    signature = re.sub(r"\s*=\s*", "=", signature)
    return _format_type_text_for_help(signature, use_fullwidth_brackets=True)


def _signature_from_class_method(method: Any) -> str:
    signature = str(inspect.signature(method))
    signature = re.sub(r"^\(self,\s*", "(", signature)
    if signature == "(self)":
        signature = "()"
    signature = signature.replace("'typing.", "typing.")
    signature = signature.replace("'", "")
    return _normalize_signature_text(signature)


def _extract_class_method_meta(class_node: ClassDef) -> dict[str, dict[str, str]]:
    methods: dict[str, dict[str, str]] = {}
    for node in class_node.body:
        if not isinstance(node, (FunctionDef, AsyncFunctionDef)):
            continue
        method_name = node.name
        if method_name.startswith("_") or method_name == "with_raw_response":
            continue
        if any(getattr(dec, "id", None) == "property" for dec in node.decorator_list):
            continue

        args_text = ast_unparse(node.args)
        if args_text.startswith("self, "):
            args_text = args_text[len("self, ") :]
        elif args_text == "self":
            args_text = ""
        return_text = ast_unparse(node.returns) if node.returns is not None else ""
        signature = f"({args_text})"
        if return_text:
            signature = f"{signature} -> {return_text}"

        methods[method_name] = {
            "signature": _normalize_signature_text(signature),
            "doc": get_docstring(node) or "",
        }
    return methods


def _resolve_runtime_base_service_class(service_name: str, class_node: ClassDef) -> Any:
    runtime_base_class = None
    try:
        module_name = f"label_studio_sdk.{service_name}.client"
        runtime_module = importlib.import_module(module_name)
        runtime_base_class = getattr(runtime_module, class_node.name, None)
    except Exception:
        runtime_base_class = None
    return runtime_base_class


def _discover_methods(service_name: str) -> dict[str, dict[str, str]]:
    client_file = _service_client_file(service_name)
    if client_file is None:
        return {}

    base_module = ast_parse(client_file.read_text(encoding="utf-8"))
    class_node = _find_client_class_node(base_module, service_name, ext=False)
    if class_node is None:
        return {}

    methods = _extract_class_method_meta(class_node)
    ext_method_names: set[str] = set()

    client_ext_file = _service_client_ext_file(service_name)
    if client_ext_file is not None and service_name in _services_with_label_studio_overrides():
        ext_module = ast_parse(client_ext_file.read_text(encoding="utf-8"))
        ext_class_node = _find_client_class_node(ext_module, service_name, ext=True)
        if ext_class_node is not None:
            # Extension definitions override generated method docs/signatures.
            ext_methods = _extract_class_method_meta(ext_class_node)
            methods.update(ext_methods)
            ext_method_names = set(ext_methods.keys())

    runtime_base_class = _resolve_runtime_base_service_class(service_name, class_node)
    for method_name in list(methods.keys()):
        runtime_method = None
        # Extension signatures come from AST without importing heavy extension modules.
        if method_name not in ext_method_names and runtime_base_class is not None:
            runtime_method = getattr(runtime_base_class, method_name, None)
        if runtime_method is not None and callable(runtime_method):
            methods[method_name]["signature"] = _signature_from_class_method(runtime_method)
    return methods


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _parse_params(items: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise typer.BadParameter(f"Expected key=value, got: {item}")
        key, value = item.split("=", 1)
        parsed[key] = _parse_value(value)
    return parsed


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump(mode="json"))
    if hasattr(value, "dict"):
        return _to_jsonable(value.dict())
    if hasattr(value, "__dict__"):
        return _to_jsonable({k: v for k, v in vars(value).items() if not k.startswith("_")})
    return str(value)


def _format_type_text_for_help(type_text: str, *, use_fullwidth_brackets: bool = True) -> str:
    formatted = type_text.replace("typing.", "")
    formatted = formatted.replace("NoneType", "None")
    formatted = formatted.replace("~", "")
    formatted = re.sub(
        r"\blabel_studio_sdk(?:\.[A-Za-z_][A-Za-z0-9_]*)+\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b",
        r"\g<name>",
        formatted,
    )
    if use_fullwidth_brackets:
        formatted = formatted.replace("[", "［").replace("]", "］")
    return formatted


def _format_request_types_for_help(doc: str) -> str:
    lines = doc.splitlines()
    in_parameters = False
    out_lines: list[str] = []

    for idx, line in enumerate(lines):
        stripped = line.strip()

        if stripped == "Parameters":
            in_parameters = True
            out_lines.append(line)
            continue

        if in_parameters and stripped in {"Returns", "Examples", "Raises", "Notes"}:
            in_parameters = False

        if in_parameters and stripped and set(stripped) == {"-"}:
            out_lines.append(line)
            continue

        if in_parameters:
            m = re.match(r"^(\s*[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$", line)
            if m:
                name = m.group(1).strip()
                type_text = _format_type_text_for_help(m.group(2), use_fullwidth_brackets=True)
                out_lines.append(f"{name} : {type_text}")
                continue

        out_lines.append(line)

    return "\n".join(out_lines)


def _format_signature_for_help(method: Any) -> str:
    # Fast-path formatter: avoid expensive get_type_hints() during CLI bootstrap.
    # SDK methods use string annotations and Ellipsis defaults for OMIT sentinels.
    signature = str(inspect.signature(method))
    signature = signature.replace("'typing.", "typing.")
    signature = signature.replace("'", "")
    return _normalize_signature_text(signature)


def _extract_summary(doc: str | None) -> str:
    """First paragraph of the SDK method docstring (before Parameters / blank line)."""
    if not doc:
        return ""
    lines = doc.strip().splitlines()
    parts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            break
        if stripped == "Parameters" or set(stripped) == {"-"}:
            break
        parts.append(line.strip())
    return "\n".join(parts).strip()


def _get_client(ctx: typer.Context) -> LabelStudio:
    cached = ctx.obj.get("client")
    if cached is not None:
        return cached

    api_key = ctx.obj.get("api_key") or os.getenv("LABEL_STUDIO_API_KEY")
    if not api_key:
        raise typer.BadParameter("Pass --api-key or set LABEL_STUDIO_API_KEY.")

    base_url = ctx.obj.get("base_url") or os.getenv("LABEL_STUDIO_URL")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    # Import lazily so help/listing commands don't pay full SDK import cost.
    from label_studio_sdk import LabelStudio

    client = LabelStudio(**kwargs)
    ctx.obj["client"] = client
    return client


def _root_version_callback(value: bool) -> None:
    if value:
        typer.echo(_SDK_VERSION)
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        "-v",
        help="Show the label-studio-sdk package version and exit.",
        callback=_root_version_callback,
        is_eager=True,
    ),
    api_key: str | None = typer.Option(None, "--api-key", envvar="LABEL_STUDIO_API_KEY"),
    base_url: str | None = typer.Option(None, "--base-url", envvar="LABEL_STUDIO_URL"),
    pretty: bool = typer.Option(True, "--pretty/--compact"),
) -> None:
    ctx.obj = {"api_key": api_key, "base_url": base_url, "pretty": pretty, "client": None}


def _make_method_command(service_name: str, method_name: str, method_meta: dict[str, str]):
    signature = method_meta.get("signature", "()")
    raw_api_doc = _sanitize_sdk_docstring_for_cli(method_meta.get("doc", ""))
    raw_api_doc = _format_request_types_for_help(raw_api_doc)
    summary = _extract_summary(raw_api_doc)
    api_doc = raw_api_doc

    help_suffix = f"\n\n---\nSDK signature: `{service_name}.{method_name}{signature}`"
    method_help = (api_doc + help_suffix).strip() if api_doc else f"SDK signature: `{service_name}.{method_name}{signature}`"
    short_help_body = (
        f"{summary}{help_suffix}" if summary else help_suffix.lstrip()
    ).strip()

    def _short_help_cb(ctx: typer.Context, param: Any, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return
        cmd = ctx.command
        saved_help = cmd.help
        try:
            # Click reads Command.help for format_help_text, not callback.__doc__.
            cmd.help = short_help_body
            click.echo(cmd.get_help(ctx))
        finally:
            cmd.help = saved_help
        raise typer.Exit()

    def _command(
        ctx: typer.Context,
        _minimal_help: bool = typer.Option(
            False,
            "-h",
            help="Minimal help: summary, SDK signature, and options.",
            callback=_short_help_cb,
            is_eager=True,
            is_flag=True,
            expose_value=False,
            hidden=True,
        ),
        param: list[str] = typer.Option(
            [],
            "--param",
            "-p",
            help="Keyword argument as key=value. Value may be JSON.",
        ),
        arg: list[str] = typer.Option(
            [],
            "--arg",
            help="Positional argument value. Value may be JSON. Repeat for multiple args.",
        ),
        body: str | None = typer.Option(
            None,
            "--body",
            help="JSON object merged into kwargs.",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Print target call details without invoking SDK method.",
        ),
    ) -> None:
        kwargs = _parse_params(param)
        args = [_parse_value(v) for v in arg]
        if body:
            body_data = _parse_value(body)
            if not isinstance(body_data, dict):
                raise typer.BadParameter("--body must decode to a JSON object.")
            kwargs = {**body_data, **kwargs}

        if dry_run:
            typer.echo(
                json.dumps(
                    {
                        "service": service_name,
                        "method": method_name,
                        "signature": signature,
                        "args": args,
                        "kwargs": kwargs,
                    },
                    indent=2,
                )
            )
            return

        client = _get_client(ctx)
        service = getattr(client, service_name)
        method = getattr(service, method_name)
        result = method(*args, **kwargs)
        payload = _to_jsonable(result)
        indent = 2 if ctx.obj.get("pretty", True) else None
        typer.echo(json.dumps(payload, indent=indent))

    _command.__name__ = f"{service_name}_{method_name}_command"
    _command.__doc__ = method_help
    return _command


for _service in _discover_services():
    _methods_meta = _discover_methods(_service)
    if not _methods_meta:
        continue
    service_app = typer.Typer(
        help=_service,
        context_settings={"help_option_names": ["--help"]},
    )
    for _method, _meta in _methods_meta.items():
        service_app.command(name=_method.replace("_", "-"))(_make_method_command(_service, _method, _meta))
    app.add_typer(service_app, name=_service.replace("_", "-"))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

