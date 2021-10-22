import os
import git
import glob
import pandas as pd

from io import StringIO


# TODO: Add all language codes
ALL_LANGS = {
    "en", "fr", "zh", "de", "ja"
}

class GitReader():
    def __init__(
        self, repo_path="./", content_path="content/", 
        branch="main", file_ext="md", pattern="folder/",
        langs=""
    ):
        self.repo_path = repo_path
        self.branch = branch
        self.pattern = pattern
        self.prefix = content_path
        self.file_types = file_ext.split(" ")
        self.all_langs = ALL_LANGS
        self.langs = langs
        
    # Read the git history at the specified branch and preprocess the histories
    def read_history(self):
        repo = git.Repo(self.repo_path)
        repo.git.checkout(self.branch)

        git_bin = repo.git
        command = 'git log --numstat --pretty=format:"\t\t\t%h\t%at\t%aN"'
        git_log = git_bin.execute(command=command, shell=True)

        commits_raw = pd.read_csv(
            StringIO(git_log), 
            sep="\t",
            header=None,              
            names=['additions', 'deletions', 'filename', 'sha', 'timestamp', 'author']
        )
        commits = commits_raw[['additions', 'deletions', 'filename']]\
            .join(commits_raw[['sha', 'timestamp', 'author']].fillna(method='ffill'))
        commits = commits.dropna()
        return commits

    # Given a full path/to/file/filename, parse the basename and langauge
    # The basename is a name of the file content that remains unchanged among languages
    def parse_base_lang(self, file_name):
        print("parsing: =========")
        if self.pattern == "folder/":
            for split in file_name.split("/"):
                if split in self.all_langs:
                    lang = split
                    base_name = os.path.basename(file_name)

                    print(lang, base_name)
                    break
        elif self.pattern == ".lang":
            lang = file_name.split(".")[-2]
            assert lang in self.all_langs, "Invalid format of translation files"
            base_name = file_name.replace("."+lang, "")        
        return base_name, lang
    
    # Parse the processed commit into 
    # {
    #   "basename": {
    #       "filename": {
    #         "lang": language of this file,
    #         "ft": timestamp of the first commit,
    #         "lt": timestamp of the last commit,
    #     }
    #   }
    # }
    def parse_commits(self):
        commits = self.read_history()

        repo_set = set([file.replace(self.repo_path, "") for file in glob.glob(self.repo_path+"/**/*.*", recursive=True)])
        file_dict = {}
        for i in commits.index:
            file_name = commits.loc[i, "filename"]

            # Filter out files that have been deleted from the current repo, 
            # and are not in the specified content path
            if (
                file_name in repo_set and
                file_name.startswith(self.prefix) and 
                file_name.split(".")[-1] in self.file_types
            ):
                base_name, lang = self.parse_base_lang(file_name)
                commit_time = float(commits.loc[i, "timestamp"])

                if (base_name not in file_dict):
                    file_dict[base_name] = {}

                if file_name in file_dict[base_name]:
                    if commit_time < file_dict[base_name][file_name]["ft"]:
                        file_dict[base_name][file_name]["ft"] = commit_time
                    elif commit_time > file_dict[base_name][file_name]["lt"]:
                        file_dict[base_name][file_name]["lt"] = commit_time
                else:
                    file_dict[base_name][file_name] = {
                        "lang": lang,
                        "ft": commit_time,
                        "lt": commit_time
                    }

        return file_dict

    # User can define the target languages to monitor for translation
    # by providing a string e.g. "en fr zh de"
    # If the target langauges are not provided, the get_langs function 
    # will get langauges based on the file names and the ALL_LANGS set
    def get_langs(self, commits):
        if len(self.langs) > 0:
            return set(self.langs.split(" "))
        else:
            langs = []
            for base_file in commits:
                for file in commits[base_file]:
                    langs.append(commits[base_file][file]["lang"])
            return set(langs)

    def get_origins(self, commits):
        origins = {}
        for base_file in commits:
            st = float('inf')
            origins[base_file] = None
            for file in commits[base_file]:
                if commits[base_file][file]["ft"] < st:
                    origins[base_file] = file
                    st = commits[base_file][file]["lt"]
        return origins


