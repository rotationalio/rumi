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


import os
import git
import pytest

from rumi.base_reader import BaseReader


##########################################################################
# BaseReader Test Cases
##########################################################################


class TestBaseReader():
    def test_fixtures_base_reader(self, tmpdir):
        """
        Generate fixture repo for testing BaseReader.
        """
        repo_name = "base_reader_repo"
        repo_path = os.path.join(tmpdir, repo_name)
        repo = git.Repo.init(repo_path)
        with open(os.path.join(tmpdir, repo_name, "test_file"), "w+") as f: 
            pass
        repo.git.add(A=True)
        repo.git.commit(m="initial commit")

        repo.git.branch("test")
        repo.git.checkout("test")

        # Add content_path and non content_path
        os.mkdir(os.path.join(repo_path, "content"))
        os.mkdir(os.path.join(repo_path, "non_content"))

        # Add correct and wrong file extensions
        with open(os.path.join(repo_path, "content", "correct.c"), "w+") as f:
            pass
        with open(os.path.join(repo_path, "non_content", "correct.c"), "w+") as f:
            pass
        with open(os.path.join(repo_path, "content", "wrong.w"), "w+") as f:
            pass
        with open(os.path.join(repo_path, "non_content", "wrong.w"), "w+") as f:
            pass

        repo.git.add(A=True)
        repo.git.commit(m="adding test fixtures")
        return repo

    def test_get_current_repo_set(self):
        """
        Assert that all added files and none deleted files in git history are 
        included in repo_set.
        """
        # 10
        # Setup repository

        # Asserting repo_set result

    def test_init_targets(self):
        """
        Assert that files outside content_path or not with file extension is 
        not identified as target.
        """
        # 11
        # Setup repository
        # Asserting target results

    @pytest.mark.parametrize(
        "path", ["base_reader_repo", "base_reader_repo/"]
    )
    def test_validate_repo_path(self, tmpdir, path):
        """
        Assert that either "repo_name" and "repo_name/" can access the repository,
        and invalid repo_path is set to None.
        """
        self.test_fixtures_base_reader(tmpdir)
        
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=os.path.join(tmpdir, path), branch="test"
        )
        assert os.path.isdir(reader.repo_path)

        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=os.path.join(tmpdir, "wrong_base_reader_repo"), branch="test"
        )
        assert reader.repo_path == None

    def test_get_repo(self, tmpdir):
        """
        Assert repository is checkout to the branch.
        """
        self.test_fixtures_base_reader(tmpdir)
        reader = BaseReader(
            content_path=["content"], extension=["c"],
            repo_path=os.path.join(tmpdir, "base_reader_repo"), branch="test"
        )

        repo = reader.get_repo()
        assert repo.active_branch.name == "test"
