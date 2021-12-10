# rumi.file_rumi.reporter
# Reporter for file-based translation monitoring
#
# Author: Tianshu Li
# Created: Oct.22 2021

"""
Reporter for file-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################


from pathlib import Path
from tabulate import tabulate

from rumi.file_rumi.reader import FileReader


##########################################################################
# Class FileReporter
##########################################################################


class FileReporter:
    """
    The FileReporter can display the file-based translation status of the static
    site repository in two modes:
    1. stats mode: displays the number of Open (hasn't been translated),
    Updated (source file has been updated after translation), Completed
    (source file has been translated for all target languages). E.g.:
        | Target Language    |   Total  |   Open |   Updated |   Completed |
        |--------------------+----------+--------+-----------+-------------|
        | fr                 |        0 |      0 |         0 |           0 |
        | en                 |       17 |     12 |         1 |           4 |
        | zh                 |        0 |      0 |         0 |           0 |
    2. detail mode: displays translation work required for each target file
    together with the word count. E.g.:
        | File    | Status    | Source Language | Word Count | Target Language | Percent Completed | Percent Updated |
        |---------+-----------+-----------------+------------+-----------------+-------------------+-----------------|
        | file.md | completed | fr              |          4 | en              | 100.0%            | 0%              |
        | file.md | updated   | fr              |          4 | zh              | 50.0%             | 50.0%           |
        | file.md | open      | fr              |          4 | ja              | 0%                | 100.0%          |

    Parameters
    ----------
    repo_path: string or Path object, default: "./"
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
        self.repo_path = Path(repo_path)
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def get_stats(self, commits):
        """
        Get the translation stats from commit history after setting status.
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
                        },
                        "status": {
                            "open", "updated", "completed", or "source"
                        }
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

        for basefile in commits:
            files = commits[basefile]
            for lang in files:

                if lang not in stats:
                    stats[lang] = {"open": 0, "updated": 0, "completed": 0, "total": 0}

                status = files[lang]["status"]

                if status != "source":
                    stats[lang]["total"] += 1
                    stats[lang][status] += 1

        return stats

    def print_stats(self, stats):
        """
        Print out a summary of the translation status.
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
            data.append(
                [lang, stat["total"], stat["open"], stat["updated"], stat["completed"]]
            )

        print(
            tabulate(
                data,
                headers=["Target Language", "Total", "Open", "Updated", "Completed"],
                tablefmt="orgtbl",
            )
        )

    def get_details(self, commits):
        """
        Get details of translation needs containing File (target filename), Status
        (Open, Updated, or Completed), Source Language, Target Language, Word
        Count, and Percent Change.
        Returns
        -------
        details: list
            [{
                "basefile": name of the source file
                "status": "open" or "updated",
                "src_lang": source language,
                "tgt_lang": target language,
                "wc": word count,
                "pc": percent change
            }]
        """
        details = []
        for basefile in commits:

            files = commits[basefile]

            # Search for the src_lang
            for lang in files:
                if files[lang]["status"] == "source":
                    src_lang = lang
                    break

            # Calculate word count of the source file
            wc = self.word_count(files[src_lang]["filename"])

            for lang in files:
                status = files[lang]["status"]
                if status == "source":
                    continue
                # File in "open" status is 100% percent updated and 0% percent completed
                elif status == "open":
                    pu = 1.0
                    pc = 0
                # Compute percent updated and percent completed for file in updated status
                elif status == "updated":
                    pu, pc = self.compute_pct(files[src_lang], files[lang])
                # File in "completed" status is 0% percent updated. Note that
                # some target file's last commit time might be the same as the
                # source file but not 100% completed, pc can give an estimation
                # of translation work needed in that case
                else:
                    pu, pc = self.compute_pct(files[src_lang], files[lang])

                details.append(
                    {
                        "basefile": basefile,
                        "status": status,
                        "src_lang": src_lang,
                        "wc": str(wc),
                        "tgt_lang": lang,
                        "pc": str(round(pc, 3) * 100) + "%",
                        "pu": str(round(pu, 3) * 100) + "%",
                    }
                )

        return details

    def print_details(self, details):
        """
        Print out the details of the work required for translating each target
        file, its open/updated/completed status, source and target language, and 
        the count of words in the source file.
        """
        data = []
        for row in details:
            if (self.src_lang == "" or self.src_lang == row["src_lang"]) and (
                self.tgt_lang == "" or self.tgt_lang == row["tgt_lang"]
            ):

                data.append(
                    [
                        row["basefile"],
                        row["status"],
                        row["src_lang"],
                        row["wc"],
                        row["tgt_lang"],
                        row["pc"],
                        row["pu"],
                    ]
                )
        # Print detail data in tabulate format
        print(
            tabulate(
                data,
                headers=[
                    "File",
                    "Status",
                    "Source Language",
                    "Word Count",
                    "Target Language",
                    "Percent Completed",
                    "Percent Updated",
                ],
                tablefmt="orgtbl",
            )
        )

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
        with open(self.repo_path / file, "r+") as f:
            for line in f:
                if line.isspace():
                    continue
                wc += len(line.split(" "))
        return wc

    def compute_pct(self, src_file, tgt_file):
        """
        Compute the percentage updated and percentage completed of the tgt_file
        versus src_file.
        Parameters
        ----------
        src_file: dictionary
            Commit history of the source file:
            {
                "filename": name of the target file,
                "ft": timestamp of the first commit (float),
                "lt": timestamp of the last commit (float),
                "history": {
                    timestamp (float): [#additions, #deletions]
                },
                "status": {
                    "open", "updated", "completed", or "source"
            }

        tgt_file: dictionary
            Commit history of the target file.
        """
        src_lt, tgt_lt = src_file["lt"], tgt_file["lt"]
        src_n_lines = src_file["history"][src_lt][-1]
        tgt_n_lines = tgt_file["history"][tgt_lt][-1]

        # pu = 0 and pc = 1 for empty files
        if src_n_lines == 0:
            return 0, 1

        # Compute percentage updated: pu
        if tgt_lt >= src_lt:
            pu = 0
        else:
            # Count all additions in the source file after target file's last update timestamp
            cnt = 0
            for ts in src_file["history"]:
                if ts > tgt_lt:
                    cnt += src_file["history"][ts][0]
            pu = cnt / src_n_lines

        # Compute percentage completed: pc
        pc = tgt_n_lines / src_n_lines

        return pu, pc
