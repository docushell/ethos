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
out = subprocess.run(
    ["git", "log", "--format=%H%x00%an <%ae>%x00%(trailers:key=Signed-off-by,valueonly)", f"{base}..{head}"],
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
