from __future__ import annotations

import json
from typing import Any

from typer.testing import CliRunner

from label_studio_sdk import LabelStudio
from label_studio_sdk._extensions.cli import main as cli_main
from label_studio_sdk._extensions.cli.main import app as root_app

runner = CliRunner()


def _is_sync_client_instance(attr: Any) -> bool:
    if attr is None or callable(attr):
        return False
    name = type(attr).__name__
    if name.startswith(("Async", "Raw")):
        return False
    return name.endswith("Client") or name.endswith("ClientExt")


def _runtime_walk(service_obj: Any) -> dict[str, Any]:
    methods: dict[str, str] = {}
    children: dict[str, Any] = {}
    for method_name in dir(service_obj):
        if method_name.startswith("_") or method_name == "with_raw_response":
            continue
        attr: Any = getattr(service_obj, method_name)
        if callable(attr):
            methods[method_name] = cli_main._format_signature_for_help(attr)
        elif _is_sync_client_instance(attr):
            child = _runtime_walk(attr)
            if child["methods"] or child["children"]:
                children[method_name] = child
    return {"methods": methods, "children": children}


def _flatten_tree(tree: dict[str, Any], path: tuple[str, ...]) -> dict[str, dict[str, str]]:
    flat: dict[str, dict[str, str]] = {}
    key = ".".join(path)
    if tree.get("methods"):
        flat[key] = dict(tree["methods"])
    for child_name, child_tree in (tree.get("children") or {}).items():
        flat.update(_flatten_tree(child_tree, path + (child_name,)))
    return flat


def _signature_tree(tree: dict[str, Any]) -> dict[str, Any]:
    return {
        "methods": {
            name: (meta["signature"] if isinstance(meta, dict) else meta)
            for name, meta in tree.get("methods", {}).items()
        },
        "children": {
            child_name: _signature_tree(child) for child_name, child in tree.get("children", {}).items()
        },
    }


def _runtime_discovery(client: LabelStudio) -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for service_name in cli_main._discover_services():
        service_obj = getattr(client, service_name, None)
        if service_obj is None:
            continue
        tree = _runtime_walk(service_obj)
        if tree["methods"] or tree["children"]:
            discovered.update(_flatten_tree(tree, (service_name,)))
    return discovered


def _ast_discovery() -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for service_name in cli_main._discover_services():
        tree = cli_main._discover_client_tree((service_name,))
        if tree["methods"] or tree["children"]:
            discovered.update(_flatten_tree(_signature_tree(tree), (service_name,)))
    return discovered


def test_cli_ast_discovery_matches_runtime_methods_and_signatures() -> None:
    # Use closed local address to avoid talking to a real Label Studio server.
    runtime_client = LabelStudio(api_key="POC_KEY", base_url="http://127.0.0.1:9")
    runtime = _runtime_discovery(runtime_client)
    ast = _ast_discovery()

    assert set(ast) == set(runtime), (
        "CLI AST-discovered services differ from runtime services.\n"
        f"Only in AST: {sorted(set(ast) - set(runtime))}\n"
        f"Only in runtime: {sorted(set(runtime) - set(ast))}"
    )

    for service_name in sorted(runtime):
        runtime_methods = runtime[service_name]
        ast_methods = ast[service_name]

        assert set(ast_methods) == set(runtime_methods), (
            f"Method discovery mismatch for service '{service_name}'.\n"
            f"Only in AST: {sorted(set(ast_methods) - set(runtime_methods))}\n"
            f"Only in runtime: {sorted(set(runtime_methods) - set(ast_methods))}"
        )

        mismatched_signatures: list[str] = []
        for method_name in sorted(runtime_methods):
            runtime_sig = runtime_methods[method_name]
            ast_sig = ast_methods[method_name]
            if ast_sig != runtime_sig:
                mismatched_signatures.append(
                    f"{service_name}.{method_name}\n"
                    f"  AST:     {ast_sig}\n"
                    f"  runtime: {runtime_sig}"
                )

        assert not mismatched_signatures, (
            "Signature extraction mismatch between CLI AST parsing and runtime introspection:\n"
            + "\n\n".join(mismatched_signatures)
        )


def test_cli_discovers_nested_projects_stats_methods() -> None:
    tree = cli_main._discover_client_tree(("projects",))
    assert "stats" in tree["children"]
    stats_methods = tree["children"]["stats"]["methods"]
    assert "label_distribution_counts" in stats_methods
    assert "label_distribution_structure" in stats_methods


def test_cli_nested_stats_help_and_dry_run() -> None:
    help_result = runner.invoke(root_app, ["projects", "stats", "--help"])
    assert help_result.exit_code == 0, help_result.output
    assert "label-distribution-counts" in help_result.output

    dry = runner.invoke(
        root_app,
        [
            "projects",
            "stats",
            "label-distribution-counts",
            "--param",
            "id=1",
            "--dry-run",
        ],
    )
    assert dry.exit_code == 0, dry.output
    payload = json.loads(dry.output)
    assert payload["service"] == "projects.stats"
    assert payload["method"] == "label_distribution_counts"
    assert payload["kwargs"] == {"id": 1}


def test_cli_registers_nested_only_top_level_services() -> None:
    help_result = runner.invoke(root_app, ["--help"])
    assert help_result.exit_code == 0, help_result.output
    assert "analytics" in help_result.output
    assert "sso" in help_result.output
    assert "import-storage" in help_result.output

    analytics_help = runner.invoke(root_app, ["analytics", "--help"])
    assert analytics_help.exit_code == 0, analytics_help.output
    assert "kpis" in analytics_help.output
