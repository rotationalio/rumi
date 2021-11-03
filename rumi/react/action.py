import os
import git
import shutil 
import subprocess
# TODO: add requirements.txt
from docx import Document

if os.path.isdir(self.repo_path):
    shutil.rmtree(self.repo_path)

# Git clone
repo = git.Repo.clone_from(self.repo_url, self.repo_name)
repo.git.checkout(self.branch)
print("Branch switched to {}".format(self.branch))

# Run extract
def parse_extract_output(s):

    return total, missing

def extract(path):
    command = "yarn extract @"+path
    process = subprocess.run(
        ["yarn", "extract"], 
        cwd = path,
        capture_output=True
    )
    output = process.stdout.decode("utf-8")
    return command, output

# Run pack
def pack_one(po_file, docx_path):
    command = "Pack "+po_file
    document = Document()

    with open(po_file, "r+") as f:
        for idx, line in enumerate(f.readlines()):
            if line.startswith("msgid "):
                document.add_paragraph(str(idx)+" "+line.split(" ")[1])

    docx_file = po_file.split(".")[0]+".docx"
    document.save(docx_file)
    output = "Created "+docx_file
    return command, output

def pack_all(locale_path, docx_path):
    pass

# Run unpack
def unpack_one(trans_file):
    # Remember to rename unpacked trans_file 
    # Also rename the corresponding docx_file
    pass
def unpack_all(trans_path):
    pass

# Run compile
def compile(path):
    command = "yarn extract @"+path
    process = subprocess.run(
        ["yarn", "compile"],
        cwd = path,
        capture_output=True
    )
    output = process.stdout.decode("utf-8")
    return command, output

# Git push
def compose_commit():

    return message, description

def git_push(repo, branch, message, description):
    repo.git.add(update=True)
    repo.index.commit(
        "-m", message, 
        "-m", "Description... \n"+description,
        author="rumi"
    )
    origin = repo.remote(name='origin '+branch)
    origin.push()