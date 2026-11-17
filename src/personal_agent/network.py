# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Optional non-root Tailscale userspace daemon; no TUN device or host networking."""

import asyncio
import os
import tempfile
from pathlib import Path


async def start_tailnet(state_dir: Path):
    socket = state_dir / "tailscaled.sock"
    daemon = await asyncio.create_subprocess_exec(
        "/usr/local/bin/tailscaled",
        "--tun=userspace-networking",
        "--socks5-server=127.0.0.1:1055",
        "--state=" + str(state_dir / "tailscaled.state"),
        "--socket=" + str(socket),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            if socket.exists():
                break
            if daemon.returncode is not None:
                raise RuntimeError("Private networking daemon failed")
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError("Private networking startup deadline exceeded")
        key = os.environ.get("TS_AUTHKEY", "")
        if not key and not (state_dir / "tailscaled.state").exists():
            raise RuntimeError("Tailscale class-only enrollment is not configured")
        with tempfile.NamedTemporaryFile(
            mode="w", dir=state_dir, prefix="ts-auth-", delete=True
        ) as auth:
            auth.write(key)
            auth.flush()
            command = [
                "/usr/local/bin/tailscale",
                "--socket=" + str(socket),
                "up",
                "--hostname=assignment3-agent",
                "--accept-dns=false",
                "--advertise-tags=tag:assignment3-agent",
            ]
            if key:
                command.append("--auth-key=file:" + auth.name)
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            try:
                code = await asyncio.wait_for(process.wait(), 45)
            except TimeoutError:
                process.terminate()
                await process.wait()
                raise RuntimeError("Private networking enrollment timed out") from None
            if code:
                raise RuntimeError(
                    "Private networking enrollment failed; inspect private account settings"
                )
        return daemon
    except BaseException:
        if daemon.returncode is None:
            daemon.terminate()
            await daemon.wait()
        raise
