from typing import Any

from label_studio_sdk import LabelStudio
from label_studio_sdk._extensions.cli import main as cli_main


def _runtime_service_names_from_label_studio() -> list[str]:
    service_names: set[str] = set()
    for cls in LabelStudio.mro():
        for name, attr in cls.__dict__.items():
            if name.startswith("_") or not isinstance(attr, property):
                continue
            if any(ch.isupper() for ch in name):
                continue
            service_names.add(name)
    return sorted(service_names)


def _runtime_discovery(client: LabelStudio) -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for service_name in _runtime_service_names_from_label_studio():
        service_obj = getattr(client, service_name, None)
        if service_obj is None:
            continue

        methods: dict[str, str] = {}
        for method_name in dir(service_obj):
            if method_name.startswith("_") or method_name == "with_raw_response":
                continue
            attr: Any = getattr(service_obj, method_name)
            if not callable(attr):
                continue
            methods[method_name] = cli_main._format_signature_for_help(attr)

        if methods:
            discovered[service_name] = methods

    return discovered


def _ast_discovery() -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for service_name in cli_main._discover_services():
        methods_meta = cli_main._discover_methods(service_name)
        if methods_meta:
            discovered[service_name] = {
                method_name: method_meta["signature"]
                for method_name, method_meta in methods_meta.items()
            }
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
