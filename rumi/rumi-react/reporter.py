# rumi.rumi-react.reporter
# Reporter for monitoring react app translation status with lingui.js
#
# Author: Tianshu Li
# Created: Nov. 3 2021

"""
Reporter for monitoring react app translation status with lingui.js
"""

##########################################################################
# Imports
##########################################################################


import os
import git
import glob
import shutil
import textwrap
import argparse

from tabulate import tabulate


##########################################################################
# Class ReactReporter
##########################################################################


class ReactReporter():
    """
    ReactReporter gets the translation needs from the react app repository
    set up with lingui.js, and report the needs in either stats mode, E.g.:
        | Language   |   Total |   Missing |   Word Count |
        |------------+---------+-----------+--------------|
        | ja         |     175 |       174 |         1204 |
        | zh         |     175 |         1 |           41 |
        | de         |     175 |         1 |           41 |
        | fr         |     175 |         1 |           41 |
        | en         |     175 |         0 |            0 |
    or detail mode, E.g.:
        ----------------------------------------------------------------------
        ja Missing: 2
        msgid1
        msgid2
        ----------------------------------------------------------------------
        zh Missing: 0
        ----------------------------------------------------------------------
        de Missing: 0
        ----------------------------------------------------------------------
        fr Missing: 1
        msgid1
        ----------------------------------------------------------------------
        en Missing: 0
    
    It also contains download_needs function to download translation needs 
    into a .txt file for each language; and a insert_done function that inserts
    translated messages back into the po files. 

    Parameters
    ----------
    repo_url: string, default: ""
        Url for cloning the repository for translation monitoring.
    repo_path: string, default: ""
        Path to a local folder that contains the react app project.
    content_path: string, default: "locales/"
        Path from the root of the repository to the directory that contains
        contents that require translation.
    """
    def __init__(self, repo_url="", repo_path="", content_path="locales/"):
        message = "Please provide either a remote repository url or the path to a local repository"
        assert not (repo_url!="" and repo_path!=""), message

        self.repo_url = repo_url
        if repo_url != "":
            self.repo_name = "repo"
            self.repo_path = self.repo_name+"/"
            self.clone_repo()
        else:
            self.validate_repo(repo_path)
        
        self.content_path = content_path

    def validate_repo(self, repo_path):
        """
        Check if the user-provided repo_path is a valid directory, if not, check
        if it is the folder name of the repository. Otherwise, message user to
        provide a valid repo_path.
        Parameters
        ----------
        repo_path: string, default: ""
            Path to the repository to monitory the translation status. Default
            uses the current path. 
        """
        if os.path.isdir(repo_path):
            if repo_path[-1] != "/":
                self.repo_path = repo_path+"/"
            else:
                self.repo_path = repo_path
        else:
            print("Please specify a valid repository path")
            self.repo_path = None 

    def clone_repo(self):
        """
        Clone the repository from a user-provided url.
        """
        if os.path.isdir(self.repo_path):
            shutil.rmtree(self.repo_path)
        
        # Clone the repo from repo_url and save it to a folder named repo_name
        git.Repo.clone_from(self.repo_url, self.repo_name)

    def get_needs(self):
        """
        Parse the po file for each language and extract msgid that are missing
        translations.

        Returns
        -------
        needs: dictionary 
            {
                lang: [list of msgid that needs to be translated]
            }
        msg_cnt: dictionary
            {
                lang: total number of msgid (int)
            }
        """
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

    def download_needs(self, path="./"):
        """
        Writes the msgid that needs to be translated into a .txt file for each
        language.

        Parameters
        ----------
        path: string, default: "./"
            Path to where the .txt file are wrote to. Default writing to the
            current path.
        """
        needs, _ = self.get_needs()
        for lang in needs:
            cnt = sum([len(s.split(" ")) for s in needs[lang]])
            filename = "{}_needing_translation.txt".format(lang)
            print("Creating file {}{}".format(path, filename))
            with open(filename, "w+") as f:
                header = "Language: {}, {} words needing translation \n".format(lang, cnt)
                f.write(header)
                for msg in needs[lang]:
                    f.write("msgid "+msg+"\n")
                    f.write('msgstr ""\n')

    def insert_done(self, file, lang):
        """
        Combine new translations together with other translations in the po file 
        of a language and generate a new file locally.

        Parameters
        ----------
        file: string
            Path to the file that contains the new translations.
        lang: string 
            Language of the translations, e.g. de, fr.
            This lang needs to be consistent with the lingui.js locale setup.
        """
        insert = {}
        with open (file, "r+") as f_insert:
            for line in f_insert.readlines():
                line = line.strip()
                if line.startswith("msgid "):
                    msgid = line.replace("msgid ", "")
                if line.startswith("msgstr "):
                    msgstr = line.replace("msgstr ", "")
                    if msgstr != '""':
                        insert[msgid] = msgstr
        print(insert)
        po_file = glob.glob("{}{}/{}/*.po".format(
            self.repo_path, self.content_path, lang
        ))[0]
        
        new_file = os.path.dirname(file)+"inserted_"+os.path.basename(file)
        f_new = open(new_file, "w+")
        with open(po_file, "r+") as f_old:
            for line in f_old.readlines():
                if line.startswith("msgid "):
                    msgid = line.strip().replace("msgid ", "")
                    f_new.write(line)
                elif line.startswith("msgstr "):
                    if msgid in insert:
                        msgstr = insert[msgid]
                        f_new.write("msgstr "+msgstr+"\n")
                    else:
                        f_new.write(line)
                else:
                    f_new.write(line)
        f_new.close()

    def stats(self, needs, msg_cnt):
        """
        Print out a summary of the translation status including number of message
        missing and word count.
        """
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
    
    def detail(self, needs):
        """
        Print out the details of messages needing translations for each language
        and provide word count.
        """
        for lang in needs:
            print("-"*70)
            print(lang, "Missing:", len(needs[lang]))
            fmt_needs = ["\n".join(textwrap.wrap(s)) for s in needs[lang]]
            print("\n".join(fmt_needs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--repo_url', type=str, default="", 
        help='Please specify the url of the repository for translation monitoring'
    )
    group.add_argument(
        '--repo_path', type=str, default="",
        help='Please specify the path to the repository'
    )
    parser.add_argument(
        '--content_path', type=str, default='locales/', 
        help='Please specify the path from the root of repository to the content to be translated'
    )

    config = parser.parse_args()

    reporter = ReactReporter(
        repo_url=config.repo_url,
        repo_path=config.repo_path,
        content_path=config.content_path
    )

    needs, msg_cnt = reporter.get_needs()
    reporter.stats(needs, msg_cnt)
    reporter.detail(needs)
    reporter.download_needs()
    reporter.insert_done("ja_translated_test.txt", "ja")