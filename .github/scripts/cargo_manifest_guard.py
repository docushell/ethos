#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
from typing import Protocol


class _Asserts(Protocol):
    def assertIn(self, member: object, container: object, msg: object = ...) -> None: ...
    def assertRegex(self, text: str, expected_regex: str, msg: object = ...) -> None: ...


def workspace_package_version(workspace_manifest: str) -> str:
    match = re.search(
        r"(?ms)^\[workspace\.package\]\s+.*?^version = \"([^\"]+)\"",
        workspace_manifest,
    )
    if match is None:
        raise AssertionError("workspace manifest is missing [workspace.package] version")
    return match.group(1)


def assert_workspace_version_is_semver(case: _Asserts, workspace_manifest: str) -> str:
    version = workspace_package_version(workspace_manifest)
    case.assertRegex(version, r"^\d+\.\d+\.\d+$")
    return version


def assert_workspace_dependency_uses_workspace_version(
    case: _Asserts,
    workspace_manifest: str,
    *,
    dependency: str,
    package: str,
    path: str,
    default_features_false: bool = False,
) -> None:
    version = assert_workspace_version_is_semver(case, workspace_manifest)
    expected = f'{dependency} = {{ package = "{package}", path = "{path}", version = "{version}"'
    case.assertIn(expected, workspace_manifest)
    if default_features_false:
        case.assertIn("default-features = false", workspace_manifest)
