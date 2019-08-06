#!/bin/bash

# usage: ./validate.sh bugid.bug
# 
# install: https://github.com/any-json/any-json 
# install: https://github.com/jessedc/ajv-cli

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCHEMA="${DIR}/robust.json"
echo Checking schema compliance for $1
any-json --input-format=yaml $1 | ajv --verbose --errors=js -s ${SCHEMA} -d /dev/stdin 2>&1 >/dev/null | sed "s/\/dev\/stdin/File $1/"
