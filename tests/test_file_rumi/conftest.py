# rumi.test_file_rumi.conftest
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
                    "filename": "content/fr/file.md",
                    "ft": 0.1,
                    "lt": 0.3,
                    "history": {
                        0.1: [2, 0, 2],
                        0.3: [2, 0, 4]
                    },
                },
                "en": {
                    "filename": "content/fr/file.md",
                    "ft": 0.1,
                    "lt": 0.3,
                    "history": {
                        0.1: [2, 0, 2],
                        0.3: [2, 0, 4]
                    },
                },
                "zh": {
                    "filename": "content/zh/file.md",
                    "ft": 0.2,
                    "lt": 0.2,
                    "history": {
                        0.2: [2, 0, 2]
                    },
                },
                "ja": {}
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
                    "filename": "content/fr/file.md",
                    "ft": 0.1,
                    "lt": 0.3,
                    "history": {
                        0.1: [2, 0, 2],
                        0.3: [2, 0, 4]
                    },
                    "status": "source"
                },
                "en": {
                    "filename": "content/fr/file.md",
                    "ft": 0.1,
                    "lt": 0.3,
                    "history": {
                        0.1: [2, 0, 2],
                        0.3: [2, 0, 4]
                    },
                    "status": "completed"
                },
                "zh": {
                    "filename": "content/zh/file.md",
                    "ft": 0.2,
                    "lt": 0.2,
                    "history": {
                        0.2: [2, 0, 2]
                    },
                    "status": "updated"
                },
                "ja": {"status": "open"}
            }
        }

    request.cls.commits_status = commits

@pytest.fixture(scope="class")
def sources(request):
    """
    Fixture of sources for testing reader.set_status.
    """

    sources = {
        "file.md": "fr"
    }
    request.cls.sources = sources