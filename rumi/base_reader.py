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

from pathlib import Path


##########################################################################
# Class BaseReader
##########################################################################


class BaseReader():
    """
    BaseReader access the repository and init target files for translation 
    monitoring.

    Parameters
    ----------
    repo_path: string, default: "./"
        Path to the repository for translation monitoring.
    content_path: list of string, default: ["content/"]
        Path from the root of the repository to the directory that contains
        contents that require translation. Default uses the "content/" folder.
    branch: string, default: "main"
        Name of the branch to read the github history from. Default to "main".
    extension: list of string, default: ["md"]
        Extension of the target files for translation monitoring. Defult
        monitoring translation of the markdown files.
    """
    def __init__(
        self, content_path=None, extension=None, repo_path="./", branch="main", 
    ) -> None:
        """
        MsgReader reads the github history and parses it into a message
        dictionary of commit history. 
        """
        content_path = content_path or ["content/"]
        extension = extension or ["md"]
        self.repo_path = self.validate_repo_path(repo_path)
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
        # Resolve content directory to only walk it, otherwise walk entire repo
        content_path = self.repo_path.joinpath(content_path) if content_path else self.repo_path
        
        target = []
        for root, dirs, files in os.walk(content_path.resolve(), topdown=True):
                # Ignore hidden directories, e.g. things like .git or .github
                # In the future we could also use an argument to ignore
                # specific directories like node_modules (or use .rumignore)
                dirs[:] = [d for d in dirs if not self.is_hidden(d)]
                
                # Convert the root to a Path for path operations 
                root = Path(root)
                
                for fname in files:
                        # Ignore hidden files
                        if self.is_hidden(fname): continue
                        
                        # Create the Path from the file
                        path = root.joinpath(fname)
                        
                        # Check the extension, note you may want to use the more complex
                        # path.suffixes for multiple extensions e.g. myfile.en.md 
                        if path.suffix in extension:
                            target.append(path)
        return set(target)
                
    def is_hidden(basename):
        """
        Helper function that looks for a base path name that is hidden
        by the operating system (either posix or windows).
        """
        return basename.startswith(".") or basename.startswith("~")

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
        repo_path = Path(repo_path)
        if (not repo_path.exists()) or (not repo_path.is_dir()):
            raise Exception("please specify a valid repository path")
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


