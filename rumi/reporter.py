# rumi.reporter
# Translation status reporter based on commit history from git
#
# Author: Tianshu Li
# Created: Oct.22 2021

"""
Translation status reporter based on commit history from git
"""

##########################################################################
# Imports
##########################################################################

import os
import argparse

from tabulate import tabulate

from reader import GitReader


##########################################################################
# Class StatusReporter
##########################################################################


class StatusReporter():
    """
    The StatusReporter can display the translation status of the static 
    site repository in two modes:
    1. stats mode: displays the number of Open (hasn't been translated), 
    Updated (source file has been updated after translation), Completed 
    (source file has been translated for all target languages). E.g.:
        | Language   |   Origin |   Open |   Updated |   Completed |
        |------------+----------+--------+-----------+-------------|
        | fr         |        0 |      0 |         0 |           0 |
        | en         |       17 |     12 |         1 |           4 |
        | zh         |        0 |      0 |         0 |           0 |
    2. detail mode: displays translation work required for each source file
    together with the word count. E.g.:
        | File             | Status   | Source Language   | Target Language   | Word Count   |
        |------------------+----------+-------------------+-------------------+--------------|
        | filename1        | Update   | en                | zh                | ?            |
        | filename2        | Open     | en                | fr                | 404          |
        | filename2        | Open     | en                | zh                | 404          |
    Parameters
    ----------
    repo_path: string, default: "./"
        Path to the repository to monitory the translation status. Default
        uses the current path. 
    
    src_lang: string, default: ""
        Language code of the source language (the original language of 
        contents) to be monitored. If not specified, all source language 
        will be monitored.
    
    tgt_lang: string, default: ""
        Language code of the target language (language to translate contents
        into) to be monitored. If not specified, all target language will 
        be monitored.
    """
    def __init__(self, repo_path="./", src_lang="", tgt_lang=""):
        self.repo_path = repo_path
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def get_num_origin(self, commits, origins, langs):
        """
        Count number of origin files in each language
        
        Parameters
        ----------
        commits: dictionary
            Commit history of the repository organized by 
            {
                "basename": {
                    "filename": {
                        "lang": "language of this file",
                        "ft": "timestamp of the first commit",
                        "lt": "timestamp of the last commit",
                    }
                }
            }
            The basename is the name of the content that is common among languages.
        origins: dictionary
            Source files (the original version of content) organized by 
            {
                "basename": {
                    "name of the source file"
                }
            }
        langs: set
            Set of all language codes contained and monitored in the repository.
        Returns
        -------
        cnt: dictionary
            Count of source files for each language organized by 
            {
                "language code": number of source files
            }
        """
        cnt = {lang: 0 for lang in langs}
        for base_file in origins:
            file = origins[base_file]
            lang = commits[base_file][file]["lang"]
            cnt[lang] += 1
        return cnt

    def get_status(self, commits, origins, langs):
        """
        Count number of source files that are Open, Updated, Completed
        
        Returns
        -------
        complete: dictionary
            Count of source files in Complete status organized by 
            {
                "language code": number of completed source files
            }
        update: dictionary
            Count of source files in Update status organized by 
            {
                "language code": number of updated source files
            }
        open: dictionary
            Count of source files in Open status organized by 
            {
                "language code": number of open source files
            }
        """
        n_langs = len(langs)
        complete = {lang: 0 for lang in langs}
        update = {lang: 0 for lang in langs}
        open = {lang: 0 for lang in langs}
        for base_file in commits:
            origin = origins[base_file]
            files = commits[base_file]
            remain, updated = n_langs, False
            for file in files:
                if file != origin:
                    if files[file]["lt"] >= files[origin]["lt"]:
                        remain -= 1
                    else:
                        updated = True
            if remain == 1:
                complete[files[origin]["lang"]] += 1
            elif updated:
                update[files[origin]["lang"]] += 1
            else:
                open[files[origin]["lang"]] += 1
        return complete, update, open

    def stats(self, commits, origins, langs):
        """
        Print out a summary of the translation status
        """
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
        """
        Estimate the word count of a given file.
        
        Parameters
        ----------
        file: string
            Name of the file.
        Returns
        -------
        wc: int
            Estimation of word count.
        """
        wc = 0
        with open(self.repo_path+file, "r+") as f:
            for line in f:
                wc += len(line.split(" "))
        return wc

    def detail(self, commits, origins, langs):
        """
        Print out the details of the work required for translating each source
        file, its Open/Update status, source and target language, and the count
        of words in the source file.
        """
        data = []
        for base_file in commits:
            origin = origins[base_file]
            files = commits[base_file]
            src_lang = files[origin]["lang"]

            # Track target languages that are complete or need update
            update_tgt_lang, complete_tgt_lang = [], []
            for file in files:
                if file != origin:
                    target_lang = files[file]["lang"]
                    if files[file]["lt"] < files[origin]["lt"]:
                        update_tgt_lang.append(target_lang)
                        if (
                            (self.src_lang=="" or self.src_lang==src_lang) and 
                            (self.tgt_lang=="" or self.tgt_lang==target_lang)
                        ):
                            data.append([origin, "Update", src_lang, target_lang, "?"])
                    else:
                        complete_tgt_lang.append(target_lang)

            # Target languages in Open status is not yet included in the commit history
            open_target_lang = [
                lang for lang in langs 
                if lang not in update_tgt_lang and lang not in complete_tgt_lang and lang != src_lang
            ]
            for target_lang in open_target_lang:
                if (
                    (self.src_lang=="" or self.src_lang==src_lang) and 
                    (self.tgt_lang=="" or self.tgt_lang==target_lang)
                ):
                    data.append([origin, "Open", src_lang, target_lang, self.word_count(file)])

        # Print detail data in tabulate format
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
        langs=config.langs
    )

    commits = reader.parse_commits()
    origins = reader.get_origins(commits)
    langs = reader.get_langs(commits)

    reporter = StatusReporter(
        repo_path=config.repo_path, 
        src_lang=config.detail_src_lang, 
        tgt_lang=config.detail_tgt_lang
    )
    reporter.stats(commits, origins, langs)
    reporter.detail(commits, origins, langs)