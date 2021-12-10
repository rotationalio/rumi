# rumi.base_reader
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

from pathlib import Path


##########################################################################
# Class BaseReader
##########################################################################


class BaseReader:
    """
    BaseReader access the repository and init target files for translation
    monitoring.

    Parameters
    ----------
    repo_path: string, default: "."
        Path to the repository for translation monitoring.
    branch: string, default: "main"
        Name of the branch to read the github history from. Default to "main".
    content_paths: list, default: ["content"]
        List of paths from the root of the repository to the directory that 
        contains contents for translation, e.g., ["content", "data", "i18n"]. 
        Default uses the "content" folder.
    extensions: list, default: [".md"]
        List of extensions of the target files for translation monitoring. 
        Defult monitoring translation of the markdown files.
    """

    def __init__(
        self,
        repo_path=".",
        branch="main",
        content_paths=["content"],
        extensions=[".md"],
    ) -> None:
        self.repo_path = self.validate_repo_path(repo_path)
        self.branch = branch
        self.targets = self.init_targets(content_paths.copy(), extensions.copy())

    def init_targets(self, content_paths, extensions):
        """
        Set self.targets based on content paths and file extensions.

        Parameters
        ----------
        content_paths: string, default: "content"
            Paths from the root of the repository to the directory that contains
            contents for translation, joined by space, e.g., "content
            data i18n". Default uses the "content" folder.
        extensions: string, default: ".md"
            Extensions of the target files for translation monitoring, joined by
            space. Defult monitoring translation of the markdown files.

        Returns
        -------
        target: set
            Set of target files (string of path from repo_path to target file)
            for translation monitoring.
        """
        target = []

        for cp in content_paths:
            # Resolve content directory to only walk it
            cp = self.repo_path.joinpath(cp)

            for root, dirs, files in os.walk(cp.resolve(), topdown=True):
                # Ignore hidden directories, e.g. things like .git or .github
                # In the future we could also use an argument to ignore
                # specific directories like node_modules (or use .rumignore)
                dirs[:] = [d for d in dirs if not self.is_hidden(d)]

                # Convert the root to a Path for path operations
                root = Path(root)

                for fname in files:
                    # Ignore hidden files
                    if self.is_hidden(fname):
                        continue

                    # Create the Path from the file relative to the repo_path
                    path = root.joinpath(fname).relative_to(self.repo_path)

                    # Check the extension, note you may want to use the more complex
                    # path.suffixes for multiple extensions e.g. myfile.en.md
                    if path.suffix in extensions:
                        target.append(str(path))
        return set(target)

    def is_hidden(self, basename):
        """
        Helper function that looks for a base path name that is hidden
        by the operating system (either posix or windows).
        """
        return basename.startswith(".") or basename.startswith("~")

    def add_target(self, target_fname):
        """
        Look for the path to the target_fname and add it to self.targets.
        """
        for root, dirs, files in os.walk(self.repo_path.resolve(), topdown=True):
            # Ignore hidden directories, e.g. things like .git or .github
            dirs[:] = [d for d in dirs if not self.is_hidden(d)]

            # Convert the root to a Path for path operations
            root = Path(root)

            for fname in files:
                if fname == target_fname:

                    # Create the Path from the file relative to the repo_path
                    path = root.joinpath(fname).relative_to(self.repo_path)

                    self.targets.add(str(path))
                    return

        raise Exception("Please provide a valid file name")

    def del_target(self, target_fname):
        """
        Delete target_fname from self.targets.
        """
        for path2file in self.targets:
            basename = os.path.basename(path2file)
            if target_fname == basename:
                self.targets.remove(path2file)
                return
        raise Exception("Please provide a valid file name")

    def validate_repo_path(self, repo_path="."):
        """
        Allow both "repo_name/" and "repo_name" provided as repo_path.

        Parameters
        ----------
        repo_path: string, default: "."
            Path to the repository to monitor the translation status.

        Returns
        -------
        repo_path: pathlib.Path object
            Validated repository path.
        """
        repo_path = Path(repo_path).resolve()

        if (not repo_path.exists()) or (not repo_path.is_dir()):
            raise Exception("Please specify a valid repository path")

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
        return repo
