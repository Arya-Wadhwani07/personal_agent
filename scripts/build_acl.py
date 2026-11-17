# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Build the pinned upstream ACL fix on the runtime's Debian ABI."""

import hashlib
import io
import pathlib
import subprocess  # nosec B404
import tarfile
import urllib.request

URL = "https://deb.debian.org/debian/pool/main/a/acl/acl_2.4.0.orig.tar.xz"
SHA256 = "e661131456d2708a01c614a0f400e11d7d1bfaeb6f3e74b75bb980b72f0161a3"


def run(args, **kwargs):
    return subprocess.run(args, check=True, timeout=180, **kwargs)  # noqa: S603  # nosec B603


def main():
    with urllib.request.urlopen(URL, timeout=60) as response:  # nosec B310
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000 or hashlib.sha256(raw).hexdigest() != SHA256:
        raise RuntimeError("ACL source integrity mismatch")
    dest = pathlib.Path("/build/acl-source")
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:xz") as archive:
        archive.extractall(dest, filter="data")
    source = dest / "acl-2.4.0"
    run([str(source / "configure"), "--prefix=/usr", "--disable-static"], cwd=source)
    run(["/usr/bin/make", "-j4"], cwd=source)
    # The upstream root suite assumes Bash and an unrestricted device cgroup.
    # Keep every assertion, accepting EPERM as the sandbox's stronger device denial.
    harness = source / "test/run"
    original = harness.read_text()
    needle = "exec ('/bin/sh', '-c',"
    if original.count(needle) != 1:
        raise RuntimeError("Unexpected ACL test harness")
    harness.write_text(original.replace(needle, "exec ('/bin/bash', '-c',"))
    permissions = source / "test/root/permissions.run"
    original = permissions.read_text()
    needle = "hdt: No such device or address$"
    if original.count(needle) != 1:
        raise RuntimeError("Unexpected ACL device test")
    permissions.write_text(
        original.replace(needle, "hdt: (No such device or address|Operation not permitted)$")
    )
    try:
        run(["/usr/bin/make", "check"], cwd=source)
    except subprocess.CalledProcessError:
        print((source / "test-suite.log").read_text(), flush=True)
        raise
    arch = subprocess.check_output(["/usr/bin/dpkg", "--print-architecture"], text=True).strip()  # nosec B603
    triplet = subprocess.check_output(["/usr/bin/cc", "-dumpmachine"], text=True).strip()  # nosec B603
    package = pathlib.Path("/build/acl-package")
    library = package / "usr/lib" / triplet
    library.mkdir(parents=True)
    candidates = [p for p in source.rglob("libacl.so.1.*") if not p.is_symlink()]
    if len(candidates) != 1:
        raise RuntimeError("Unexpected ACL build output")
    built = candidates[0]
    target = library / built.name
    target.write_bytes(built.read_bytes())
    (library / "libacl.so.1").symlink_to(target.name)
    control = package / "DEBIAN"
    control.mkdir()
    (control / "control").write_text(
        "Package: libacl1\nVersion: 2.4.0-a3.1\nArchitecture: "
        + arch
        + "\nMaintainer: Assignment 3 <arya.wadhwani@gmail.com>\n"
        "Depends: libc6 (>= 2.34)\nSection: libs\nPriority: optional\n"
        "Description: Verified upstream ACL 2.4.0 built for Assignment 3\n"
    )
    run(
        [
            "/usr/bin/dpkg-deb",
            "--build",
            "--root-owner-group",
            str(package),
            "/out/acl-security.deb",
        ]
    )


if __name__ == "__main__":
    main()
