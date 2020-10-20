#!/bin/bash

# usage: ./validate.sh bugid.bug
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VALIDATOR="${DIR}/yamale_validator.py"
echo Checking schema compliance for $1
python3 ${VALIDATOR} $1
