# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Build the verified upstream SQLite security release inside the image build stage."""

import hashlib
import io
import pathlib
import subprocess  # nosec B404
import urllib.request
import zipfile

URL = "https://www.sqlite.org/2026/sqlite-amalgamation-3540100.zip"
SHA3 = "92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30"
SOURCE_SHA3 = "e2b869d3003b33c942b7dd7063604fbc53553e1b66609570df39b9b7b558ee81"


def main():
    with urllib.request.urlopen(URL, timeout=60) as response:  # nosec B310
        archive = response.read(10_000_001)
    if len(archive) > 10_000_000 or hashlib.sha3_256(archive).hexdigest() != SHA3:
        raise RuntimeError("SQLite archive integrity mismatch")
    source = zipfile.ZipFile(io.BytesIO(archive)).read("sqlite-amalgamation-3540100/sqlite3.c")
    if hashlib.sha3_256(source).hexdigest() != SOURCE_SHA3:
        raise RuntimeError("SQLite source integrity mismatch")
    pathlib.Path("/build").mkdir(exist_ok=True)
    pathlib.Path("/build/sqlite3.c").write_bytes(source)
    pathlib.Path("/out").mkdir(exist_ok=True)
    subprocess.run(
        [
            "/usr/bin/cc",
            "-O2",
            "-fPIC",
            "-shared",
            "-DSQLITE_ENABLE_FTS5",
            "-DSQLITE_ENABLE_RTREE",
            "-DSQLITE_ENABLE_COLUMN_METADATA",
            "-DSQLITE_THREADSAFE=1",
            "-DSQLITE_USE_URI=1",
            "-Wl,-soname,libsqlite3.so.0",
            "-o",
            "/out/libsqlite3.so.0",
            "/build/sqlite3.c",
            "-lm",
            "-ldl",
            "-pthread",
        ],
        check=True,
        timeout=180,
    )  # noqa: S603  # nosec B603

    # A real replacement package records the actual patched upstream version.
    # This replaces the vulnerable ELF as well as its package inventory entry.
    arch = subprocess.check_output(["/usr/bin/dpkg", "--print-architecture"], text=True).strip()  # nosec B603
    triplet = subprocess.check_output(["/usr/bin/cc", "-dumpmachine"], text=True).strip()  # nosec B603
    root = pathlib.Path("/build/package")
    library = root / "usr/lib" / triplet
    library.mkdir(parents=True)
    (library / "libsqlite3.so.0.8.6").write_bytes(pathlib.Path("/out/libsqlite3.so.0").read_bytes())
    (library / "libsqlite3.so.0").symlink_to("libsqlite3.so.0.8.6")
    control = root / "DEBIAN"
    control.mkdir()
    (control / "control").write_text(
        "Package: libsqlite3-0\nVersion: 3.54.1-a3.1\nArchitecture: "
        + arch
        + "\nMaintainer: Assignment 3 <arya.wadhwani@gmail.com>\n"
        "Depends: libc6 (>= 2.34)\nSection: libs\nPriority: optional\n"
        "Description: Verified upstream SQLite 3.54.1, built for Assignment 3\n"
    )
    subprocess.run(  # noqa: S603  # nosec B603
        [
            "/usr/bin/dpkg-deb",
            "--build",
            "--root-owner-group",
            str(root),  # noqa: S603
            "/out/sqlite-security.deb",
        ],
        check=True,
        timeout=60,
    )  # nosec B603


if __name__ == "__main__":
    main()
