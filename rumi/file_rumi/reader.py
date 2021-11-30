# rumi.reader
# Git history reader for monitoring translation status
#
# Author: Tianshu Li
# Created: Oct.22 2021

"""
Git history reader for monitoring translation status
"""

##########################################################################
# Imports
##########################################################################


import os
import re
import git
import glob
import string
import shutil
import argparse
import pandas as pd

from io import StringIO
from version import Version

# Language Codes
ALL_LANGS = {
    "aa",
    "ab",
    "ae",
    "af",
    "ak",
    "am",
    "an",
    "ar",
    "as",
    "av",
    "ay",
    "az",
    "ba",
    "be",
    "bg",
    "bh",
    "bm",
    "bi",
    "bn",
    "bo",
    "br",
    "bs",
    "ca",
    "ce",
    "ch",
    "co",
    "cr",
    "cs",
    "cu",
    "cv",
    "cy",
    "da",
    "de",
    "dv",
    "dz",
    "ee",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "ff",
    "fi",
    "fj",
    "fo",
    "fr",
    "fy",
    "ga",
    "gd",
    "gl",
    "gn",
    "gu",
    "gv",
    "ha",
    "he",
    "hi",
    "ho",
    "hr",
    "ht",
    "hu",
    "hy",
    "hz",
    "ia",
    "id",
    "ie",
    "ig",
    "ii",
    "ik",
    "io",
    "is",
    "it",
    "iu",
    "ja",
    "jv",
    "ka",
    "kg",
    "ki",
    "kj",
    "kk",
    "kl",
    "km",
    "kn",
    "ko",
    "kr",
    "ks",
    "ku",
    "kv",
    "kw",
    "ky",
    "la",
    "lb",
    "lg",
    "li",
    "ln",
    "lo",
    "lt",
    "lu",
    "lv",
    "mg",
    "mh",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "na",
    "nb",
    "nd",
    "ne",
    "ng",
    "nl",
    "nn",
    "no",
    "nr",
    "nv",
    "ny",
    "oc",
    "oj",
    "om",
    "or",
    "os",
    "pa",
    "pi",
    "pl",
    "ps",
    "pt",
    "qu",
    "rm",
    "rn",
    "ro",
    "ru",
    "rw",
    "sa",
    "sc",
    "sd",
    "se",
    "sg",
    "si",
    "sk",
    "sl",
    "sm",
    "sn",
    "so",
    "sq",
    "sr",
    "ss",
    "st",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "ti",
    "tk",
    "tl",
    "tn",
    "to",
    "tr",
    "ts",
    "tt",
    "tw",
    "ty",
    "ug",
    "uk",
    "ur",
    "uz",
    "ve",
    "vi",
    "vo",
    "wa",
    "wo",
    "xh",
    "yi",
    "yo",
    "za",
    "zh",
    "zu",
}


##########################################################################
# Class GitReader
##########################################################################


