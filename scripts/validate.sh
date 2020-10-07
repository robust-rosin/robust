#!/bin/bash

# usage: ./validate.sh bugid.bug

echo Checking schema compliance for $1
python3 yamale_validator.py $1
