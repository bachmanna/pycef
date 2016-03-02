# Copyright (c) 2016 The PyCEF Authors. All rights reserved.

"""Run all unit tests."""

import os
from os.path import dirname, join, realpath
import subprocess


if __name__ == "__main__":
    os.chdir(join(dirname(realpath(__file__)), "../unittests"))
    subprocess.call(["python", "_run.py"])
