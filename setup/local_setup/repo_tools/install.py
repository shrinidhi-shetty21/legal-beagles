#!/usr/bin/env python3

import os
import subprocess

file_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])
cur_dir = "/".join(file_dir.split("/")[:-3])
pre_commit_file = file_dir + "/pre-commit.py"
git_hooks_precommit_file = cur_dir + "/.git/hooks/pre-commit"
copy_file_process = subprocess.Popen("cp -v " + pre_commit_file + " " + git_hooks_precommit_file, shell=True)
copy_file_process.wait()
chmod_precommit_file = subprocess.Popen("chmod 775 " + git_hooks_precommit_file, shell=True)
chmod_precommit_file.wait()
