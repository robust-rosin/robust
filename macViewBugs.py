#!/usr/local/bin/python3
import argparse
import sys
import os
import subprocess
#Orginal author: Zack Coker
#reads in a list of bugs, either from a file specified with the -f
#argument or from the standard input
#
#parse the file for the repo and commit hash
#open up the file in TextEdit
#open up the commit in Safari
#
#Note: This script is not perfect. It dies if the hash
#is missing or the file organization is inconsistent.

def runAppleScript(scpt, args=[]):
    p = subprocess.Popen(['osascript', '-'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
    stdout, stderr = p.communicate(scpt)
    return stdout

def readBugFile(bugName):
  fileName = subprocess.check_output(['find','.','-name',bugName]).decode("utf-8")
  fileName = fileName.rstrip()
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
        subprocess.Popen(['open','-e',bug_path])
        website = repo + "/commit/" + commit
        print("website: ",website)
        subprocess.Popen(['open','-a','Safari',website])
      input("press enter to continue...\n")
      #uncomment this next line if you want to close all tabs between each bug
      #runAppleScript('quit app "Safari"')
      runAppleScript('quit app "TextEdit"')

if __name__ == "__main__":
  main()
