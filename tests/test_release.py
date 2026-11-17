# I developed this file with Codex assistance; see PROCESS_LOG.md.
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "deploy", Path(__file__).parents[1] / "scripts/deploy.py"
)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
ENV = {
    "A3_GCP_PROJECT": "synthetic-project",
    "A3_REGION": "us-west1",
    "A3_BUDGET_USD": "5",
    "A3_IMAGE": "us-west1-docker.pkg.dev/synthetic-project/a3/agent@sha256:" + "a" * 64,
}
GATE = {
    "ready": True,
    "frozen": False,
    "blockers": [],
    "instance": "a3-test",
    "cpu": "1",
    "memory": "2Gi",
}


@pytest.mark.parametrize(
    "change", [{"frozen": True}, {"ready": False}, {"blockers": ["unfinished state"]}]
)
def test_release_gates(change):
    with pytest.raises(ValueError):
        deploy.command(ENV, {**GATE, **change})


def test_digest_and_budget_required():
    for changes in ({"A3_BUDGET_USD": "0"}, {"A3_IMAGE": "latest"}, {"A3_GCP_PROJECT": ""}):
        with pytest.raises(ValueError):
            deploy.command({**ENV, **changes}, GATE)


def test_instance_resource_not_service():
    command = deploy.command(ENV, GATE)
    assert command[:5] == ["gcloud", "beta", "run", "instances", "deploy"]
