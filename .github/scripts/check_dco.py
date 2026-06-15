#!/usr/bin/env python3
"""DCO enforcement (ADR-0004): every commit in the checked range carries a Signed-off-by line.

Usage: check_dco.py <base_sha> <head_sha>
"""
import subprocess
import sys

if len(sys.argv) != 3:
    print("usage: check_dco.py <base_sha> <head_sha>")
    sys.exit(2)

base, head = sys.argv[1], sys.argv[2]


def commit_exists(sha: str) -> bool:
    if not sha or set(sha) == {"0"}:
        return False
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


if not commit_exists(head):
    print(f"DCO: head commit is not available in this checkout: {head}")
    sys.exit(2)

if commit_exists(base):
    rev = f"{base}..{head}"
else:
    # Force-pushes after history rewrites can make github.event.before unreachable in the
    # fresh checkout. In that case there is no valid range to inspect, so validate the
    # pushed tip instead of failing with an internal git-log error.
    print(f"DCO: base commit unavailable; checking pushed head only: {head[:12]}")
    rev = f"{head}^!"

out = subprocess.run(
    ["git", "log", "--format=%H%x00%an <%ae>%x00%(trailers:key=Signed-off-by,valueonly)", rev],
    capture_output=True,
    text=True,
    check=True,
).stdout

bad = []
for record in filter(None, out.strip().split("\n")):
    sha, author, *trailer = record.split("\x00")
    signoff = (trailer[0] if trailer else "").strip()
    if not signoff:
        bad.append((sha[:12], author))

if bad:
    for sha, author in bad:
        print(f"DCO: commit {sha} by {author} lacks Signed-off-by (use `git commit -s`)")
    sys.exit(1)
print("DCO green")
