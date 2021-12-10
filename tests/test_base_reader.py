# tests.test_base_reader
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


import os
import git
import pytest

from rumi.base_reader import BaseReader


##########################################################################
# BaseReader Test Cases
##########################################################################


class TestBaseReader:
    def generate_fixtures(self, tmpdir):
        """
        Generate fixture repo for testing BaseReader.
        """
        repo_name = "base_reader_repo"
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

        # Switch to test branch
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
            non_content_dir / "wrong.w",
        ]
        for file in files:
            file.write_text("", encoding="utf8")

        repo.git.add(A=True)
        repo.git.commit(m="adding test fixtures")

        return repo_name

    def test_init_targets(self, tmpdir):
        """
        Assert that files outside content_path or not with file extension is
        not identified as target.
        """
        # Setup repository
        repo_name = self.generate_fixtures(tmpdir)

        reader = BaseReader(
            content_paths=["content"],
            extensions=[".c"],
            repo_path=str(tmpdir / repo_name),
            branch="test",
        )

        # Asserting only files in correct path with correct extension
        # are identified as reader.targets
        assert reader.targets == {os.path.join("content", "correct.c")}

    def test_validate_repo_path(self, tmpdir):
        """
        Assert invalid repo_path raises exception.
        """
        with pytest.raises(Exception, match=r"Please specify a valid repository path"):
            reader = BaseReader(
                content_paths=["content"],
                extensions=[".c"],
                repo_path=str(tmpdir / "wrong_base_reader_repo"),
                branch="test",
            )

    def test_get_repo(self, tmpdir):
        """
        Assert repository is checkout to the branch.
        """
        repo_name = self.generate_fixtures(tmpdir)
        reader = BaseReader(
            content_paths=["content"],
            extensions=[".c"],
            repo_path=str(tmpdir / repo_name),
            branch="test",
        )

        repo = reader.get_repo()
        assert repo.active_branch.name == "test"
