# rumi.rumi-react.reporter
# Git history parser for monitoring react app translation status with lingui.js
#
# Author: Tianshu Li
# Created: Nov. 3 2021

"""
Git history parser for monitoring react app translation status with lingui.js
"""

##########################################################################
# Imports
##########################################################################


import glob
import textwrap
import argparse

from tabulate import tabulate


##########################################################################
# Class ReactReporter
##########################################################################


class ReactReporter():
    def __init__(self, repo_url="", content_path="locales/"):
        self.repo_url = repo_url
        self.repo_name = "repo"
        # self.repo_path = self.repo_name+"/"
        self.repo_path = repo_url
        self.content_path = content_path

    def clone_repo(self):
        if os.path.isdir(self.repo_path):
            shutil.rmtree(self.repo_path)
        
        # Clone the repo from repo_url and save it to a folder named repo_name
        git.Repo.clone_from(self.repo_url, self.repo_name)

    def get_needs(self):
        needs, msg_cnt = {}, {}
        for po_file in glob.glob(self.repo_path+self.content_path+"/*/*.po"):
            lang = po_file.split("/")[-2]
            needs[lang], msg_cnt[lang] = [], 0
            with open(po_file, "r+") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line.startswith("msgid "):
                        msgid = line.replace("msgid ", "")
                        if msgid != "":
                            msg_cnt[lang] += 1
                    if line == 'msgstr ""' and msgid != '""':
                        needs[lang].append(msgid)
        return needs, msg_cnt

    def download_needs(self):

    def insert_done(self):

    def stats(self, needs, msg_cnt):
        data = []
        for lang in needs:

            data.append([
                lang, msg_cnt[lang], len(needs[lang]), 
                sum([len(s.split(" ")) for s in needs[lang]])
            ])

        print(tabulate(
            data, 
            headers=["Language", "Total", "Missing", "Word Count"],
            tablefmt="orgtbl"
        ))
    
    def detail(self, needs, msg_cnt):
        for lang in needs:
            print("-"*70)
            print(lang, "Missing:", len(needs[lang]))
            fmt_needs = ["\n".join(textwrap.wrap(s)) for s in needs[lang]]
            print("\n".join(fmt_needs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--repo_url', type=str, default="", 
        help='Please specify the url of the repository for translation monitoring'
    )
    parser.add_argument(
        '--content_path', type=str, default='content/', 
        help='Please specify the path from the root of repository to the content to be translated'
    )

    config = parser.parse_args()

    reporter = ReactReporter(
        repo_url="../directory/",
        content_path="web/gds-ui/src/locales"
    )

    needs, msg_cnt = reporter.get_needs()
    reporter.stats(needs, msg_cnt)
    reporter.detail(needs, msg_cnt)