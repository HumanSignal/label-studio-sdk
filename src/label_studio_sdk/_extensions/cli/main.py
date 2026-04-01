from __future__ import annotations

import inspect
import json
import os
import re
import typing
from typing import Any, get_args, get_origin

import click
import pydantic
import typer

from label_studio_sdk import LabelStudio
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


def _discover_services(client: LabelStudio) -> list[str]:
    # Discover SDK service groups from declared @property attributes on client classes.
    # This captures generated clients and extension clients.
    service_names: set[str] = set()
    for cls in type(client).mro():
        for name, attr in cls.__dict__.items():
            if name.startswith("_") or not isinstance(attr, property):
                continue
            service_names.add(name)

    services: list[str] = []
    for name in sorted(service_names):
        try:
            value = getattr(client, name)
        except Exception:
            continue
        if callable(value):
            continue
        if any(ch.isupper() for ch in name):
            continue
        if _discover_methods(value):
            services.append(name)
    return sorted(set(services))


def _discover_methods(service_obj: Any) -> list[str]:
    methods: list[str] = []
    for name in dir(service_obj):
        if name.startswith("_"):
            continue
        attr = getattr(service_obj, name)
        if callable(attr):
            methods.append(name)
    return sorted(set(methods))


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


def _raw_callable(method: Any) -> Any:
    return method.__func__ if hasattr(method, "__func__") else method


def _resolve_return_annotation(method: Any) -> Any:
    func = _raw_callable(method)
    mod = inspect.getmodule(func)
    globalns = vars(mod) if mod is not None else {}
    try:
        hints = typing.get_type_hints(func, globalns=globalns, include_extras=True)
    except Exception:
        return None
    return hints.get("return")


def _strip_optional(tp: Any) -> Any:
    """Unpack Optional / Union[..., None]."""
    origin = get_origin(tp)
    args = get_args(tp)
    if origin is typing.Union and args:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return tp


def _annotation_label(tp: Any) -> str:
    if tp is None:
        return "Any"
    if inspect.isclass(tp):
        return tp.__name__
    s = str(tp).replace("typing.", "")
    if len(s) > 120:
        s = s[:117] + "..."
    # Typer/Rich help parses "[" as Markdown links; use fullwidth brackets for display.
    return s.replace("[", "［").replace("]", "］")


def _format_model_fields(model_cls: type[pydantic.BaseModel]) -> str:
    fields = getattr(model_cls, "model_fields", None)
    if not fields:
        return ""

    lines: list[str] = []
    for name in fields:
        finfo = fields[name]
        ann = getattr(finfo, "annotation", None)
        desc = getattr(finfo, "description", None) or ""
        ann_s = _annotation_label(ann) if ann is not None else ""
        type_part = f"`{ann_s}`" if ann_s else "`Any`"
        if desc:
            lines.append(f"  {name}: {type_part}\n    {desc}")
        else:
            lines.append(f"  {name}: {type_part}")
    return "\n".join(lines)


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


def _expand_return_type_for_help(ret: Any) -> str | None:
    if ret is None:
        return None

    origin = get_origin(ret)
    args = get_args(ret)

    if origin is list and args:
        inner = _strip_optional(args[0])
        if inspect.isclass(inner) and issubclass(inner, pydantic.BaseModel):
            body = _format_model_fields(inner)
            if body:
                return f"Return value: list of {inner.__name__}\nEach element fields:\n{body}"

    inner = _strip_optional(ret)
    if inspect.isclass(inner) and issubclass(inner, pydantic.BaseModel):
        body = _format_model_fields(inner)
        if body:
            return f"Return value fields ({inner.__name__}):\n{body}"

    return None


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


# Introspection-only client: use a closed port so we never hit a real LS instance (e.g. dev on :8080).
_discovery_client = LabelStudio(api_key="POC_KEY", base_url="http://127.0.0.1:9")


def _make_method_command(service_name: str, method_name: str):
    service_obj = getattr(_discovery_client, service_name)
    method = getattr(service_obj, method_name)
    signature = str(inspect.signature(method))
    raw_api_doc = _sanitize_sdk_docstring_for_cli(inspect.getdoc(method) or "")
    summary = _extract_summary(raw_api_doc)
    api_doc = raw_api_doc
    return_expansion = _expand_return_type_for_help(_resolve_return_annotation(method))
    if return_expansion:
        api_doc = api_doc.rstrip() + ("\n\n" if api_doc else "") + return_expansion

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


for _service in _discover_services(_discovery_client):
    service_app = typer.Typer(
        help=_service,
        context_settings={"help_option_names": ["--help"]},
    )
    service_obj = getattr(_discovery_client, _service)
    for _method in _discover_methods(service_obj):
        service_app.command(name=_method.replace("_", "-"))(_make_method_command(_service, _method))
    app.add_typer(service_app, name=_service.replace("_", "-"))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

