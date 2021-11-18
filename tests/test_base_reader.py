# rumi.test_base_reader
# Test the base git history reader
# 
# Author: Tianshu Li
# Created: Nov.15 2021

"""
Test the base git history reader
"""

##########################################################################
# Imports
##########################################################################


import git
import pytest

from rumi.base_reader import BaseReader


##########################################################################
# BaseReader Test Cases
##########################################################################


class TestBaseReader():
    def test_fixtures_base_reader(self, tmpdir, delete=False):
        """
        Generate fixture repo for testing BaseReader.
        """
        repo_name = "base_reader_repo"
        repo_path = tmpdir / repo_name
        repo = git.Repo.init(repo_path)
        repo.config_writer().set_value("user", "name", "testrumi").release()
        repo.config_writer().set_value("user", "email", "testrumiemail").release()
        
        initial_file = repo_path / "initial_file.txt"
        initial_file.write_text("", encoding="utf8")
        repo.git.add(A=True)
        repo.git.commit(m="initial commit")

        repo.git.branch("test")
        repo.git.checkout("test")

        # Add content_path and non content_path
        content_dir = repo_path / "content"
        content_dir.mkdir()
        non_content_dir = repo_path / "non_content"
        non_content_dir.mkdir()

        # Add correct and wrong file extensions for testing init_targets
        files = [
            content_dir / "correct.c",
            content_dir / "wrong.w", 
            non_content_dir / "correct.c",
            non_content_dir / "wrong.w"
        ]
        for file in files:
            file.write_text("", encoding="utf8")

        repo.git.add(A=True)
        repo.git.commit(m="adding test fixtures")

        if delete:
            non_content_dir.remove(rec=1)
            repo.git.add(A=True)
            repo.git.commit(m="deleting part of test fixtures")
        return repo_name

    def test_get_current_repo_set(self, tmpdir):
        """
        Assert that all added files and none deleted files in git history are 
        included in repo_set.
        """
        # Setup repository
        repo_name = self.test_fixtures_base_reader(tmpdir, delete=True)
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=str(tmpdir / repo_name), branch="test"
        )
        # Asserting repo_set result
        assert reader.get_current_repo_set() == {"initial_file.txt", "content/correct.c", "content/wrong.w"}

    def test_init_targets(self, tmpdir):
        """
        Assert that files outside content_path or not with file extension is 
        not identified as target.
        """
        # Setup repository
        repo_name = self.test_fixtures_base_reader(tmpdir)
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=str(tmpdir / repo_name), branch="test"
        )
        # Asserting only files in correct path with correct extension
        # are identified as reader.targets
        assert reader.targets == {"content/correct.c"}

    @pytest.mark.parametrize(
        "path", ["base_reader_repo", "base_reader_repo/"]
    )
    def test_validate_repo_path(self, tmpdir, path):
        """
        Assert invalid repo_path is set to None.
        """
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=str(tmpdir / "wrong_base_reader_repo"), branch="test"
        )
        assert reader.repo_path == None

    def test_get_repo(self, tmpdir):
        """
        Assert repository is checkout to the branch.
        """
        repo_name = self.test_fixtures_base_reader(tmpdir)
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=str(tmpdir / repo_name), branch="test"
        )

        repo = reader.get_repo()
        assert repo.active_branch.name == "test"
