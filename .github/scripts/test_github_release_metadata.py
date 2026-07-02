#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import unittest
from copy import deepcopy

from check_github_release_metadata import ReleaseMetadataError, validate_release_metadata


class GitHubReleaseMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.github = {
            "tag": "v0.3.0",
            "name": "Release v0.3.0",
            "assets": ["ethos-linux-x64.tar.gz", "ethos-macos-arm64.tar.gz"],
        }
        self.release = {
            "id": 30,
            "tag_name": "v0.3.0",
            "name": "Release v0.3.0",
            "draft": False,
            "prerelease": False,
            "body": "canonical notes\n",
            "assets": [
                {"name": "ethos-macos-arm64.tar.gz"},
                {"name": "ethos-linux-x64.tar.gz"},
            ],
        }
        self.latest = deepcopy(self.release)

    def test_matching_latest_release_is_accepted(self) -> None:
        validate_release_metadata(self.github, self.latest, self.release, "canonical notes")

    def test_stale_latest_pointer_is_rejected(self) -> None:
        self.latest["tag_name"] = "v0.2.0"
        with self.assertRaisesRegex(ReleaseMetadataError, "latest release"):
            validate_release_metadata(self.github, self.latest, self.release, "canonical notes")

    def test_mismatched_release_body_is_rejected(self) -> None:
        self.release["body"] = "stale notes"
        with self.assertRaisesRegex(ReleaseMetadataError, "canonical notes"):
            validate_release_metadata(self.github, self.latest, self.release, "canonical notes")

    def test_draft_or_prerelease_is_rejected(self) -> None:
        self.release["draft"] = True
        with self.assertRaisesRegex(ReleaseMetadataError, "must not be a draft"):
            validate_release_metadata(self.github, self.latest, self.release, "canonical notes")

    def test_asset_drift_is_rejected(self) -> None:
        self.release["assets"].pop()
        with self.assertRaisesRegex(ReleaseMetadataError, "assets differ"):
            validate_release_metadata(self.github, self.latest, self.release, "canonical notes")


if __name__ == "__main__":
    unittest.main()
