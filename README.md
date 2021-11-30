# rumi

> Not the ones speaking the same language, but the ones sharing the same feeling understand each other.   &mdash;Rumi

Rumi is a static site translation monitoring tool designed to support the localization (l10n) and internationalization (i18n) of documentation, and to facilitation the long-term maintenance of translated documentation.

Rumi currently supports two workflows for translation monitoring: file-based monitoring and message-based monitoring, both of which are described below.

## File-based Translation Monitoring Workflow

**File-based translation flow exemplified with Hugo site**
![](https://raw.githubusercontent.com/rotationalio/rumi/main/docs/images/readme/hugo-flow.png?token=ADVLS6MXMRDY2AKTXFYG2MTBV4ANG)

### 1. Create reader

```python
reader = GitReader(
        repo_path="",
        branch="main,
        content_path=["content/"],
        file_ext=["md"],
        pattern="folder/",
        langs=""
    )
```

Parameters:
`repo_path`: Path to the repository for translation monitoring.
`branch`: Name of the branch to read the github history from.
`content_path`: List of paths from the root of the repository to the directory that contains contents that require translation.
`file_ext`: List of extensions of the target files for translation monitoring.
`pattern`: Two types of patterns in which the static site repository is organized: "folder/" (organizing contents from each locale into one folder of the locale name, e.g. en/filename.md, fr/filename.md) and ".lang" (organizing contents from each locale by tagging the file name with the locale name, e.g. filename.en.md, filename.fr.md)
`langs`: Language codes joint by a white space as specified by the user. If not provided, will monitor languages currently contained in the repository.

### 2. Set Target

The target files for translation monitoring are initialized using `content_path` and `file_ext`, and it can also be specified by adding or deleting single filename.

```python
reader.add_target(filename)
reader.del_target(filename)
```

### 3. Calculate commits, origins, langs

```python
commits = reader.parse_commits()       # Structured commit history
origins = reader.get_origins(commits)  # Original target files
langs = reader.get_langs(commits)      # Target languages
```

### 4. Create reporter

```python
reporter = StatusReporter(
    repo_path=reader.repo_path,
    src_lang=detail_src_lang,
    tgt_lang=detail_tgt_lang
)
```

`src_lang`: Language code of the source language (the original language of contents) to be reported. If not specified, all source language will be reported.
`tgt_lang`: Language code of the target language (language to translate contents
into) to be reported. If not specified, all target language will be reported.

### 5. Report stats and details

stats mode: displays the number of Open (hasn't been translated), Updated (source file has been updated after translation), and Completed (source file has been translated for all target languages) for each Language. E.g.:

```python
reporter.stats(commits, origins, langs)

"""
    | Language   |   Origin |   Open |   Updated |   Completed |
    |------------+----------+--------+-----------+-------------|
    | fr         |        0 |      0 |         0 |           0 |
    | en         |       17 |     12 |         1 |           4 |
    | zh         |        0 |      0 |         0 |           0 |
"""
```

detail mode: displays translation work required for each source file together with the word count and percent change. E.g.:

```python
reporter.detail(commits, origins, langs)

"""
| File     | Status| Source Language| Target Language| Word Count| Percent Change|
|----------+-------+----------------+----------------+-----------+---------------|
| filename1| Update| en             | zh             | ?         | 50%           |
| filename2| Open  | en             | fr             | 404       | 100%          |
| filename2| Open  | en             | zh             | 404       | 100%          |
"""
```

### 6. Github Action

To setup your repository with Rumi github action so that stats and details are automated on push, include the following code in `.github/workflow/rumi.yaml`:

<!-- will be finalized after publishing this action. -->
```yaml
name: Rumi action
on: push
jobs:
  rumi:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Run Action
        # Directory path that contains action.yaml
        uses: ./
        # Pass user input as arguments
        with:
          repo_url: "https://github.com/rotationalio/rotational.io.git"
          pattern: "folder/"
```

### 7. Additional resources for the SDE steps

For more about setting up a Hugo site, check out the documentation about [Hugo in multilingual mode](https://gohugo.io/content-management/multilingual/).


## Message-based Translation Monitoring Workflow

**Message-based translation flow exemplified with React App**
![](https://raw.githubusercontent.com/rotationalio/rumi/main/docs/images/readme/react-flow.png?token=ADVLS6M34UDADK7JFLS3ZPTBV4AXY)

<!-- need updates after refactoring reporter for unified data structure -->
### 1. Create reporter

```python
reporter = ReactReporter(
    repo_path=config.repo_path,
    content_path=config.content_path
)
```

### 2. Calculate needs

```python
needs, msg_cnt = reporter.get_needs()
```

### 3. Report stats and details

stats mode: Print out a summary of the translation status including number of message missing and word count.
```python
reporter.stats(needs, msg_cnt)

"""
    | Language   |   Total |   Missing |   Word Count |
    |------------+---------+-----------+--------------|
    | ja         |     175 |       174 |         1204 |
    | zh         |     175 |         1 |           41 |
    | de         |     175 |         1 |           41 |
    | fr         |     175 |         1 |           41 |
    | en         |     175 |         0 |            0 |
"""
```

detail mode: Print out the details of messages needing translations for each language
and provide word count.

```python
reporter.detail(needs)

"""
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
    ----------------------------------------------------------------------
"""
```

### 4. Github Action

To setup your repository with Rumi github action so that stats and details are automated on push, include the following code in `.github/workflow/rumi.yaml`:

<!-- will be added after publishing this action. -->

### 5. Rumi Download

Rumi can help you download the new messages from `Lingui Extract` results:

```python
reporter.download_needs()
```

### 6. Rumi Insert Translated

Rumi can also insert the new translations back into the old ones, to support the next `Lingui Compile` step.

```python
reporter.insert_done("new_translations.txt", "old_messages.po", language_code)

```

### 7. Additional Resources for the SDE steps

Here are some additional resources for getting set up with Lingui on your React project:
  - UI Dev: Setup Lingui.js
    - Installation: [Setup Lingui with React project](https://lingui.js.org/tutorials/setup-react.html)
    - Wrap Messages: Wrap UI text message according to [Lingui patterns](https://lingui.js.org/tutorials/react-patterns.html)
  - Lingui Extract: `npm run extract` or `yarn extract`
  - Lingui Compile: `npm run compile` or `yarn compile`
