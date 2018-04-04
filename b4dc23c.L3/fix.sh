#!/bin/sh
# apply the fixing commit (extracted verbatim from historic repo)
patch -p1 -d src/ <fix.patch
