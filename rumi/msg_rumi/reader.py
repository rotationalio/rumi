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


import re
import os

from rumi.cache import Cache
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
    repo_path: string, default: "."
        Path to the repository for translation monitoring.
    branch: string, default: "main"
        Name of the branch to read the github history from. Default to "main".
    content_paths: list, default: ["content"]
        List of paths from the root of the repository to the directory that 
        contains contents for translation, e.g., ["content", "data", "i18n"]. 
        Default uses the "content" folder.
    extensions: list, default: [".md"]
        List of extensions of the target files for translation monitoring. 
        Defult monitoring translation of the markdown files.
    src_lang: string, default: "en"
        Source language as set up with lingui.js.
    use_cache: bool, default: True
        Whether to use cached commit history datastructure. 
    """

    def __init__(
        self,
        repo_path=".",
        branch="main",
        content_paths=["content"],
        extensions=[".md"],
        src_lang="en",
        use_cache=True,
    ) -> None:

        super().__init__(
            content_paths=content_paths.copy(),
            extensions=extensions.copy(),
            repo_path=repo_path,
            branch=branch,
        )
        self.src_lang = src_lang

        self.use_cache = use_cache
        if self.use_cache:
            repo_name = self.repo_path.stem
            self.cache = Cache(repo_name=repo_name, which_rumi="msg")

    def modify_commits(
        self, commits, timestamp, fname, locale, msgid, content, status, kind
    ):
        """
        Helper function to modify the commit dictionary while parsing history.

        Parameters
        ----------
        commits: dictionary
            Commit history datastructure.
        timestamp: float
            Float format of commit.authored_datetime.
        fname: string
            Target file name.
        locale:
            Target file language (locale).
        msgid: string
            Id of the message to be translated.
        content: string
            Content of a msgid or msgstr (translation) to be added.
        status: string
            Status of the modification, can be "dep", "add", "del" or "same".
        kind: string
            Kind of the modification, can be "msgid" or "msgstr".
        """

        # Case when a message is deleted
        # It's translation is marked as "deleted" in the datastructure
        if kind == "msgid" and status == "del":
            commits[content][locale]["history"].append((timestamp, '"deleted"'))
            commits[content][locale]["lt"] = timestamp

        # Case when a translation is added
        elif kind == "msgstr" and status == "add":

            # Parsing relies on one line of msgid before msgstr, will raise
            # exception if not
            if not msgid:
                raise Exception("Unable to parse file {}".format(fname))

            # Add empty dict if msgid or locale has not been documented
            if msgid not in commits:
                commits[msgid] = {}
            if locale not in commits[msgid]:
                commits[msgid][locale] = {
                    "filename": fname,
                    "ft": timestamp,
                    "lt": timestamp,
                    "history": [],
                }

            commits[msgid][locale]["history"].append((timestamp, content))
            commits[msgid][locale]["lt"] = timestamp
        return commits

    def parse_line(self, line):
        """
        Helper function to parse one line from changes of the target file
        while parsing git history.

        Returns
        -------
        content: string
            Content of msgid (source message) or msgstr (translation).
        kind: string
            Whether this line is "msgid" or "msgstr".
        status: str
            Whether this line is "dep", "add", "del", or "same". "dep" refers to
            lingui.js's documentation of deprecated messages.
        """

        if line.startswith("+msg"):
            status = "add"
        elif line.startswith("-msg"):
            status = "del"
        elif line.startswith(" msg"):
            status = "same"

        # lingui.js's deprecated messages begins with ~
        elif re.match(r"^[+|-| ]~", line):
            status = "dep"

        # Ignore other lines such as comments or file header
        else:
            return None, None, None

        splits = line.strip().split(" ")

        content = " ".join(splits[1:])
        kind = re.sub(r"[^a-z]+", "", splits[0])

        return content, status, kind

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

        # Iterate through commits from the first to the last
        if self.use_cache:
            commits = self.cache.load_cache()
            history = list(repo.iter_commits(since=self.cache.latest_date))
        else:
            commits = {}
            history = list(repo.iter_commits())

        history.reverse()
        history.append(repo.head.commit)

        for idx, commit in enumerate(history[:-1]):

            timestamp = float(datetime.timestamp(history[idx + 1].authored_datetime))

            # Iterate through each diff item in the commit
            # create_patch will create the block of actual diff lines
            for item in commit.diff(history[idx + 1], create_patch=True):

                # Check if b_path (file name after this commit) is in targets
                if item.b_path in self.targets:
                    s = item.diff.decode("utf-8")

                    lines = s.split("\n")

                    for line in lines:
                        content, status, kind = self.parse_line(line)

                        # Ignore the lines without a content
                        if not content:
                            continue

                        # Track msgid for next line
                        if kind == "msgid":
                            msgid = content

                        # Put content into the datastructure
                        fname = item.b_path
                        locale = self.parse_lang(item.b_path)

                        commits = self.modify_commits(
                            commits,
                            timestamp,
                            fname,
                            locale,
                            msgid,
                            content,
                            status,
                            kind,
                        )

        if self.use_cache:
            self.cache.write_cache(commits)

        return commits

    def parse_lang(self, filename):
        """
        Parse language from filename.
        """
        lang = os.path.basename(os.path.dirname(filename))
        return lang
