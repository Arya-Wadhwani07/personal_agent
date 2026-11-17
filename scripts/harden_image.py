# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Remove unused privileged entrypoints from this container's merged filesystem."""

import os
import stat
from pathlib import Path


def main():
    if os.uname().sysname != "Linux" or os.getuid() != 0 or os.environ.get("A3_IMAGE_BUILD") != "1":
        raise SystemExit("Image-build-only operation")
    for name in ("mount", "umount", "nsenter", "infocmp"):
        for directory in ("/usr/bin", "/usr/sbin", "/bin", "/sbin"):
            (Path(directory) / name).unlink(missing_ok=True)
    for directory in ("/usr", "/opt"):
        for path in Path(directory).rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            mode = path.stat().st_mode
            if mode & (stat.S_ISUID | stat.S_ISGID):
                path.chmod(stat.S_IMODE(mode) & ~(stat.S_ISUID | stat.S_ISGID))


if __name__ == "__main__":
    main()
