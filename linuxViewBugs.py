#!/usr/bin/python3
import argparse
import sys
import os
import subprocess
import signal
#read in a line delimited or csv file of bug names
#parse the file for the repo and commit hash
#open up the file in gedit
#open up the commit in firefox

def readBugFile(bugName):
  fileName = subprocess.check_output(['find','.','-name',bugName]).decode("utf-8")
  fileName = fileName.rstrip()
  print(fileName)
  fin = open(fileName,'r')
  commit = None
  repo = None
  for line in fin:
    line = line.strip()
    if line.startswith('hash:'):
      commit = line.split()[1]
    elif line.startswith('repo:'):
      repo = line.split()[1]
  return (repo, commit, fileName)

def main():
  parser = argparse.ArgumentParser(description='Explore bugs in the bug database')
  parser.add_argument('-f', nargs='?', type=argparse.FileType('r'),default=sys.stdin)
  args = parser.parse_args()
  inFile = args.f
  if inFile == sys.stdin:
    print("please enter the name of the bug or restart and provide a bug list with the -f argument\n")
  for line in inFile:
    bugName = line.rstrip()
    if bugName == "":
      print("Received empty bug name. Terminating scipt")
      return
    else:
      print("bug: ",bugName)
      (repo, commit, bug_path) = readBugFile(bugName)
      textPid = None
      webPid = None
      if repo is not None and commit is not None:
        textPid = subprocess.Popen(['gedit',bug_path]).pid
        website = repo + "/commit/" + commit
        subprocess.Popen(['firefox',website])
      input("press enter to continue...\n")
      #uncomment these next two lines if you want the text summaries to persist between multiple bugs
      if textPid != None: 
        os.kill(textPid,signal.SIGTERM);
      #closing tabs that were openned by the script are more complex, so I've left it as a todo for someone who wants that feature

if __name__ == "__main__":
  main()
