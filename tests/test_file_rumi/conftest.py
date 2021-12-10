# tests.test_file_rumi.conftest
# Create fixtures for testing rumi's file-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov.29 2021

"""
Create fixtures for testing rumi's file-based translation monitoring
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
def commits_no_status(request):
    """
    Fixture of commit history datastructure before setting translation status.
    """

    commits = {
        "file.md": {
            "fr": {
                "filename": os.path.join("content", "fr", "file.md"),
                "ft": 0.1,
                "lt": 0.3,
                "history": {0.1: [2, 0, 2], 0.3: [2, 0, 4]},
            },
            "en": {
                "filename": os.path.join("content", "en", "file.md"),
                "ft": 0.1,
                "lt": 0.3,
                "history": {0.1: [2, 0, 2], 0.3: [2, 0, 4]},
            },
            "zh": {
                "filename": os.path.join("content", "zh", "file.md"),
                "ft": 0.2,
                "lt": 0.2,
                "history": {0.2: [2, 0, 2]},
            },
            "ja": {},
        }
    }

    request.cls.commits_no_status = commits


@pytest.fixture(scope="class")
def commits_status(request):
    """
    Fixture of commit history datastructure after setting translation status.
    """
    commits = {
        "file.md": {
            "fr": {
                "filename": os.path.join("content", "fr", "file.md"),
                "ft": 0.1,
                "lt": 0.3,
                "history": {0.1: [2, 0, 2], 0.3: [2, 0, 4]},
                "status": "source",
            },
            "en": {
                "filename": os.path.join("content", "en", "file.md"),
                "ft": 0.1,
                "lt": 0.3,
                "history": {0.1: [2, 0, 2], 0.3: [2, 0, 4]},
                "status": "completed",
            },
            "zh": {
                "filename": os.path.join("content", "zh", "file.md"),
                "ft": 0.2,
                "lt": 0.2,
                "history": {0.2: [2, 0, 2]},
                "status": "updated",
            },
            "ja": {"status": "open"},
        }
    }

    request.cls.commits_status = commits


@pytest.fixture(scope="class")
def sources(request):
    """
    Fixture of sources for testing reader.set_status.
    """

    sources = {"file.md": "fr"}
    request.cls.sources = sources


@pytest.fixture(scope="class")
def stats_table(request):
    """
    Expected print out of stats table.
    """
    rows = [
        "| Target Language   |   Total |   Open |   Updated |   Completed |",
        "|-------------------+---------+--------+-----------+-------------|",
        "| fr                |       0 |      0 |         0 |           0 |",
        "| en                |       1 |      0 |         0 |           1 |",
        "| zh                |       1 |      0 |         1 |           0 |",
        "| ja                |       1 |      1 |         0 |           0 |",
    ]

    table = "\n".join(rows) + "\n"

    request.cls.stats_table = table


@pytest.fixture(scope="class")
def details_table(request):
    """
    Expected print out of details table.
    """
    rows = [
        "| File    | Status    | Source Language   |   Word Count | Target Language   | Percent Completed   | Percent Updated   |",
        "|---------+-----------+-------------------+--------------+-------------------+---------------------+-------------------|",
        "| file.md | completed | fr                |            4 | en                | 100.0%              | 0%                |",
        "| file.md | updated   | fr                |            4 | zh                | 50.0%               | 50.0%             |",
        "| file.md | open      | fr                |            4 | ja                | 0%                  | 100.0%            |",
    ]

    table = "\n".join(rows) + "\n"

    request.cls.details_table = table
