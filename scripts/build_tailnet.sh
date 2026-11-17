#!/bin/sh
# Adapted from https://github.com/tailscale/tailscale/blob/v1.104.7/build_docker.sh - retain version stamps for a container-only dependency patch.
# I developed this adaptation with Codex assistance; see PROCESS_LOG.md.
set -eu
go mod download -json tailscale.com@v1.104.7 > /tmp/tailscale-source.json
grep -F '"Sum": "h1:YqImcXyNIe25x7Qwei8PgbtkjFd3pKed9cFY0Flkitc="' /tmp/tailscale-source.json >/dev/null
cp -R /go/pkg/mod/tailscale.com@v1.104.7 /src
chmod -R u+w /src
cd /src
go get github.com/klauspost/compress@v1.20.2 golang.org/x/net@v0.62.0 golang.org/x/crypto@v0.58.1-0.20261009181718-2f1f834330b2
go mod verify
mkdir -p /out
for name in tailscale tailscaled; do
  CGO_ENABLED=0 GOOS=linux GOARCH="$TARGETARCH" go build -trimpath -buildvcs=false -tags ts_package_container -ldflags '-s -w -X tailscale.com/version.longStamp=1.104.7-a3-security1 -X tailscale.com/version.shortStamp=1.104.7-a3-security1 -X tailscale.com/version.gitCommitStamp=cbc74fe48ef1b1649f69a4d9a602319427e25102' -o "/out/$name" "./cmd/$name"
done
cp go.mod go.sum /out/
