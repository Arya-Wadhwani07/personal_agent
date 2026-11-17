# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Fail closed if a release is launched with privilege outside the reviewed profile."""

import ctypes
import os
from pathlib import Path


def enforce():
    if os.geteuid() == 0:
        raise RuntimeError("The assistant must run as a non-root user")
    fields = dict(
        line.split(":", 1)
        for line in Path("/proc/self/status").read_text().splitlines()
        if ":" in line
    )
    if int(fields["CapEff"].strip(), 16) != 0:
        raise RuntimeError("The assistant must run without effective capabilities")
    libc = ctypes.CDLL(None, use_errno=True)
    # PR_SET_NO_NEW_PRIVS is inherited by every child and cannot be undone.
    if libc.prctl(38, 1, 0, 0, 0) != 0:
        raise RuntimeError("Cannot enforce no-new-privileges")
