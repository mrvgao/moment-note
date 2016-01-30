# -*- coding:utf-8 -*-

from __future__ import with_statement

import os
import argparse

from fabric.api import *
from fabric.contrib.console import confirm

# add fabric function here

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add argument to parser
    # parser.add_argument()
    args = parser.parse_args()
    # call fabric function base on arguments
    if True:
        print 'Wrong input format, try -h'
