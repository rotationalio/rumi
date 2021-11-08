import os
import pickle

from datetime import datetime as dt

class Version():
    def __init__(self, repo_name) -> None:
        self.repo_name = repo_name
        self.date_format = '%Y-%m-%d %H:%M:%S'
        self.cache_dir = "cache/"
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        self.latest_version, self.latest_date = self.get_latest()

    def get_latest(self):
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
        splits = name.split(" ")
        version = splits[0][1:]
        date = dt.strptime(" ".join(splits[1:]), self.date_format)
        return version, date
    
    def name_cache(self, version, date):
        name = os.path.join(
            self.cache_dir, self.repo_name, "v"+str(version)+" "+date
        )
        return name

    def write_cache(self, commits):
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
            file = os.path.join(
                self.cache_dir, self.repo_name, "v"+str(new_version)+" "+date
            )
            with open(file, "wb") as f:
                pickle.dump(commits,f)

    def load_cache(self):
        file = os.path.join(
            self.cache_dir, self.repo_name, 
            "v"+str(self.latest_version)+" "+self.latest_date
        )
        if os.path.isfile(file):
            with open(file, "rb") as f:
                commits = pickle.load(f)
        else:
            commits = {}
        return commits

