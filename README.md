# rumi

> Not the ones speaking the same language, but the ones sharing the same feeling understand each other.   &mdash;Rumi

A static site translation monitoring tool

## File-based Translation Monitoring Functions

- Create reader

```python
reader = GitReader(
        repo_path="",
        content_path=["content/"],
        branch="main, 
        file_ext=["md"], 
        pattern="folder/",
        langs=""
    )
```

Parameters:  
`repo_path`: Path to the repository for translation monitoring.    
`content_path`: List of paths from the root of the repository to the directory that contains contents that require translation.  
`branch`: Name of the branch to read the github history from.  
`file+ext`: List of extensions of the target files for translation monitoring.  
`pattern`: Two types of patterns in which the static site repository is organized: "folder/" (organizing contents from each locale into one folder of the locale name, e.g. en/content_file.md, fr/content_file.md) and ".lang" (organizing contents from each locale by tagging the file name with the locale name, e.g. content_file.en.md, content_file.fr.md)  
`langs`: Language codes joint by a white space as specified by the user. If not provided, will monitor languages currently contained in the repository.  

- Set Target

```python
reader.add_target(filename)
reader.del_target(filename)
```

- Calculate commits, origins, langs
- Create reporter
- Report stats and details
- Github Action

## Message-based Translation Monitoring Functions

- Create reporter
- Calculate needs
- Report stats and details
- Github Action

### React App Use Case

- UI Dev: Setup Lingui.js
- UI Dev: Wrap Messages
- Lingui Extract
- Rumi Download
- Translator
- Rumi Insert Translated
- Lingui Compile
- Github Action



