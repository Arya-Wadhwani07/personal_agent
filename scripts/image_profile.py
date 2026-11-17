# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Verify the exact runtime conditions supporting component-specific scan triage."""
import ctypes
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path
from types import SimpleNamespace

from hermes_cli.web_server_boundary import ws_host_origin_reason

from personal_agent.api import edge_app
from personal_agent.isolation import enforce
from personal_agent.settings import Settings


def require(condition):
    if not condition:
        raise RuntimeError("Image profile verification failed")


def main():
    enforce()
    require(sqlite3.sqlite_version == "3.54.1")
    # Fixed ACL ABI is present in the replacement package, not just a version label.
    lib = ctypes.CDLL("libacl.so.1")
    require(lib.acl_get_file_at and lib.acl_set_file_at)
    absent = ["/usr/bin/mount", "/usr/bin/umount", "/usr/bin/nsenter", "/usr/bin/infocmp",
              "/usr/lib/systemd/systemd-homed"]
    require(all(not Path(p).exists() for p in absent))
    require(not list(Path("/usr/share/perl").rglob("Archive/Tar.pm")))
    require(not list(Path("/usr/lib").rglob("Archive/Tar.pm")))
    elevated = []
    for base in ("/usr", "/opt"):
        for p in Path(base).rglob("*"):
            if not p.is_symlink() and p.is_file() and p.stat().st_mode & (stat.S_ISUID | stat.S_ISGID):
                elevated.append(str(p))
    require(not elevated)
    fields = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    require(int(fields["NoNewPrivs"]) == 1 and int(fields["CapEff"], 16) == 0 and os.geteuid() != 0)
    listener = SimpleNamespace(bound_host="127.0.0.1", bound_port=8081)
    for headers in ({"host": "attacker.test", "origin": "https://attacker.test"},
                    {"host": "127.0.0.1:8081", "origin": "https://attacker.test"}):
        require(ws_host_origin_reason(SimpleNamespace(headers=headers), listener))
    app = edge_app(Settings(api_key="synthetic-public-" + "a" * 32,
                            internal_key="synthetic-internal-" + "b" * 32))
    require(not any("websocket" in type(route).__name__.lower() for route in app.routes))
    proof = {"schema": 1, "uid": os.geteuid(), "caps": 0, "no_new_privileges": True,
             "sqlite": sqlite3.sqlite_version, "acl_fixed_abi": True,
             "removed_utilities": absent, "perl_archive_tar_absent": True,
             "hermes_ws_boundary_rejects_attack": True, "public_websocket_routes": False,
             "setuid_files": elevated}
    proof["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
