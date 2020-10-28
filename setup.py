#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import setuptools


path = os.path.join(os.path.dirname(__file__), 'lib/robust/version.py')
with open(path, 'r') as f:
    exec(f.read())


setuptools.setup(version=__version__)
