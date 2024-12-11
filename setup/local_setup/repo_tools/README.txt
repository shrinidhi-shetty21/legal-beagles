command to install the tool :
python install.py

The above command will install a pre-commit hook for git.
The hook checks for mixed indentations. ie files indented using tabs and spaces.
Ideally, we should either tabs OR spaces but not both.

Check the pre-commit.py and toggle the "tabs" and "spaces" as needed . DO NOT keep both as """True""".