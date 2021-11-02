# rumi.action
# Integration of rumi with github action
#
# Author: Tianshu Li
# Created: Nov.1 2021

"""
Integration of rumi with github action
"""

##########################################################################
# Imports
##########################################################################


import os

from reader import GitReader
from reporter import StatusReporter

# Get args from environemt variables
repo_url = os.environ["INPUT_REPO_URL"]
content_path = os.environ["INPUT_CONTENT_PATH"]
branch = os.environ["INPUT_BRANCH"]
file_ext = os.environ["INPUT_FILE_EXT"]
pattern = os.environ['INPUT_PATTERN']
langs = os.environ["INPUT_LANGS"]
detail_src_lang = os.environ["INPUT_DETAIL_SRC_LANG"]
detail_tgt_lang = os.environ["INPUT_DETAIL_TGT_LANG"]


##########################################################################
# Action
##########################################################################


reader = GitReader(
    repo_url=repo_url,
    content_path=content_path, 
    branch=branch, 
    file_ext=file_ext, 
    pattern=pattern,
    langs=langs)

commits = reader.parse_commits()
origins = reader.get_origins(commits)
langs = reader.get_langs(commits)

reporter = StatusReporter(reader.repo_path)

reporter.stats(commits, origins, langs)
reporter.detail(commits, origins, langs)