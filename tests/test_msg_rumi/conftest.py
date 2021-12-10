# tests.test_msg_rumi.conftest
# Create fixtures for testing rumi's message-based translation monitoring
#
# Author: Rebecca Bilbro
# Created: Nov.26 2021

"""
Create fixtures for testing rumi's message-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import pytest


# #########################################################################
# Fixture
##########################################################################


@pytest.fixture(scope="class")
def commits(request):
    """
    Fixture of commit history datastructure for testing MsgReporter.
    """

    commits = {
        # For testing "updated" status
        "updated_message": {
            # source
            "en": {
                "filename": os.path.join("src", "locales", "en", "messages.po"),
                "ft": 1.0,
                "lt": 2.0,
                "history": [(1.0, "message"), (2.0, "deleted")],
            },
            # hasn't been translated but in "updated" status because the
            # original message were deleted
            "fr": {
                "filename": os.path.join("src", "locales", "fr", "messages.po"),
                "ft": 1.0,
                "lt": 1.0,
                "history": [(1.0, "")],
            },
            # has been translated but in "updated" status
            "ja": {
                "filename": os.path.join("src", "locales", "ja", "messages.po"),
                "ft": 1.0,
                "lt": 1.5,
                "history": [(1.0, ""), (1.5, "メッセージ")],
            },
        },
        # For testing "open" and "completed" status
        "message": {
            # source
            "en": {
                "filename": os.path.join("src", "locales", "en", "messages.po"),
                "ft": 1.0,
                "lt": 1.0,
                "history": [(1.0, "message")],
            },
            # open
            "fr": {
                "filename": os.path.join("src", "locales", "fr", "messages.po"),
                "ft": 1.0,
                "lt": 1.0,
                "history": [(1.0, "")],
            },
            # completed
            "ja": {
                "filename": os.path.join("src", "locales", "ja", "messages.po"),
                "ft": 1.0,
                "lt": 2.0,
                "history": [(1.0, ""), (2.0, "メッセージ")],
            },
        },
    }
    request.cls.commits = commits


@pytest.fixture(scope="class")
def src_lang(request):

    request.cls.src_lang = "en"


@pytest.fixture(scope="class")
def old_trans(request):
    """
    Old translation file for testing insert_translated function.
    """

    result = ""

    # Comment line should not be changed
    result += "Comment line.\n"

    # Empty msgstr can be inserted
    result += 'msgid "empty translation need to be inserted"\nmsgstr ""\n'

    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "old translation"\n'

    # Deprecated msgid will not be inserted
    result += '~msgid "deprecated msgid should not be inserted"\n~msgstr "deprecated translation"\n'

    request.cls.old_trans = result


@pytest.fixture(scope="class")
def add_trans(request):
    """
    Insert translation file for testing insert_translated function.
    """

    result = ""

    # Empty msgstr can be inserted
    result += 'msgid "empty translation need to be inserted"\nmsgstr "added empty translation"\n'

    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "new translation"\n'

    # Deprecated msgid will not be inserted
    result += (
        'msgid "deprecated msgid should not be inserted"\nmsgstr "new translation"\n'
    )

    request.cls.add_trans = result


@pytest.fixture(scope="class")
def new_trans(request):
    """
    New translation file for testing insert_translated function.
    """

    result = ""
    # Comment line should not be changed

    result += "Comment line.\n"
    # Empty msgstr can be inserted

    result += 'msgid "empty translation need to be inserted"\nmsgstr "added empty translation"\n'
    # Msgstr can be updated
    result += 'msgid "old translation need to be updated"\nmsgstr "new translation"\n'

    # Deprecated msgid will not be inserted
    result += '~msgid "deprecated msgid should not be inserted"\n~msgstr "deprecated translation"\n'

    request.cls.new_trans = result


@pytest.fixture(scope="class")
def stats_table(request):
    """
    Expected print out of stats table.
    """

    rows = [
        "| Language   |   Total |   Open |   Updated |   Completed |",
        "|------------+---------+--------+-----------+-------------|",
        "| en         |       2 |      0 |         0 |           0 |",
        "| fr         |       2 |      1 |         1 |           0 |",
        "| ja         |       2 |      0 |         1 |           1 |",
    ]

    table = "\n".join(rows) + "\n"

    request.cls.stats_table = table


@pytest.fixture(scope="class")
def details_table(request):
    """
    Expected print out of details table.
    """
    rows = [
        "----------------------------------------------------------------------",
        "en Open: 1",
        "message",
        "----------------------------------------------------------------------",
        "fr Open: 1",
        "message",
        "----------------------------------------------------------------------",
        "ja Open: 0",
        "----------------------------------------------------------------------",
    ]

    table = "\n".join(rows) + "\n"

    request.cls.details_table = table
