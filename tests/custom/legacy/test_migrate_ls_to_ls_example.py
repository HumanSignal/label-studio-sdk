import importlib.util
from pathlib import Path


EXAMPLE_PATH = Path(__file__).parents[3] / "examples" / "migrate_ls_to_ls" / "migrate-ls-to-ls.py"


def load_migration_module():
    spec = importlib.util.spec_from_file_location("migrate_ls_to_ls_example", EXAMPLE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_defaults_to_smaller_chunks():
    module = load_migration_module()

    assert module.CHUNK_SIZE == 50


def test_migration_sets_sdk_and_session_timeouts(monkeypatch):
    module = load_migration_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def request(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return "ok"

    class DummyClient:
        def __init__(self, **kwargs):
            self.session = DummySession()

    monkeypatch.setattr(module, "Client", DummyClient)

    migration = module.Migration(
        src_url="http://source",
        src_key="source-token",
        dst_url="http://destination",
        dst_key="destination-token",
        dest_workspace=None,
        connect_timeout=2.0,
        request_timeout=30.0,
    )

    assert module.legacy_client.TIMEOUT == (2.0, 30.0)

    migration.src_ls.session.request("GET", "http://source/api/version")
    assert migration.src_ls.session.calls[-1][1]["timeout"] == (2.0, 30.0)

    migration.dst_ls.session.request(
        "GET",
        "http://destination/api/version",
        timeout=(1.0, 5.0),
    )
    assert migration.dst_ls.session.calls[-1][1]["timeout"] == (1.0, 5.0)