class GitReader:
    """
    GitReader reads the github history, parses it into a commit dictionary,
    and also parses the source files and source and target languages.

    Parameters
    ----------
    repo_url: string, default: ""
        Url for cloning the repository for translation monitoring.
    content_path: list of string, default: ["content/"]
        Path from the root of the repository to the directory that contains
        contents that require translation. Default uses the "content/" folder.
    branch: string, default: "main"
        Name of the branch to read the github history from. Default to "main".
    file_ext: list of string, default: ["md"]
        Extension of the target files for translation monitoring. Defult
        monitoring translation of the markdown files.
    pattern: string, choices: "folder/", ".lang"
        Two types of patterns in which the static site repository is organized.
    langs: string, default: ""
        Language codes joint by a white space as specified by the user. If not
        specified, GitReader will try to get languages from the filenames in the
        current repository for monitoring.
    src_lang: string, default: "en"
        Default source language set by user.

    Attributes
    ----------
    file_types: list
        List of file_types such as "md" or "po" that require translation monitoring.
    all_lang: set
        Set of all language codes.
    """

    def __init__(
        self,
        repo_url="",
        repo_path="",
        branch="main",
        langs="",
        content_path=["content/"],
        file_ext=["md"],
        pattern="folder/",
        src_lang="en",
    ):
        message = "Please provide either a remote repository url or the path to a local repository"
        assert not (repo_url != "" and repo_path != ""), message

        self.repo_url = repo_url
        if repo_url != "":
            self.repo_name = os.path.basename(repo_url).replace(".git", "")
            self.repo_path = self.repo_name + "/"
        else:
            self.validate_repo(repo_path)
        self.branch = branch
        self.langs = langs
        self.content_path = content_path
        self.pattern = pattern

        self.file_types = file_ext
        self.all_langs = ALL_LANGS

        self.version = Version(self.repo_name)
        self.repo_set = self.get_current_repo()
        self.targets = self.init_targets()

        self.src_lang = src_lang

    def get_current_repo(self):
        # Files that have been deleted are not monitored
        repo_set = set(
            [
                file.replace(self.repo_path, "")
                for file in glob.glob(self.repo_path + "**/*.*", recursive=True)
            ]
        )
        return repo_set

    def validate_repo(self, repo_path):
        """
        Check if the user-provided repo_path is a valid directory, if not, check
        if it is the folder name of the repository. Otherwise, message user to
        provide a valid repo_path.
        Parameters
        ----------
        repo_path: string, default: "./"
            Path to the repository to monitory the translation status. Default
            uses the current path.
        """
        if os.path.isdir(repo_path):
            if repo_path[-1] != "/":
                self.repo_path = repo_path + "/"
            else:
                self.repo_path = repo_path
            self.repo_name = os.path.basename(os.path.dirname(self.repo_path))
        else:
            print("Please specify a valid repository path")
            self.repo_path = None
            self.repo_name = None

    def get_repo(self):
        if self.repo_url != "":
            if os.path.isdir(self.repo_path):
                shutil.rmtree(self.repo_path)

            # Clone the repo using user-passing repo_url and save it to a folder named repo_name
            repo = git.Repo.clone_from(self.repo_url, self.repo_name)
        else:
            repo = git.Repo(self.repo_path)
            print("Using locale repository {}".format(self.repo_path))
        repo.git.checkout(self.branch)
        print("Branch switched to {}".format(self.branch))
        return repo

    def read_history(self, start_time):
        """
        Read the git history at the specified branch and preprocess the histories.

        Returns
        -------
        commits: pandas DataFrame
        """
        repo = self.get_repo()

        command = 'git log --numstat --pretty=format:"\t\t\t%h\t%at\t%aN" --since="{}"'.format(
            start_time
        )
        git_log = repo.git.execute(command=command, shell=True)

        commits_raw = pd.read_csv(
            StringIO(git_log),
            sep="\t",
            header=None,
            names=["additions", "deletions", "filename", "sha", "timestamp", "author"],
        )
        commits = commits_raw[["additions", "deletions", "filename"]].join(
            commits_raw[["sha", "timestamp", "author"]].fillna(method="ffill")
        )
        commits = commits.dropna()
        return commits

    def parse_base_lang(self, file_name):
        """
        Given a full path/to/file/filename, parse the basename and langauge with
        consideration of the two types of repository organization patterns: "folder/"
        and ".lang".

        Parameters
        ----------
        file_name: string
            Name of the file.

        Returns
        -------
        basename: string
            Name of the file content that remains unchanged among languages.

        lang: string
            Code of language used in the file.
        """
        base_name, lang = None, None
        if self.pattern == "folder/":
            for split in file_name.split("/"):
                if split in self.all_langs:
                    lang = split
                    base_name = os.path.basename(file_name)
                    break
        elif self.pattern == ".lang":
            lang = file_name.split(".")[-2]
            assert lang in self.all_langs, "Invalid format of translation files"
            base_name = file_name.replace("." + lang, "")
        return base_name, lang

    def add_target(self, filename):
        for path2file in self.repo_set:
            basename = os.path.basename(path2file)
            if filename == basename:
                self.targets.add(path2file)
                return
        print("Please provide a valid file name")
        return

    def del_target(self, filename):
        for path2file in self.repo_set:
            basename = os.path.basename(path2file)
            if filename == basename:
                self.targets.remove(path2file)
                return
        print("Please provide a valid file name")
        return

    def init_targets(self):
        target = []
        for file in self.repo_set:
            if file.split(".")[-1] in self.file_types:
                for dir in self.content_path:
                    if file.startswith(dir):
                        target.append(file)
        return set(target)

    def parse_commits(self):
        """
        Parse the processed commits.

        Returns
        -------
        file_dict: dictionary
            Commit history of the repository organized by
            {
                "basename": {
                    "filename": {
                        "lang": "language of this file",
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": {
                            timestamp (float): [#additions, #deletions]
                        }
                    }
                }
            }
            The basename is the name of the content that is common among languages.
        """
        commits = self.read_history(self.version.latest_date)

        repo_set = set(
            [
                file.replace(self.repo_path, "")
                for file in glob.glob(self.repo_path + "**/*.*", recursive=True)
            ]
        )

        file_dict = self.version.load_cache()

        for i in commits.index:
            file_name = commits.loc[i, "filename"]
            add = commits.loc[i, "additions"]
            add = 0 if add == "-" else int(add)
            delete = commits.loc[i, "deletions"]
            delete = 0 if delete == "-" else int(delete)

            # Clean out the { *** => ***} format in file name
            path_hack = re.search(r"\{.+\}", file_name)
            rename_sign = " => "
            if path_hack:
                path_hack = path_hack.group()
                file_name = file_name.replace(
                    path_hack, path_hack[1:-1].split("=>")[-1].strip()
                )
            elif rename_sign in file_name:
                rename = file_name.split(rename_sign)[-1]
                file_name = rename
            if file_name in self.targets:
                base_name, lang = self.parse_base_lang(file_name)
                if not base_name:
                    continue
                commit_time = float(commits.loc[i, "timestamp"])

                if base_name not in file_dict:
                    file_dict[base_name] = {}

                if file_name in file_dict[base_name]:
                    if commit_time < file_dict[base_name][file_name]["ft"]:
                        file_dict[base_name][file_name]["ft"] = commit_time
                    elif commit_time > file_dict[base_name][file_name]["lt"]:
                        file_dict[base_name][file_name]["lt"] = commit_time

                    file_dict[base_name][file_name]["history"][commit_time] = [
                        add,
                        delete,
                    ]
                else:
                    file_dict[base_name][file_name] = {
                        "lang": lang,
                        "ft": commit_time,
                        "lt": commit_time,
                        "history": {commit_time: [add, delete]},
                    }

        self.version.write_cache(file_dict)
        return file_dict

    def get_langs(self, commits):
        """
        User can define the target languages to monitor for translation
        by providing a string e.g. "en fr zh de". If the target langauges
        are not provided, the get_langs function will get langauges based
        on the file names and the ALL_LANGS set.

        Returns
        -------
        langs: set
            Set of all language codes contained and monitored in the repository.
        """
        if self.langs != "":
            # Verify the specified language string is valid
            allowed = set(string.ascii_lowercase + string.whitespace)
            assert (
                set(self.langs) <= allowed
            ), "Invalid languages specified. Only lowercase letters and whitespace are allowed"
            return set(self.langs.split(" "))
        else:
            langs = []
            for base_file in commits:
                for file in commits[base_file]:
                    langs.append(commits[base_file][file]["lang"])
            return set(langs)

    def get_origins(self, commits):
        """
        Parse through the commit dictionary and get all source files.

        Returns
        -------
        origins: dictionary
            Source files (the original version of content) organized by
            {
                "basename": {
                    "name of the source file"
                }
            }
        """
        origins = {}
        for base_file in commits:
            st = float("inf")
            origins[base_file] = None
            for file in commits[base_file]:
                file_dict = commits[base_file][file]
                if file_dict["ft"] < st:
                    origins[base_file] = file
                    st = file_dict["ft"]
                elif file_dict["ft"] == st:
                    if file_dict["lang"] == self.src_lang:
                        origins[base_file] = file
        return origins


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--repo_url",
        type=str,
        default="",
        help="Please specify the url of the repository for translation monitoring",
    )
    group.add_argument(
        "--repo_path",
        type=str,
        default="",
        help="Please specify the path to the repository",
    )
    parser.add_argument(
        "--content_path",
        nargs="+",
        default=["content/"],
        help="Please specify the path from the root of repository to the content to be translated",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Please specify the name of branch to fetch the .git history",
    )
    parser.add_argument(
        "--file_ext",
        nargs="+",
        default=["md"],
        help="Please specify the file extension of the translation files",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        choices=["folder/", ".lang"],
        required=True,
        help="Please specify the pattern of how the translation files are organized",
    )
    parser.add_argument(
        "--langs",
        type=str,
        required=False,
        default="",
        help='Target languages to monitor for translation, e.g. "en zh ja" ',
    )

    config = parser.parse_args()
    reader = GitReader(
        repo_url=config.repo_url,
        repo_path=config.repo_path,
        content_path=config.content_path,
        branch=config.branch,
        file_ext=config.file_ext,
        pattern=config.pattern,
        langs=config.langs,
    )

    commits = reader.parse_commits()
    origins = reader.get_origins(commits)
    langs = reader.get_langs(commits)
