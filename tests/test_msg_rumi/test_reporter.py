# tests.test_msg_rumi.test_reporter
# Test the reporter for message-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov.16 2021

"""
Test the reporter for message-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import pytest

from rumi.msg_rumi.reporter import MsgReporter


##########################################################################
# MsgReporter Test Cases
##########################################################################


@pytest.mark.usefixtures(
    "commits",
    "src_lang",
    "old_trans",
    "add_trans",
    "new_trans",
    "stats_table",
    "details_table",
)
class TestMsgReporter:
    def test_get_stats(self):
        """
        Assert that stats are calculated correctly based on commits and src_lang.
        """
        reporter = MsgReporter()

        got_stats = reporter.get_stats(self.commits, self.src_lang)

        want_stats = {
            "en": {"total": 2, "open": 0, "updated": 0, "completed": 0},
            "fr": {"total": 2, "open": 1, "updated": 1, "completed": 0},
            "ja": {"total": 2, "open": 0, "updated": 1, "completed": 1},
        }

        assert want_stats == got_stats

    def test_get_details(self):
        """
        Assert details are extracted correctly based on commits and src_lang.
        """

        reporter = MsgReporter()

        got_details = reporter.get_details(self.commits, self.src_lang)

        want_details = {
            "en": {"open": 1, "msgs": ["message"], "wc": 1},
            "fr": {"open": 1, "msgs": ["message"], "wc": 1},
            "ja": {"open": 0, "msgs": [], "wc": 0},
        }

        assert want_details == got_details

    def test_print_stats(self, capsys):
        """
        Assert reporter.stats() prints with no error.
        """

        reporter = MsgReporter()
        stats = reporter.get_stats(self.commits, self.src_lang)
        reporter.print_stats(stats)

        captured = capsys.readouterr()

        assert captured.out == self.stats_table

    def test_print_details(self, capsys):
        """
        Assert reporter.detail() prints with no error.
        """

        reporter = MsgReporter()
        details = reporter.get_details(self.commits, self.src_lang)
        reporter.print_details(details)

        captured = capsys.readouterr()

        assert captured.out == self.details_table

    def test_download_needs(self, tmpdir):
        """
        Assert msg needing translation can be correctly downloaded to specified
        path
        """

        reporter = MsgReporter()
        details = reporter.get_details(self.commits, self.src_lang)
        reporter.download_needs(details, "fr", path=tmpdir)

        want = tmpdir / "fr_needing_translation.txt"

        assert want in tmpdir.listdir()

    def test_insert_translations(self, tmpdir):
        """
        Assert translations and the original file is correctly combined.
        """

        old_file = tmpdir / "old_file.txt"
        old_file.write_text(self.old_trans, encoding="utf8")

        add_file = tmpdir / "file.txt"
        add_file.write_text(self.add_trans, encoding="utf8")

        reporter = MsgReporter()
        reporter.insert_translations(add_file, old_file)

        got = tmpdir / "inserted_file.txt"

        assert got.read_text(encoding="utf8") == self.new_trans
