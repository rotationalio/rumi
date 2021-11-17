# rumi.test_msg_rumi.test_reporter
# Test the reporter for translation-based monitoring
# 
# Author: Tianshu Li
# Created: Nov.16 2021

"""
Test the reporter for translation-based monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import pytest

from io import StringIO
from rumi.msg_rumi.reporter import MsgReporter


##########################################################################
# Fixture
##########################################################################


@pytest.fixture
def commits():
    commits = {
            "updated_message": {
                # source
                "en": {
                    "filename": "src/locales/en/messages.po",
                    "ft": 1.0,
                    "lt": 2.0,
                    "history": [(1.0, "message"), (2.0, "deleted")]
                },
                # hasn't been translated but in "updated" status because the
                # original message were deleted
                "fr": {
                    "filename": "src/locales/fr/messages.po",
                    "ft": 1.0,
                    "lt": 1.0,
                    "history": [(1.0, "")]
                },
                # has been translated but in "updated" status 
                "ja": {
                    "filename": "src/locales/ja/messages.po",
                    "ft": 1.0,
                    "lt": 1.5,
                    "history": [(1.0, ""), (1.5, "メッセージ")]
                }
            },
            "message":{
                # source
                "en": {
                    "filename": "src/locales/en/messages.po",
                    "ft": 1.0,
                    "lt": 1.0,
                    "history": [(1.0, "message")]
                },
                # open
                "fr": {
                    "filename": "src/locales/fr/messages.po",
                    "ft": 1.0,
                    "lt": 1.0,
                    "history": [(1.0, "")]
                },
                # completed 
                "ja": {
                    "filename": "src/locales/fr/messages.po",
                    "ft": 1.0,
                    "lt": 2.0,
                    "history": [(1.0, ""), (2.0, "メッセージ")]
                }

            }
        }
    return commits

@pytest.fixture
def src_lang():
    return "en"

@pytest.fixture
def old_trans():
    result = ""
    # Comment line should not be changed
    result += "Comment line.\n"
    # Empty msgstr can be inserted
    result += 'msgid "empty translation need to be inserted"\nmsgstr ""\n'
    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "old translation"\n'
    # Deprecated msgid will not be inserted
    result += '~msgid "deprecated msgid should not be inserted"\n~msgstr "deprecated translation"\n'
    return result

@pytest.fixture
def add_trans():
    result = ""
    # Empty msgstr can be inserted
    result += 'msgid "empty translation need to be inserted"\nmsgstr "added empty translation"\n'
    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "new translation"\n'
    # Deprecated msgid will not be inserted
    result += 'msgid "deprecated msgid should not be inserted"\nmsgstr "new translation"\n'
    return result

@pytest.fixture
def new_trans():
    result = ""
    # Comment line should not be changed
    result += "Comment line.\n"
    # Empty msgstr can be inserted
    result += 'msgid "empty translation need to be inserted"\nmsgstr "added empty translation"\n'
    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "new translation"\n'
    # Deprecated msgid will not be inserted
    result += '~msgid "deprecated msgid should not be inserted"\n~msgstr "deprecated translation"\n'
    return result


##########################################################################
# MsgReporter Test Cases
##########################################################################


class TestMsgReporter():

    def test_fixtures_msg_reporter(self, ):
        """
        Generate fixture repo for testing MsgReporter.
        """
        

    def test_get_stats(self, commits, src_lang):
        """
        Assert that stats are calculated correctly based on commits and src_lang.
        """
        reporter = MsgReporter()

        got_stats = reporter.get_stats(commits, src_lang)
        want_stats = {
            "en": {"total": 2, "open": 0, "updated": 0, "completed": 0},
            "fr": {"total": 2, "open": 1, "updated": 1, "completed": 0},
            "ja": {"total": 2, "open": 0, "updated": 1, "completed": 1}
        }
        assert want_stats == got_stats

    def test_get_details(self, commits, src_lang):
        """
        Assert details are extracted correctly based on commits and src_lang.
        """
        reporter = MsgReporter()
        got_details = reporter.get_details(commits, src_lang)
        want_details = {
            "en": {
                "open": 1, 
                "msgs": ["message"],
                "wc": 1
            },
            "fr": {
                "open": 1, 
                "msgs": ["message"],
                "wc": 1
            },
            "ja": {
                "open": 0, 
                "msgs": [],
                "wc": 0
            }
        }
        assert want_details == got_details

    def test_stats(self, commits, src_lang):
        """
        Assert reporter.stats() prints as expected.
        """
        reporter = MsgReporter()
        stats = reporter.get_details(commits, src_lang)
        reporter.detail(stats)

    def test_detail(self, commits, src_lang):
        """
        Assert reporter.detail() prints as expected.
        """
        reporter = MsgReporter()
        details = reporter.get_details(commits, src_lang)
        reporter.detail(details)
       
    def test_download_needs(self, tmpdir, commits, src_lang):
        """
        Assert msg needing translation can be correctly downloaded to specified
        path
        """
        reporter = MsgReporter()
        details = reporter.get_details(commits, src_lang)
        reporter.download_needs(details, "fr", path=tmpdir)

        assert os.path.isfile(os.path.join(tmpdir, "fr_needing_translation.txt"))
    
    def test_insert_translations(
        self, tmpdir, old_trans, add_trans, new_trans
    ):
        """
        Assert translations and the original file is correctly combined.
        """
        old_file = os.path.join(tmpdir, "old_file.txt")
        with open(old_file, "w+") as f:
            f.write(old_trans)

        add_file = os.path.join(tmpdir, "file.txt")
        with open(add_file, "w+") as f:
            f.write(add_trans)
        
        reporter = MsgReporter()
        reporter.insert_translations(add_file, old_file)

        got = tmpdir / "inserted_file.txt"
        want = new_trans.strip().split("\n")
        with open(got, "r+") as f:
            assert len(f.readlines()) == len(want)
            for line, want_line in zip(f.readlines(), want):
                assert line.strip() == want_line