#!/usr/bin/env python

# Copyright (c) 2018, G.A. vd. Hoorn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# yes, this could have been done with urllib(2) or requests and json, but
# future extensions / other utils will probably use PyGitHub as well.

import os
import sys
import argparse
import urlparse

try:
    from github import Github
except:
    sys.stderr.write("Cannot import PyGitHub, do you have it installed?\n")
    sys.exit(os.EX_UNAVAILABLE)

parser = argparse.ArgumentParser()
parser.add_argument('URL', help='Issue url.')
args = parser.parse_args()

issue_url = args.URL
# see if this is a complete url (crude check)
if 'http' in issue_url:
    import urllib
    issue_url = urlparse.urlparse(issue_url).path

splits = issue_url.split('/')
repo, issue_nr = '{}/{}'.format(splits[1], splits[2]), int(splits[-1])

g = Github()
issue = g.get_repo(repo).get_issue(issue_nr)

# github issue creation dates are UTC
print (issue.created_at.isoformat() + 'Z')
