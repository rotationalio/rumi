import os
import re
import git
import glob
import argparse
import pandas as pd

from io import StringIO
from tabulate import tabulate


class GitReader():
    def __init__(self, congig):
        self.repo_path = config.repo_path
        self.branch = config.branch
        self.pattern = config.pattern
        self.prefix = config.content_path
        self.file_types = config.file_ext.split(" ")

        # TODO: Add all language codes
        self.all_langs = set(
            ["en", "fr", "zh", "de", "ja"]
        )
        
        self.commits = self.parse_commits(self.read_history())
        self.origins = self.get_origins()
        self.langs = self.get_langs()

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
        if self.pattern == "folder/":
            for split in file_name.split("/"):
                if split in self.all_langs:
                    lang = split
                    base_name = os.path.basename(file_name)
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
    def parse_commits(self, commits):
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

    # Get the total types of languages in the repo
    def get_langs(self):
        langs = []
        for base_file in self.commits:
            for file in self.commits[base_file]:
                langs.append(self.commits[base_file][file]["lang"])
        return set(langs)

    def get_origins(self):
        origins = {}
        for base_file in self.commits:
            st = float('inf')
            origins[base_file] = None
            for file in self.commits[base_file]:
                if self.commits[base_file][file]["ft"] < st:
                    origins[base_file] = file
                    st = self.commits[base_file][file]["lt"]
        return origins

    # Count number of origin files in each language
    def get_num_origin(self):
        cnt = {lang: 0 for lang in self.langs}
        for base_file in self.origins:
            file = self.origins[base_file]
            lang = self.commits[base_file][file]["lang"]
            cnt[lang] += 1
        return cnt
    
    # Count number of origin files that are open, updated, completed 
    def get_status(self):
        n_langs = len(self.langs)
        complete = {lang: 0 for lang in self.langs}
        update = {lang: 0 for lang in self.langs}
        open = {lang: 0 for lang in self.langs}
        for base_file in self.commits:
            origin = self.origins[base_file]
            files = self.commits[base_file]
            remain = n_langs
            for file in files:
                if file != origin:
                    if files[file]["lt"] >= files[origin]["lt"]:
                        remain -= 1
                    else:
                        update[files[file]["lang"]] = 1
            if complete == 0:
                complete[files[origin]["lang"]] += 1
            else:
                open[files[origin]["lang"]] += 1
        return complete, update, open

    # Print out a summary of the translation status
    def script(self):
        complete, update, open = self.get_status()
        origin = self.get_num_origin()
        data = []
        for lang in self.langs:
            data.append(
                [lang, origin[lang], open[lang], update[lang], complete[lang]]
            )
        print(tabulate(
            data, 
            headers=["Language", "Origin", "Open", "Updated", "Completed"], 
            tablefmt='orgtbl'
        ))

    def word_count(self, file):
        wc = 0
        with open(self.repo_path+file, "r+") as f:
            for line in f:
                wc += len(line.split(" "))
        return wc

    def detail(self, src, tgt):
        data = []
        for base_file in self.commits:
            origin = self.origins[base_file]
            files = self.commits[base_file]
            src_lang = files[origin]["lang"]

            update_target_lang = []
            for file in files:
                if file != origin:
                    target_lang = files[file]["lang"]
                    if files[file]["lt"] < files[origin]["lt"]:
                        update_target_lang.append(target_lang)
                        if (src=="" or src== src_lang) and (tgt=="" or tgt==target_lang):
                            data.append([origin, "Update", src_lang, target_lang, "?"])
            
            open_target_lang = [lang for lang in self.langs if lang not in update_target_lang and lang != src_lang]
            for target_lang in open_target_lang:
                if (src=="" or src== src_lang) and (tgt=="" or tgt==target_lang):
                    data.append([origin, "Open", src_lang, target_lang, self.word_count(file)])

        print(tabulate(
            data, 
            headers=["File", "Status", "Source Language", "Target Language", "Word Count"],
            tablefmt='orgtbl'
        ))

parser = argparse.ArgumentParser()
parser.add_argument(
    '--branch', type=str, default="main", 
    help='Please specify the name of branch to fetch the .git history'
)
parser.add_argument(
    '--repo_path', type=str, default=os.getcwd(),
    help='Please specify the path to the repository'
)
parser.add_argument(
    '--content_path', type=str, default='content/', 
    help='Please specify the path from the root of repository to the content to be translated'
)
parser.add_argument(
    '--file_ext', type=str, default='md', 
    help='Please specify the file extention of the translation files'
)
parser.add_argument(
    '--pattern', type=str, choices=["folder/", ".lang"], required=True,
    help='Please specify the pattern of how the translation files are organized'
)

parser.add_argument(
    '--script', type=bool, default=True, 
    help='Set as True if you want to display the translation monitoring board'
)
parser.add_argument(
    '--detail', type=bool, default=True, 
    help='Set as True if you want to display the translation details'
)
parser.add_argument(
    '--detail_src_lang', type=str, default="",
    help='Specify a source language to display the translation details'
)
parser.add_argument(
    '--detail_tgt_lang', type=str, default="",
    help='Specify a target language to display the translation details'
)

if __name__ == "__main__":
    config = parser.parse_args()
    reader = GitReader(config)

    if config.script:
        reader.script()
    if config.detail or config.detail_src_lang or config.detail_tgt_lang:
        reader.detail(config.detail_src_lang, config.detail_tgt_lang)

    GitReader(config)