# tests.test_file_rumi.test_reader
# Test the reader for file-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov.19 2021

"""
Test the reader for file-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import re
import git
import time
import pytest
import shutil

from datetime import datetime
from rumi.file_rumi.reader import FileReader


##########################################################################
# FileReader Test Cases
##########################################################################


@pytest.mark.usefixtures("commits_no_status", "commits_status", "sources")
class TestFileReader:
    @pytest.mark.parametrize(
        "filename, ori_name, rename",
        [
            (
                os.path.join("content", "file.md"),
                os.path.join("content", "file.md"),
                None,
            ),
            (
                os.path.join("content", "{ english => en }", "file.md"),
                os.path.join("content", "english", "file.md"),
                os.path.join("content", "en", "file.md"),
            ),
            ("file1.md => file2.md", "file1.md", "file2.md"),
            # Case when filename does not contain rename sign
            ("file1.md file2.md", "file1.md file2.md", None),
        ],
    )
    def test_process_rename(self, filename, ori_name, rename):
        """
        Assert renaming path hack can be removed from a filename in git log.
        """
        reader = FileReader()

        got_ori_name, got_rename = reader.process_rename(filename)

        assert got_ori_name == ori_name
        assert got_rename == rename

    @pytest.mark.parametrize(
        "badfilename",
        [
            # Case when filename has multiple rename pattern { => }
            os.path.join("{ content", "{ english => en } => newdir } ", "file.md"),
            # Case when filename has multiple rename sign =>
            "file1.md => file=>2.md",
        ],
    )
    def test_parse_rename_fail(self, badfilename):
        with pytest.raises(Exception, match=r"Unable to parse the filename"):
            reader = FileReader()
            reader.process_rename(badfilename)

    def generate_fixtures(self, tmpdir, repo_name, pattern):
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

        content_dir = repo_path / "content"
        content_dir.mkdir()

        if pattern == "folder/":
            en_dir = content_dir / "en"
            en_dir.mkdir()
            fr_dir = content_dir / "fr"
            fr_dir.mkdir()

            en_file = en_dir / "test_content.md"
            fr_file = fr_dir / "test_content.md"

        elif pattern == ".lang":
            en_file = content_dir / "test_content.en.md"
            fr_file = content_dir / "test_content.fr.md"

        en_file.write_text("testing source content", encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m="source content file")
        ts1 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        time.sleep(0.5)

        fr_file.write_text("testing translation content", encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m="translation content file")
        ts2 = float(datetime.timestamp(repo.head.commit.authored_datetime))

        return str(repo_path), ts1, ts2

    @pytest.mark.parametrize(
        "pattern, en_fname, fr_fname",
        [
            (
                "folder/",
                os.path.join("content", "en", "test_content.md"),
                os.path.join("content", "fr", "test_content.md"),
            ),
            (
                ".lang",
                os.path.join("content", "test_content.en.md"),
                os.path.join("content", "test_content.fr.md"),
            ),
        ],
    )
    def test_parse_history(self, tmpdir, pattern, en_fname, fr_fname):
        """
        Assert git history is correctly parsed into a commit dictionary.
        """

        repo_path, ts1, ts2 = self.generate_fixtures(
            tmpdir, "test_{}_repo".format(re.sub("[^a-zA-Z]+", "", pattern)), pattern
        )

        reader = FileReader(
            content_paths=["content"],
            extensions=[".md"],
            repo_path=repo_path,
            branch="test",
            pattern=pattern,
            use_cache=True,
        )

        got = reader.parse_history()
        # Need to remove fixture repository after test
        shutil.rmtree(reader.cache.cache_dir)

        want = {
            "test_content.md": {
                "en": {
                    "filename": en_fname,
                    "ft": ts1,
                    "lt": ts1,
                    "history": {ts1: [1, 0, 1]},
                    "status": "source",
                },
                "fr": {
                    "filename": fr_fname,
                    "ft": ts2,
                    "lt": ts2,
                    "history": {ts2: [1, 0, 1]},
                    "status": "completed",
                },
            }
        }

        assert got == want

    @pytest.mark.parametrize(
        "pattern, fname, basename, lang",
        [
            ("folder/", os.path.join("content", "en", "file.md"), "file.md", "en"),
            (".lang", os.path.join("content", "file.en.md"), "file.md", "en"),
        ],
    )
    def test_parse_base_lang(self, pattern, fname, basename, lang):
        """
        Assert basename and lang can be parsed for two patterns.
        """
        reader = FileReader(
            content_paths=["content"], extensions=[".md"], pattern=pattern
        )

        got_basename, got_lang = reader.parse_base_lang(fname)
        assert got_basename == basename
        assert got_lang == lang

    def test_get_langs(self):
        """
        Assert self.langs can be specified.
        """

        reader = FileReader(langs="EN FR")
        commits = {"basefile": {"EN": {}, "FR": {}}}
        got = reader.get_langs(commits)
        want = {"EN", "FR"}
        assert got == want

    def test_get_sources(self):
        """
        Assert when first commit time is the same for the source and target files,
        source file is decided based on default source language.
        """
        reader = FileReader(src_lang="fr")
        commits = {"basefile": {"en": {"ft": 3.0}, "fr": {"ft": 3.0}}}
        got = reader.get_sources(commits)
        want = {"basefile": "fr"}
        assert got == want

    def test_set_status(self):
        """
        Assert "open", "completed", "updated" and "source" status correctly set.
        """

        reader = FileReader()

        commits = self.commits_no_status.copy()
        reader.set_status(commits, self.sources)

        assert commits == self.commits_status
