# tests.test_file_rumi.test_reporter
# Test the reporter for file-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov.19 2021

"""
Test the reporter for file-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import pytest

from rumi.file_rumi.reporter import FileReporter


##########################################################################
# FileReporter Test Cases
##########################################################################


@pytest.mark.usefixtures("commits_status", "stats_table", "details_table")
class TestFileReporter:
    def test_get_stats(self):
        """
        Assert the status can be correctly aggregated. 
        """
        reporter = FileReporter()
        got = reporter.get_stats(self.commits_status)
        want = {
            "fr": {"open": 0, "updated": 0, "completed": 0, "total": 0},
            "en": {"open": 0, "updated": 0, "completed": 1, "total": 1},
            "zh": {"open": 0, "updated": 1, "completed": 0, "total": 1},
            "ja": {"open": 1, "updated": 0, "completed": 0, "total": 1},
        }
        assert got == want

    def test_print_stats(self, capsys):
        """
        Assert reporter.stats() prints with no error.
        """
        reporter = FileReporter()
        stats = reporter.get_stats(self.commits_status)
        reporter.print_stats(stats)

        captured = capsys.readouterr()

        assert captured.out == self.stats_table

    def generate_fixture(self, tmpdir):
        """
        Generate fixture files for testing reporter.get_details.
        """
        # Make repo path
        repo_path = tmpdir / "repo"
        repo_path.mkdir()

        # Make content path
        content_path = repo_path / "content"
        content_path.mkdir()

        # Make source file for testing word count
        src_path = content_path / "fr"
        src_path.mkdir()
        src_file = repo_path / os.path.join("content", "fr", "file.md")
        src_file.write_text("line1\nline2\nline3\nline4\n", encoding="utf-8")

        return repo_path

    def test_get_details(self, tmpdir):
        """
        Assert details of translation status, e.g. percent updated and percent
        completed can be correctly computed.
        """
        repo_path = self.generate_fixture(tmpdir)

        reporter = FileReporter(repo_path=repo_path)

        got = reporter.get_details(self.commits_status)

        want = [
            {
                "basefile": "file.md",
                "status": "completed",
                "src_lang": "fr",
                "wc": "4",
                "tgt_lang": "en",
                "pc": "100.0%",
                "pu": "0%",
            },
            {
                "basefile": "file.md",
                "status": "updated",
                "src_lang": "fr",
                "wc": "4",
                "tgt_lang": "zh",
                "pc": "50.0%",
                "pu": "50.0%",
            },
            {
                "basefile": "file.md",
                "status": "open",
                "src_lang": "fr",
                "wc": "4",
                "tgt_lang": "ja",
                "pc": "0%",
                "pu": "100.0%",
            },
        ]
        assert got == want

    def test_print_details(self, tmpdir, capsys):
        """
        Assert reporter.detail() prints with no error.
        """
        repo_path = self.generate_fixture(tmpdir)

        reporter = FileReporter(repo_path=repo_path)

        details = reporter.get_details(self.commits_status)
        reporter.print_details(details)

        captured = capsys.readouterr()

        assert captured.out == self.details_table

    def test_word_count(self, tmpdir):
        """
        Assert empty lines are ignored in word count.
        """
        # Setup word count testing file
        repo_path = tmpdir / "repo"
        repo_path.mkdir()

        # Make test file content
        fname = "wc_test.txt"
        file = repo_path / fname
        file.write_text("\n\ncontent content\n", encoding="utf-8")

        # Init reporter
        reporter = FileReporter(repo_path=repo_path)

        got = reporter.word_count(fname)
        assert got == 2
