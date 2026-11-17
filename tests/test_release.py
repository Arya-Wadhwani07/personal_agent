# I developed this file with Codex assistance; see PROCESS_LOG.md.
import ast
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
    "A3_BUDGET_USD": "4",
    "A3_IMAGE": "us-west1-docker.pkg.dev/synthetic-project/a3/agent@sha256:" + "a" * 64,
}
GATE = {
    "primary_auth": "oauth",
    "oauth_secret_version": "1",
    "project": "synthetic-project",
    "budget_usd": 4,
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
    ast.parse(Path(deploy.__file__).read_text(), feature_version=(3, 11))


@pytest.mark.parametrize("budget", ["4.01", "5", "-1", "nan", "Infinity", "-Infinity", "invalid"])
def test_budget_cannot_exceed_approval_or_bypass_with_nonfinite_values(budget):
    with pytest.raises(ValueError):
        deploy.command({**ENV, "A3_BUDGET_USD": budget}, GATE)


def test_different_valid_project_and_own_image_are_still_refused():
    alternate = {
        **ENV,
        "A3_GCP_PROJECT": "unapproved-project",
        "A3_IMAGE": "us-west1-docker.pkg.dev/unapproved-project/a3/agent@sha256:" + "b" * 64,
    }
    with pytest.raises(ValueError, match="reviewed release gate"):
        deploy.command(alternate, GATE)


@pytest.mark.parametrize("ceiling", [None, "nan", "Infinity", 0, -1])
def test_missing_or_invalid_authorization_is_fail_closed(ceiling):
    with pytest.raises(ValueError):
        deploy.command(ENV, {**GATE, "budget_usd": ceiling})


def test_lower_declared_budget_is_allowed_but_truthy_readiness_is_not():
    assert deploy.command({**ENV, "A3_BUDGET_USD": "3.50"}, GATE)
    with pytest.raises(ValueError):
        deploy.command(ENV, {**GATE, "ready": "false"})


def test_oauth_release_mounts_pinned_native_credentials_without_paid_key():
    command = deploy.command(ENV, GATE)
    mapping = command[command.index("--set-secrets") + 1]
    assert "/run/a3-oauth/auth.json=a3-hermes-oauth:1" in mapping
    assert "A3_OPENAI_API_KEY" not in mapping
    with pytest.raises(ValueError):
        deploy.command(ENV, {**GATE, "oauth_secret_version": "latest"})

    with pytest.raises(ValueError, match="requires Hermes OAuth"):
        deploy.command(ENV, {**GATE, "primary_auth": "api_key"})
