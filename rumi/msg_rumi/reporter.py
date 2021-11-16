# rumi.msg_rumi.reporter
# Reporter for message-based translation monitoring
#
# Author: Tianshu Li
# Created: Nov. 3 2021

"""
Reporter for message-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import git
import textwrap

from tabulate import tabulate


##########################################################################
# Class MsgReporter
##########################################################################


class MsgReporter():
    """
    MsgReporter gets the translation needs from the react app repository
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
    """
        
    def get_stats(self, commits, src_lang):
        """
        Get the translation stats of Total (number of items to be translated),
        Open (hasn't been translated), Updated (has been changed since translation),
        and Completed.

        Parameters
        ----------
        commits: dictionary
            {
                message: {
                    locale: {
                        "filename": name of the file that contains target message,
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": [
                            (timestamp (float), translation)
                        ]
                    }
                }
            }

        Returns
        -------
        stats: dictionary
            {
                locale: {
                    "total": int, 
                    "open": int, 
                    "updated": int,
                    "completed": int
                }
            }
        """
        stats = {}

        for msg in commits:
            src_lt = commits[msg][src_lang]["lt"]
            for locale in commits[msg]:
                if locale == src_lang: pass
                if not (locale in stats):
                    stats[locale] = {
                        "total": 0, "open": 0, "updated": 0, "completed": 0
                    }
                
                stats[locale]["total"] += 1

                tgt_lt = commits[msg][locale]["lt"]
                
                if src_lt < tgt_lt:
                    stats[locale]["completed"] += 1
                elif src_lt == tgt_lt:
                    stats[locale]["open"] += 1
                else:
                    stats[locale]["updated"] += 1
                
        return stats

    def get_details(self, commits, src_lang):
        """
        Get the details of translation work needed for each target language.

        Parameters
        ----------
        commits: dictionary
            {
                message: {
                    locale: {
                        "filename": name of the file that contains target message,
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": [
                            (timestamp (float), translation)
                        ]
                    }
                }
            }

        Returns
        -------
        details: dictionary
            {
                locale: {
                    "open": int, 
                    "msgs": list
                    "wc": int
                }
            }
        """
        details = {}

        for msg in commits:
            src_lt = commits[msg][src_lang]["lt"]
            for locale in commits[msg]:
                if locale == src_lang: pass
                if not (locale in details):
                    details[locale] = {
                        "open": 0, "msgs": [], "wc": 0
                    }
                tgt_lt = commits[msg][locale]["lt"]
                if src_lt == tgt_lt:
                    details[locale]["open"] += 1
                    details[locale]["msgs"].append(msg)
                    details[locale]["wc"] += len(" ".split(msg))
        return details

    def stats(self, stats):
        """
        Print out a summary of the translation status including number of message
        missing and word count.

        Parameters
        ----------
        stats: dictionary
            {
                locale: {
                    "total": int, 
                    "open": int, 
                    "updated": int,
                    "completed": int
                }
            }
        """
        data = []
        for lang in stats:
            stat = stats[lang]
            data.append([
                lang, stat["total"], stat["open"], stat["updated"], stat["completed"]
            ])

        print(tabulate(
            data, 
            headers=["Language", "Total", "Open", "Updated", "Completed"],
            tablefmt="orgtbl"
        ))
    
    def detail(self, details):
        """
        Print out the details of messages needing translations for each language
        and provide word count.

        Parameters
        ----------
        details: dictionary
            {
                locale: {
                    "open": int, 
                    "msgs": list
                    "wc": int
                }
            }
        """
        for lang in details:
            detail = details[lang]
            print("-"*70)
            print(lang, "Open:", detail["wc"])
            # Format msg with textwrap
            fmt_msgs = ["\n".join(textwrap.wrap(s)) for s in detail["msgs"]]
            print("\n".join(fmt_msgs))
        print("-"*70)
        

    def download_needs(self, details, path="./"):
        """
        Writes the msgid that needs to be translated into a .txt file for each
        language.

        Parameters
        ----------
        details: dictionary
            {
                locale: {
                    "open": int, 
                    "msgs": list
                    "wc": int
                }
            }
        path: string, default: "./"
            Path to where the .txt file are wrote to. Default writing to the
            current path.
        """

        for lang in details:
            detail = details[lang]
            filename = "{}_needing_translation.txt".format(lang)
            print("Creating file {}{}".format(path, filename))
            with open(filename, "w+") as f:
                header = "Language: {}, {} words needing translation \n".format(lang, detail["wc"])
                f.write(header)
                for msg in details["msgs"]:
                    f.write("msgid "+msg+"\n")
                    f.write('msgstr ""\n')

    def insert_done(self, file, po_file, lang):
        """
        Combine new translations together with other translations in the po file 
        of a language and generate a new file locally.

        Parameters
        ----------
        file: string
            Path to the file that contains the new translations.
        po_file: string
            Name of the po file as used with lingui.js.
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
        
        file = os.path.join(self.repo_path, self.content_path, lang, po_file)
        if not os.path.isfile(file):
            print("Please ensure there are po files in this locale by running lingui extract")
        
        new_file = os.path.dirname(file)+"inserted_"+os.path.basename(file)
        f_new = open(new_file, "w+")
        with open(file, "r+") as f_old:
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