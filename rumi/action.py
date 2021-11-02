import os

from reader import GitReader
from reporter import StatusReporter

pattern = os.environ['INPUT_PATTERN']

reader = GitReader(
    repo_name="rotational.io",
    repo_url="https://github.com/rotationalio/rotational.io.git",
    pattern=pattern)
commits = reader.parse_commits()
origins = reader.get_origins(commits)
langs = reader.get_langs(commits)

reporter = StatusReporter(repo_path="rotational.io/")
reporter.stats(commits, origins, langs)
reporter.detail(commits, origins, langs)