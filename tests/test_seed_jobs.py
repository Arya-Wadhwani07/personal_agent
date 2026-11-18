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


def test_native_scheduler_executes_installed_scripts_and_rejects_escape(tmp_path):
    root = Path(__file__).parents[1]
    code = r"""
import importlib.util, os, threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from cron.scheduler_script import _run_job_script
spec = importlib.util.spec_from_file_location("seed", "scripts/seed_jobs.py")
seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed)
seed.install_scripts()
seen = []
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        assert self.headers.get("Authorization") == "Bearer synthetic-internal-check"
        seen.append(self.path)
        self.send_response(200); self.end_headers(); self.wfile.write(b'{}')
    def log_message(self, *args):
        pass
server = ThreadingHTTPServer(("127.0.0.1", 8090), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
try:
    for name in ("checkpoint.py", "alerts.py"):
        ok, output = _run_job_script(name)
        assert ok, output
        assert "[SILENT]" in output
    assert seen == ["/checkpoint", "/jobs/alerts"]
    ok, output = _run_job_script(str(Path("scripts/checkpoint.py").resolve()))
    assert not ok and "outside the scripts directory" in output
    target = Path(os.environ["HERMES_HOME"]) / "scripts" / "checkpoint.py"
    target.unlink(); target.symlink_to(Path("scripts/checkpoint.py").resolve())
    try:
        seed.install_scripts()
    except RuntimeError as exc:
        assert "symlink" in str(exc)
    else:
        raise AssertionError("Symlink entrypoint accepted")
finally:
    server.shutdown();server.server_close()
"""
    env = dict(os.environ, HERMES_HOME=str(tmp_path / "hermes"),
               A3_INTERNAL_KEY="synthetic-internal-check")
    result = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
