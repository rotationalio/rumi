#
# Filename: reporter.py
# Author: Tianshu Li
# Date: Oct.22 2021
#


import os
import argparse

from tabulate import tabulate

from reader import GitReader

class StatusReporter():
    def __init__(self, repo_path="./", src_lang="", tgt_lang=""):
        self.repo_path = repo_path
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    # Count number of origin files in each language
    def get_num_origin(self, commits, origins, langs):
        cnt = {lang: 0 for lang in langs}
        for base_file in origins:
            file = origins[base_file]
            lang = commits[base_file][file]["lang"]
            cnt[lang] += 1
        return cnt
    
    # Count number of origin files that are open, updated, completed 
    def get_status(self, commits, origins, langs):
        n_langs = len(langs)
        complete = {lang: 0 for lang in langs}
        update = {lang: 0 for lang in langs}
        open = {lang: 0 for lang in langs}
        for base_file in commits:
            origin = origins[base_file]
            files = commits[base_file]
            remain = n_langs
            for file in files:
                if file != origin:
                    if files[file]["lt"] >= files[origin]["lt"]:
                        remain -= 1
                    else:
                        update[files[file]["lang"]] = 1
            if remain == 1:
                complete[files[origin]["lang"]] += 1
            else:
                open[files[origin]["lang"]] += 1
        return complete, update, open

    # Print out a summary of the translation status
    def script(self, commits, origins, langs):
        complete, update, open = self.get_status(commits, origins, langs)
        origin = self.get_num_origin(commits, origins, langs)
        data = []
        for lang in langs:
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

    def detail(self, commits, origins, langs):
        data = []
        for base_file in commits:
            origin = origins[base_file]
            files = commits[base_file]
            src_lang = files[origin]["lang"]
            
            update_target_lang = []
            for file in files:
                if file != origin:
                    target_lang = files[file]["lang"]
                    if files[file]["lt"] < files[origin]["lt"]:
                        update_target_lang.append(target_lang)
                        
                        if (self.src_lang=="" or self.src_lang==src_lang) and (self.tgt_lang=="" or self.tgt_lang == target_lang):
                            data.append([origin, "Update", src_lang, target_lang, "?"])
            
            open_target_lang = [lang for lang in langs if lang not in update_target_lang and lang != src_lang]
            for target_lang in open_target_lang:
                if (self.src_lang=="" or self.src_lang== src_lang) and (self.tgt_lang=="" or self.tgt_lang == target_lang):
                    data.append([origin, "Open", src_lang, target_lang, self.word_count(file)])

        print(tabulate(
            data, 
            headers=["File", "Status", "Source Language", "Target Language", "Word Count"],
            tablefmt='orgtbl'
        ))


if __name__ == "__main__":
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
        '--langs', type=str, required=False,
        help='Target languages to monitor for translation, e.g. "en zh ja" '
    )

    parser.add_argument(
        '--detail_src_lang', type=str, default="",
        help='Specify a source language to display the translation details'
    )
    parser.add_argument(
        '--detail_tgt_lang', type=str, default="",
        help='Specify the target language to display the translation details'
    )

    config = parser.parse_args()
    reader = GitReader(
        repo_path=config.repo_path, 
        content_path=config.content_path, 
        branch=config.branch, 
        file_ext=config.file_ext, 
        pattern=config.pattern,
    )

    commits = reader.parse_commits()
    origins = reader.get_origins(commits)
    langs = reader.get_langs(commits)

    reporter = StatusReporter(
        repo_path=config.repo_path, 
        src_lang=config.detail_src_lang, 
        tgt_lang=config.detail_tgt_lang
    )
    reporter.script(commits, origins, langs)
    reporter.detail(commits, origins, langs)






