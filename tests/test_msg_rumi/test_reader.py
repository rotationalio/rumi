# rumi.test_msg_rumi.test_reader
# Test the reader for message-based translation
#
# Author: Tianshu Li
# Created: Nov.15 2021

"""
Test the reader for message-based translation
"""

##########################################################################
# Imports
##########################################################################


import os 
import git

from datetime import datetime, timezone
from rumi.msg_rumi.reader import MsgReader


##########################################################################
# MsgReader Test Cases
##########################################################################


class TestMsgReader():
    def test_fixtures_msg_reader(self, tmpdir):
        """
        Generate fixture repo for testing MsgReader.
        """
        repo_name = "msg_reader_repo"
        repo_path = os.path.join(tmpdir, repo_name)
        repo = git.Repo.init(repo_path)
        with open(os.path.join(tmpdir, repo_name, "test_file"), "w+") as f: 
            pass
        repo.git.add(A=True)
        repo.git.commit(m="initial commit")

        repo.git.branch("test")
        repo.git.checkout("test")

        with open(os.path.join(tmpdir, repo_name, "test_file1"), "w+") as f: 
            pass

        repo.git.add(A=True)
        repo.git.commit(m="adding test fixtures")
        return repo

    def test_parse_timestamp(self, tmpdir):
        """
        Assert correct float timestamp is given based on a string in this format:
        "Thu Nov 11 22:45:36 2021 +0800".
        """
        now = datetime.now(timezone.utc)
        s = now.strftime("%a %b %d %H:%M:%S %Y %z")

        reader = MsgReader(
            content_path="locales/", extension=["po"], src_lang="en"
        )
        ts = reader.parse_timestamp(s)
        
        assert ts == float(int(datetime.timestamp(now)))

    def test_parse_lang(self, tmpdir):
        """
        Assert correct language is parsed from filename.
        """
        filename = "web/src/locales/en/messages.po"
        reader = MsgReader(
            content_path="locales/", extension=["po"], src_lang="en"
        )
        lang = reader.parse_lang(filename)

        assert lang == "en"