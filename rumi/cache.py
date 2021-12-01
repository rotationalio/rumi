# rumi.cache
# Maintain caches for git history reader
#
# Author: Tianshu Li
# Created: Nov.11 2021

"""
Maintain caches for git history reader
"""

##########################################################################
# Imports
##########################################################################


import os
import pickle

from datetime import datetime as dt


##########################################################################
# Class Cache
##########################################################################


class Cache:
    """
    Maintain caches for git history reader to load latest cache and read 
    git history since latest cache.
    Parameters
    ----------
    repo_name: string
        Name of the repository for translation monitoring.
    which_rumi: string
        "file" or "msg" rumi.
    """

    def __init__(self, repo_name, which_rumi) -> None:
        self.repo_name = repo_name
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.cache_dir = os.path.join("cache", which_rumi)
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        self.latest_version, self.latest_date = self.get_latest()

    def get_latest(self):
        """
        Get the version and date of the latest cache from cache folder. If no
        cache folder or cache file, return version 0 and timestamp "1900-1-1 00:00:00".
        Returns
        -------
        version: int
            Version of the cache commit history.
        date: string
            Timestamp of the cache commit history in the format of  
            "yyyy-mm-dd HH:MM:SS"
        """
        dir = os.path.join(self.cache_dir, self.repo_name)
        if not os.path.isdir(dir):
            os.mkdir(dir)

        cache_names = os.listdir(dir)
        if len(cache_names) == 0:
            latest_version = 0
            latest_date = "1900-1-1 00:00:00"
        else:
            versions, dates = [], []
            for name in cache_names:
                version, date = self.parse_cache_name(name)
                versions.append(version)
                dates.append(date)
            latest_version = max([int(version) for version in versions])
            latest_date = max(dates).strftime(self.date_format)
        return latest_version, latest_date

    def parse_cache_name(self, name):
        """
        Utility function to parse the name of cache file for version and date.
        Parameters
        ----------
        name: string
            Name of the cache file.
        Returns
        -------
        version: int
            Version of the cache commit history.
        date: string
            Timestamp of the cache commit history in the format of  
            "yyyy-mm-dd HH:MM:SS"
        """
        splits = name.split(" ")
        version = splits[0][1:]
        date = dt.strptime(" ".join(splits[1:]), self.date_format)
        return version, date

    def name_cache(self, version, date):
        """
        Utility function to compose the name of cache file given version and 
        date.
        Parameters
        ----------
        version: int
            Version of the cache commit history.
        date: string
            Timestamp of the cache commit history in the format of  
            "yyyy-mm-dd HH:MM:SS"
        Returns
        -------
        name: string
            Name of the cache file.
        """
        name = os.path.join(
            self.cache_dir, self.repo_name, "v" + str(version) + " " + date
        )
        return name

    def write_cache(self, commits):
        """
        Check if the current commit history is different from the latest cache. 
        If so, write new cache version; Otherwise, update the filename of the 
        latest cache to reflect new timestamp.
        Parameters
        ----------
        commits: dictionary
            Current commit history from git reader.
        """
        date = dt.now().strftime(self.date_format)

        old_file = self.name_cache(self.latest_version, self.latest_date)
        if os.path.isfile(old_file):
            with open(old_file, "rb") as f:
                old_commits = pickle.load(f)
        else:
            old_commits = None

        if old_commits == commits:
            os.rename(old_file, self.name_cache(self.latest_version, date))
        else:
            new_version = self.latest_version + 1
            file = self.name_cache(new_version, date)
            with open(file, "wb") as f:
                pickle.dump(commits, f)

    def load_cache(self):
        """
        Load cached git history.
        Returns
        -------
        commits: dictionary
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
        file = os.path.join(
            self.cache_dir,
            self.repo_name,
            "v" + str(self.latest_version) + " " + self.latest_date,
        )
        if os.path.isfile(file):
            with open(file, "rb") as f:
                commits = pickle.load(f)
        else:
            commits = {}
        return commits
