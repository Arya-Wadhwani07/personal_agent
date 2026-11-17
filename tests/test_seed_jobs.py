# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Exercise actual native cron persistence in a disposable profile, without dispatching jobs."""
import os
import subprocess
import sys
from pathlib import Path


def test_native_job_reconciliation_preserves_pause_history_and_owner_boundary(tmp_path):
    root = Path(__file__).parents[1]
    code = r"""
import importlib.util
from pathlib import Path
from cron.jobs import create_job, list_jobs, pause_job, update_job
spec = importlib.util.spec_from_file_location("seed", "scripts/seed_jobs.py")
seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed)
assert len(seed.reconcile("1234")) == 5
before = {j["name"]: j for j in list_jobs(include_disabled=True)}
assert seed.reconcile("1234") == []
assert len(list_jobs(include_disabled=True)) == 5
morning = before["a3-morning"]
pause_job(morning["id"], reason="Synthetic operator pause")
update_job(morning["id"], {"prompt": "obsolete prompt", "last_status": "success"})
create_job(name="unrelated", prompt="Synthetic unrelated job", schedule="0 12 * * *", deliver="local")
changes = seed.reconcile("5678")
after = {j["name"]: j for j in list_jobs(include_disabled=True)}
assert after["a3-morning"]["id"] == morning["id"]
assert after["a3-morning"]["enabled"] is False
assert after["a3-morning"]["state"] == "paused"
assert after["a3-morning"]["paused_reason"] == "Synthetic operator pause"
assert after["a3-morning"]["last_status"] == "success"
assert after["a3-morning"]["prompt"] != "obsolete prompt"
assert after["a3-morning"]["deliver"] == "telegram:5678"
assert after["unrelated"]["enabled"] is True
assert "a3_review_content" in after["a3-content"]["prompt"]
assert seed.reconcile("5678") == []
seed.reconcile("")
after = {j["name"]: j for j in list_jobs(include_disabled=True)}
assert after["a3-checkpoint"]["enabled"] is True
assert after["unrelated"]["enabled"] is True
assert all(not after[n]["enabled"] for n in seed.MANAGED_NAMES - {"a3-checkpoint"})
seed.reconcile("5678")
after = {j["name"]: j for j in list_jobs(include_disabled=True)}
assert all(not after[n]["enabled"] for n in seed.MANAGED_NAMES - {"a3-checkpoint"})
create_job(name="a3-morning", prompt="Duplicate", schedule="0 8 * * *")
try:
    seed.reconcile("5678")
except RuntimeError as exc:
    assert "Duplicate" in str(exc)
else:
    raise AssertionError("Duplicate managed job was accepted")
print("Native schedule reconciliation passed")
"""
    env = dict(os.environ, HERMES_HOME=str(tmp_path / "hermes"), HOME=str(tmp_path / "home"))
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=root, env=env, capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Native schedule reconciliation passed" in result.stdout
