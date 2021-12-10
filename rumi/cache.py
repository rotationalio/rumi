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
        self.which_rumi = which_rumi
        self.date_format = "%Y-%m-%d-%H-%M-%S"
        self.cache_dir = os.path.join("cache", which_rumi, repo_name)

        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.latest_date = self.get_latest()

    def get_latest(self):
        """
        Get the date of the latest cache from cache folder. If no cache folder 
        or cache file, return timestamp "1900-1-1 00:00:00".
        Returns
        -------
        date: string
            Timestamp of the cache commit history in the format of "yyyy-mm-dd HH:MM:SS"
        """
        cache_dates = os.listdir(self.cache_dir)

        if len(cache_dates) == 0:
            latest_date = "1900-1-1 00:00:00"
        else:
            dates = []
            for date in cache_dates:
                dates.append(dt.strptime(date, self.date_format))
            latest_date = max(dates).strftime(self.date_format)
        return latest_date

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
        old_file = os.path.join(self.cache_dir, self.latest_date)

        if os.path.isfile(old_file):
            with open(old_file, "rb") as f:
                old_commits = pickle.load(f)
        else:
            old_commits = None

        date = dt.now().strftime(self.date_format)
        new_file = os.path.join(self.cache_dir, date)
        if old_commits == commits:
            os.rename(old_file, new_file)
        else:
            with open(new_file, "wb") as f:
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
        file = os.path.join(self.cache_dir, self.latest_date,)
        if os.path.isfile(file):
            with open(file, "rb") as f:
                commits = pickle.load(f)
        else:
            commits = {}
        return commits
