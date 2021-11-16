# rumi.msg_rumi.reader
# Git history reader for message-based translation monitoring
# 
# Author: Tianshu Li
# Created: Nov.15 2021

"""
Git history reader for message-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import os
import git

from io import StringIO
from datetime import datetime
from rumi.base_reader import BaseReader


##########################################################################
# Class MsgReader
##########################################################################


class MsgReader(BaseReader):
    """
    MsgReader reads the github history, parses it into a commit dictionary,
    and also parses the source files and source and target languages.

    Parameters
    ----------
    repo_path: string, default: "./"
        Url for cloning the repository for translation monitoring.
    content_path: list of string, default: ["content/"]
        Path from the root of the repository to the directory that contains
        contents that require translation. Default uses the "content/" folder.
    branch: string, default: "main"
        Name of the branch to read the github history from. Default to "main".
    extension: list of string, default: ["md"]
        Extension of the target files for translation monitoring. Defult
        monitoring translation of the markdown files.
    src_lang: 
    """
    def __init__(
            self, content_path, extension, src_lang,
            repo_path="./", branch="main"
    ) -> None:
        """
        MsgReader reads the github history and parses it into a message
        dictionary of commit history. 
        """
        super().__init__(
            content_path=content_path, extension=extension, 
            repo_path=repo_path, branch=branch
        )
        self.src_lang = src_lang

    def parse_history(self):
        """
        Parse the output from git log command, into a dictionary of message
        commit history.

        Returns
        -------
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
        """
        repo = self.get_repo()

        commits = {}
        patterns  = {
            "new_msg": "+msgid ",
            "del_msg": "-msgid ",
            "update_msg": " msgid ",
            "new_trans": "+msgstr ",
            "del_trans": "-msgstr ",
            "dt": "Date:"
        }
        
        for tgt_file in self.targets:
            tgt_lang = self.parse_lang(tgt_file)
            command="git log -p %s".format(tgt_file)
            git_log = repo.git.execute(command=command, shell=True)

            for line in StringIO(git_log).readlines():
                # Date line
                if line.startswith(patterns["dt"]):
                    timestamp = self.parse_timestamp(line.replace(patterns["dt"]).strip())
                # When line starts with "+msgid ", save temp var msg
                elif line.startswith(patterns["new_msg"]):
                    msg = line.replace(patterns["new_msg"], "")
                # When line starts with " msgid ", save temp var msg
                elif line.startswith(patterns["update_msg"]):
                    msg = line.replace(patterns["update_msg"])
                # When line starts with "-msgid ", document the deletion, also
                # save temp var msg incase msgstr is also deleted in next line
                elif line.startswith(patterns["del_msg"]):
                    msg = line.replace(patterns["del_msg"])
                    commits[msg][tgt_lang]["lt"] = timestamp
                    commits[msg][tgt_lang]["history"].append((timestamp, "deleted"))

                elif line.startswith(patterns["new_trans"]):
                    trans = line.replace(patterns["new_trans"], "")
                    if msg == "":
                        print("Unable to parse the git history")
                    else:
                        commits[msg][tgt_lang]["lt"] = timestamp
                        commits[msg][tgt_lang]["history"].append((timestamp, trans))
                        msg = ""

                elif line.startswith(patterns["del_trans"]):
                    trans = line.replace(patterns["del_trans"], "")
                    if msg == "":
                        print("Unable to parse the git history")
                    else:
                        # When msgid isn't deleted bu msgstr is:
                        if commits[msg][tgt_lang]["lt"] != timestamp:
                            commits[msg][tgt_lang]["history"].append((timestamp, "deleted"))
                        msg = ""
        return commits

    def parse_timestamp(self, s):
        """
        Parse timestamp in git log (e.g. Thu Nov 11 22:45:36 2021 +0800) into a 
        float number of timestamp.
        """
        
        dt = datetime.strptime(s, '%a %b %d %H:%M:%S %Y %z')
        ts = float(datetime.timestamp(dt))
        return ts

    def parse_lang(self, filename):
        """
        Parse language from filename.
        """
        lang = os.path.basename(os.path.dirname(filename))
        return lang
