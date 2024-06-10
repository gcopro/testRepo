import os
import subprocess
import re
import difflib

# takes the file path of any file and reads it to a string
def fileContentToString(path):
    # if the file is not a text file, we will store the contents in a string
    with open(path, "r") as ourFile:
        content = ourFile.read()

    # content is of type string so we will pass this to the LLM
    return content

# retrieve the code diff based on hash value or id num
def codeDiffToString(destPath, ch1, ch2):
    # download the code diff to local and write to local txt file
    diffFile = os.path.join(destPath, "diff.txt")
    
    # opens the diff.txt file and writes to it
    try:
        with open(diffFile, "w") as file:
            subprocess.run(["git", "diff", ch1, ch2], stdout=file, 
                           stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff command: {e}")

    # return the content as a string
    return fileContentToString(destPath + "diff.txt")

# retrieve the latest original code and return the content as string
def pullOriginToString(destPath, fileComp, diffPath):
    # since we have the CanvasCommons package, we can pull from local
    # we should always update before doing the analysis
    oriContent = ""

    # read from file locally
    try:
        with open(destPath + fileComp, "r") as file:
            oriContent = file.read()
    except:
        print("BAD")

    try:
        with open(diffPath + "orig.txt", "w") as file:
            file.write(oriContent)
            file.close()
    except:
        print("BAD")

    return oriContent

# creates a list of files that exist and new files that were added
def makeFileList(diffContent):
    oldFiles = []
    newFiles = []
    files = {}

    for line in diffContent.split('\n'):
        if line.startswith("diff --git"):
            continue
        if line.startswith("+++") or line.startswith("---"):
            filePath = line.split()[-1]
            if filePath == "/dev/null":
                continue
            if line.startswith("+++"):
                filePath = filePath[1:]
                newFiles.append(filePath)
            elif line.startswith("---"):
                filePath = filePath[1:]
                oldFiles.append(filePath)
            if len(oldFiles) == len(newFiles):
                if oldFiles[len(oldFiles) - 1] == newFiles[len(newFiles) - 1]:
                    oldFiles.pop()
                    newFiles.pop()
    
    return oldFiles, newFiles