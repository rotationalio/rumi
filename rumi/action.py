import os

from reader import GitReader
from reporter import StatusReporter

repo_path = os.environ['INPUT_REPO_PATH']
pattern = os.environ['INPUT_PATTERN']

reader = GitReader(repo_path=repo_path, pattern=pattern,)
commits = reader.parse_commits()
origins = reader.get_origins(commits)
langs = reader.get_langs(commits)

reporter = StatusReporter(repo_path=repo_path)
reporter.stats(commits, origins, langs)
reporter.detail(commits, origins, langs)