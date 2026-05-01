import importlib
import warnings


def _collect_module_deprecation_warning_messages(module_name: str) -> list[str]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        module = importlib.import_module(module_name)
        importlib.reload(module)
    return [str(warning.message) for warning in caught]


def test_legacy_client_import_has_no_v1_root_validator_deprecation_warning():
    warning_messages = _collect_module_deprecation_warning_messages("label_studio_sdk._legacy.client")

    assert all("V1 style `@root_validator` validators are deprecated" not in message for message in warning_messages)
    assert all("`allow_reuse` is deprecated" not in message for message in warning_messages)


def test_control_tags_import_has_no_v1_validator_deprecation_warning():
    warning_messages = _collect_module_deprecation_warning_messages("label_studio_sdk.label_interface.control_tags")

    assert all("V1 style `@validator` validators are deprecated" not in message for message in warning_messages)


def test_objects_import_has_no_class_config_deprecation_warning():
    warning_messages = _collect_module_deprecation_warning_messages("label_studio_sdk.label_interface.objects")

    assert all("Support for class-based `config` is deprecated" not in message for message in warning_messages)
