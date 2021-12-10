# tests.test_msg_rumi.test_reader
# Test the reader for message-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov.15 2021

"""
Test the reader for message-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import git
import time
import shutil

from datetime import datetime
from rumi.msg_rumi.reader import MsgReader


##########################################################################
# MsgReader Test Cases
##########################################################################


class TestMsgReader:
    def generate_fixtures(self, tmpdir):
        """
        Generate fixture repo for testing MsgReader.
        """
        repo_name = "msg_reader_repo"
        repo_path = tmpdir / repo_name
        repo = git.Repo.init(repo_path)

        # Git config needed for making commits
        repo.config_writer().set_value("user", "name", "testrumi").release()
        repo.config_writer().set_value("user", "email", "testrumiemail").release()

        # Initial commit
        initial_file = repo_path / "initial_file.txt"
        initial_file.write_text("", encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m="initial commit")

        # Switch branch to "test"
        repo.git.branch("test")
        repo.git.checkout("test")

        # Set up content/en/messages.po, content/fr/messages.po for testing
        content_dir = repo_path / "locales"
        content_dir.mkdir()
        en_dir = content_dir / "en"
        en_dir.mkdir()
        fr_dir = content_dir / "fr"
        fr_dir.mkdir()
        en_file = en_dir / "messages.po"
        fr_file = fr_dir / "messages.po"

        # For testing new msg can be added and empty translation is set to ""
        en_content = '#Header line.\nmsgid "new msg"\nmsgstr "new msg"'
        fr_content = '#Header line.\nmsgid "new msg"\nmsgstr ""'
        en_file.write_text(en_content, encoding="utf8")
        fr_file.write_text(fr_content, encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m='new msg can be added and empty translation is set to ""')
        # Track this commit's timestamp
        ts1 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        # For testing new translation is added
        fr_content = '#Header line.\nmsgid "new msg"\nmsgstr "nouveau message"'
        fr_file.write_text(fr_content, encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m="new translation is added")
        # Track this commit's timestamp
        ts2 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        # For testing deleted translation is set to ""
        fr_content = '#Header line.\nmsgid "new msg"\nmsgstr ""'
        fr_file.write_text(fr_content, encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m='deleted translation is set to ""')
        # Track this commit's timestamp
        ts3 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        # For testing deleted msg is set to "deleted"
        en_content = '#Header line.\n~msgid "new msg"\n~msgstr "new msg"'
        fr_content = '#Header line.\n~msgid "new msg"\n~msgstr ""'
        en_file.write_text(en_content, encoding="utf8")
        fr_file.write_text(fr_content, encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m='deleted msg is set to "deleted"')
        # Track this commit's timestamp
        ts4 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        return str(repo_path), [ts1, ts2, ts3, ts4]

    def test_parse_history(self, tmpdir):
        """
        Assert git history is correctly parsed into a commit dictionary.
        """
        repo_path, ts = self.generate_fixtures(tmpdir)

        reader = MsgReader(
            content_paths=["locales"],
            extensions=[".po"],
            src_lang="en",
            repo_path=repo_path,
            branch="test",
            use_cache=True,
        )

        got = reader.parse_history()
        # Need to remove fixture repository after test
        shutil.rmtree(reader.cache.cache_dir)

        want = {
            '"new msg"': {
                "en": {
                    "filename": os.path.join("locales", "en", "messages.po"),
                    "ft": ts[0],
                    "lt": ts[3],
                    "history": [(ts[0], '"new msg"'), (ts[3], '"deleted"')],
                },
                "fr": {
                    "filename": os.path.join("locales", "fr", "messages.po"),
                    "ft": ts[0],
                    "lt": ts[3],
                    "history": [
                        (ts[0], '""'),
                        (ts[1], '"nouveau message"'),
                        (ts[2], '""'),
                        (ts[3], '"deleted"'),
                    ],
                },
            }
        }
        assert got == want

    def test_parse_lang(self, tmpdir):
        """
        Assert correct language is parsed from filename.
        """
        filename = os.path.join("web", "src", "locales", "en", "messages.po")
        reader = MsgReader(content_paths=["locales"], extensions=[".po"], src_lang="en")
        lang = reader.parse_lang(filename)

        assert lang == "en"
