# rumi.basereader
# Base git history reader for translation monitoring
# 
# Author: Tianshu Li
# Created: Nov.15 2021

"""
Base git history reader for translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import git
import glob


##########################################################################
# Class BaseReader
##########################################################################


class BaseReader():
    def __init__(
        self, content_path, extension, repo_path="./", branch="main", 
    ) -> None:
        """
        MsgReader reads the github history and parses it into a message
        dictionary of commit history. 
        """
        self.repo_path = self.validate_repo_path(repo_path)
        if not self.repo_path:
            return
        self.branch = branch
        self.targets = self.init_targets(content_path, extension)
    
    def get_current_repo_set(self):
        """
        Set self.targets based on content_path and file extension.

        Returns
        -------
        repo_set: set
            Set of files currently in the repository.
        """
        # Files that have been deleted are not monitored
        repo_set = set([
            file.replace(self.repo_path, "") 
            for file in glob.glob(os.path.join(self.repo_path,"**/*.*"), recursive=True)
        ])
        return repo_set

    def init_targets(self, content_path, extension):
        """
        Set self.targets based on content_path and file extension.

        Parameters
        ----------
        repo_set: set
            Set of files currently in the repository.
        content_path: string
            Path from the repo_path to the folder that contains contents for 
            translation monitoring.
        extension: list
            List of file extensions (e.g. "md", "po") for translation monitoring.

        Returns
        -------
        target: set
            Set of target files for translation monitoring.
        """
        target = []
        for file in self.get_current_repo_set():
            if file.split(".")[-1] in extension:
                for dir in content_path:
                    if file.startswith(dir):
                        target.append(file)
        return set(target)

    def validate_repo_path(self, repo_path="./"):
        """
        Allow both "repo_name/" and "repo_name" provided as repo_path.

        Parameters
        ----------
        repo_path: string, default: "./"
            Path to the repository to monitory the translation status. Default
            uses the current path. 

        Returns
        -------
        repo_path: string
            Validated repository path.
        """
        if os.path.isdir(repo_path):
            if repo_path[-1] != "/":
                repo_path = repo_path+"/"
        else:
            print("Please specify a valid repository path")
            repo_path = None 
        return repo_path

    def get_repo(self):
        """
        Access the repository at certain branch.

        Returns
        -------
        repo: object
            Gitpython Repo object.
        """
        repo = git.Repo(self.repo_path)
        print("Using locale repository {}".format(self.repo_path))
        repo.git.checkout(self.branch)
        print("Branch switched to {}".format(self.branch))
        print(repo.active_branch)
        return repo


