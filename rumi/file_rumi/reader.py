# rumi.file_rumi.reader
# Git history reader for file-based translation monitoring
#
# Author: Tianshu Li
# Created: Oct.22 2021

"""
Git history reader for file-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


import re

from pathlib import Path
from datetime import datetime
from rumi.cache import Cache
from rumi.base_reader import BaseReader

# Language Codes
ALL_LANGS = {
    "aa",
    "ab",
    "ae",
    "af",
    "ak",
    "am",
    "an",
    "ar",
    "as",
    "av",
    "ay",
    "az",
    "ba",
    "be",
    "bg",
    "bh",
    "bm",
    "bi",
    "bn",
    "bo",
    "br",
    "bs",
    "ca",
    "ce",
    "ch",
    "co",
    "cr",
    "cs",
    "cu",
    "cv",
    "cy",
    "da",
    "de",
    "dv",
    "dz",
    "ee",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "ff",
    "fi",
    "fj",
    "fo",
    "fr",
    "fy",
    "ga",
    "gd",
    "gl",
    "gn",
    "gu",
    "gv",
    "ha",
    "he",
    "hi",
    "ho",
    "hr",
    "ht",
    "hu",
    "hy",
    "hz",
    "ia",
    "id",
    "ie",
    "ig",
    "ii",
    "ik",
    "io",
    "is",
    "it",
    "iu",
    "ja",
    "jv",
    "ka",
    "kg",
    "ki",
    "kj",
    "kk",
    "kl",
    "km",
    "kn",
    "ko",
    "kr",
    "ks",
    "ku",
    "kv",
    "kw",
    "ky",
    "la",
    "lb",
    "lg",
    "li",
    "ln",
    "lo",
    "lt",
    "lu",
    "lv",
    "mg",
    "mh",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "na",
    "nb",
    "nd",
    "ne",
    "ng",
    "nl",
    "nn",
    "no",
    "nr",
    "nv",
    "ny",
    "oc",
    "oj",
    "om",
    "or",
    "os",
    "pa",
    "pi",
    "pl",
    "ps",
    "pt",
    "qu",
    "rm",
    "rn",
    "ro",
    "ru",
    "rw",
    "sa",
    "sc",
    "sd",
    "se",
    "sg",
    "si",
    "sk",
    "sl",
    "sm",
    "sn",
    "so",
    "sq",
    "sr",
    "ss",
    "st",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "ti",
    "tk",
    "tl",
    "tn",
    "to",
    "tr",
    "ts",
    "tt",
    "tw",
    "ty",
    "ug",
    "uk",
    "ur",
    "uz",
    "ve",
    "vi",
    "vo",
    "wa",
    "wo",
    "xh",
    "yi",
    "yo",
    "za",
    "zh",
    "zu",
}


##########################################################################
# Class FileReader
##########################################################################


class FileReader(BaseReader):
    """
    FileReader reads the github history, parses it into a commit dictionary,
    and also parses the source files and translation status.
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
    pattern: string, choices: "folder/", ".lang"
        Two types of patterns in which the static site repository is organized.
    langs: string, default: ""
        Language codes joint by a white space as specified by the user. If not
        specified, FileReader will try to get languages from the filenames in the
        current repository for monitoring.
    src_lang: string, default: "en"
        Default source language set by user.
    use_cache: bool, default: True
        Whether to use cached commit history datastructure. 
    """

    def __init__(
        self,
        repo_path=".",
        branch="main",
        langs="",
        content_paths=["content"],
        extensions=[".md"],
        pattern="folder/",
        src_lang="en",
        use_cache=True,
    ):
        super().__init__(
            content_paths=content_paths.copy(),
            extensions=extensions.copy(),
            repo_path=repo_path,
            branch=branch,
        )

        self.pattern = pattern
        self.src_lang = src_lang
        # rumi looks through commit history and can detect languages based on
        # filename. The detected language are saved to the commits dictionary in
        # basename: {locale: {}}. The lang_pool is the pool of valid languages to
        # support detecting. User can specify any string as languages as long as
        # it's consistent with filenames in their repository. If not specified,
        # pool will be set with lower case language codes.
        self.lang_pool = set(langs.split(" ")) if langs else ALL_LANGS
        # Specified target languages
        # self.langs is needed to keep track of the use specified languages so
        # that for a totally untranslated repository, with no languages can be
        # detected, rumi can still display translation status in each target language.
        self.langs = langs.split(" ") if langs else []

        self.use_cache = use_cache
        if self.use_cache:
            repo_name = self.repo_path.stem
            self.cache = Cache(repo_name=repo_name, which_rumi="file")

    def process_rename(self, filename):
        """
        Clean out the { xxx => xxx } renaming format in file name.
        Returns
        -------
        ori_name: string
            Original filename.
        rename: string
            Renamed filename.
        """
        rename_sign = " => "
        if rename_sign not in filename:
            return filename, None

        renamed = re.search(r"\{.+=>.+\}", filename)

        # Case when filename is "path/{ xxx => xxx }/file.md"
        if renamed:
            rename_pattern = renamed.group()

            if filename.count("=>") > 1:
                raise Exception("Unable to parse the filename {}".format(filename))
            part1, part2 = rename_pattern[1:-1].split(rename_sign)

            # Reassemble the original filename and renamed filename
            ori_name = filename.replace(rename_pattern, part1.strip())
            rename = filename.replace(rename_pattern, part2.strip())

        # Case when filename is "xxx => xxx"
        else:
            if filename.count("=>") > 1:
                raise Exception("Unable to parse the filename {}".format(filename))

            ori_name, rename = filename.split(rename_sign)
            ori_name, rename = ori_name.strip(), rename.strip()
        return ori_name, rename

    def parse_history(self):
        """
        Parse the output from git log command, into a dictionary of file commit
        history.
        Returns
        -------
        commits: dictionary
            Commit history of the repository organized by
            {
                "basename": {
                    "locale": {
                        "filename": name of the target file,
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": {
                            timestamp (float): [#additions, #deletions]
                        },
                        "status": {
                            "open", "updated", "completed", or "source"
                        }
                    }
                }
            }
            The basename is the name of the content that is common among languages.
        """
        repo = self.get_repo()

        # Iterate through commits from the first to the last
        if self.use_cache:
            commits = self.cache.load_cache()
            iter = reversed(
                list(
                    repo.iter_commits(paths=self.targets, since=self.cache.latest_date)
                )
            )
        else:
            commits = {}
            iter = reversed(list(repo.iter_commits(paths=self.targets)))

        for commit in iter:

            timestamp = float(datetime.timestamp(commit.authored_datetime))

            for file in commit.stats.files:

                ori_name, rename = self.process_rename(file)

                if rename:
                    # Change filename in commits datastructure if file is renamed
                    if ori_name in commits:
                        commits[rename] = commits.pop(ori_name)
                    fname = rename
                else:
                    fname = ori_name

                if fname not in self.targets:
                    continue

                add = commit.stats.files[file]["insertions"]
                delete = commit.stats.files[file]["deletions"]
                n_lines = commit.stats.files[file]["lines"]

                base_name, lang = self.parse_base_lang(fname)

                if not base_name:
                    raise Exception("Invalid target filename")

                if base_name not in commits:
                    commits[base_name] = {}

                # Track the first and last commit time for each locale of the basefile
                if lang in commits[base_name]:
                    if timestamp < commits[base_name][lang]["ft"]:
                        commits[base_name][lang]["ft"] = timestamp
                    elif timestamp > commits[base_name][lang]["lt"]:
                        commits[base_name][lang]["lt"] = timestamp

                    commits[base_name][lang]["history"][timestamp] = [
                        add,
                        delete,
                        n_lines,
                    ]
                else:
                    commits[base_name][lang] = {
                        "filename": fname,
                        "ft": timestamp,
                        "lt": timestamp,
                        "history": {timestamp: [add, delete, n_lines]},  # handle total
                    }

        # Determine which locale is the source for each basename
        sources = self.get_sources(commits)

        # Ensure each basename has the same set of locales
        self.set_langs(commits)

        # Set translation status for each locale of each basename
        self.set_status(commits, sources)

        if self.use_cache:
            self.cache.write_cache(commits)

        return commits

    def parse_base_lang(self, file_name):
        """
        Given a full path/to/file/filename, parse the basename and langauge with
        consideration of the two types of repository organization patterns: "folder/"
        and ".lang".
        Parameters
        ----------
        file_name: string
            Name of the file.
        Returns
        -------
        basename: string
            Name of the file content that remains unchanged among languages.
        lang: string
            Code of language used in the file.
        """
        file_name = Path(file_name)

        if self.pattern == "folder/":
            # In this pattern, lang (locale) is one of the directory name
            for dir_name in file_name.parts:
                if dir_name in self.lang_pool:
                    lang = dir_name
                    base_name = file_name.name
                    break
            if not "lang" in locals() or lang not in self.lang_pool:
                raise Exception("Unable to parse file {}".format(file_name))

        elif self.pattern == ".lang":
            # In this pattern, lang (locale) is one of the extensions
            extensions = file_name.suffixes

            for ext in extensions:

                if ext[1:] in self.lang_pool:
                    lang = ext[1:]
                    break

            if not "lang" in locals() or not lang in self.lang_pool:
                raise Exception("Unable to parse file {}".format(file_name))

            base_name = file_name.name.replace(ext, "")
        else:
            raise Exception("Unable to parse file {}".format(file_name))
        return base_name, lang

    def get_langs(self, commits):
        """
        User can define the target languages to monitor for translation
        by providing a string e.g. "en fr zh de". If the target langauges
        are not provided, the get_langs function will get langauges based
        on the file names and the ALL_LANGS set.
        Returns
        -------
        langs: set
            Set of all language codes contained and monitored in the repository.
        """

        langs = self.langs
        for base_file in commits:
            langs.extend(list(commits[base_file].keys()))

        return set(langs)

    def set_langs(self, commits):
        """
        Parse through the commit dictionary and set all locales for each basefile.
        """
        langs = self.get_langs(commits)

        for basefile in commits:
            files = commits[basefile]

            for lang in langs:
                if lang not in files:
                    files[lang] = {}

    def get_sources(self, commits):
        """
        Parse through the commit dictionary and set all source files.
        """
        sources = {}
        for base_file in commits:

            st = float("inf")

            for lang in commits[base_file]:

                file_dict = commits[base_file][lang]

                if file_dict["ft"] < st:
                    src_lang = lang
                    st = file_dict["ft"]

                # When two file have the same first commit time, use default src_lang
                elif file_dict["ft"] == st:
                    if lang == self.src_lang:
                        src_lang = lang

            sources[base_file] = src_lang

        return sources

    def set_status(self, commits, sources):
        """
        Set the translation status of source, open (hasn't been translated), 
        updated (has been changed since translation), and completed.
        Parameters
        ----------
        commits: dictionary
            Commit history of the repository organized by
            {
                "basename": {
                    "locale": {
                        "filename": name of the target file,
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": {
                            timestamp (float): [#additions, #deletions]
                        }
                    }
                }
            }
            The basename is the name of the content that is common among languages.
        Returns
        -------
        commits: dictionary
            Commit history of the repository organized by
            {
                "basename": {
                    "locale": {
                        "filename": name of the target file,
                        "ft": timestamp of the first commit (float),
                        "lt": timestamp of the last commit (float),
                        "history": {
                            timestamp (float): [#additions, #deletions]
                        },
                        "status": {
                            "open", "updated", "completed", or "source"
                        }
                    }
                }
            }
        """

        for basefile in commits:

            src_lang = sources[basefile]
            files = commits[basefile]

            for lang in files:

                if lang == src_lang:
                    files[lang]["status"] = "source"

                else:
                    # Target file with empty commit history is in status "open"
                    if files[lang] == {} or files[lang] == {"status": "open"}:
                        files[lang]["status"] = "open"

                    # Target file with last commit time not earlier than source file is "completed"
                    elif files[lang]["lt"] >= files[src_lang]["lt"]:
                        files[lang]["status"] = "completed"

                    # Target file with last commit time earlier than source file is "updated"
                    else:
                        files[lang]["status"] = "updated"
