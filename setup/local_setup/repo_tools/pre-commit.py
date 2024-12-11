#!/usr/bin/env python3

import os
import sys
import subprocess

print("INDENTATION CHECKS..")
tabs = False
spaces = True
output = True
exit_status = 0
get_files_to_be_committed = subprocess.Popen("git status -s | grep -E '^\?\?|^ *M|^ *A' | grep -i -e py$ -e sls$", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip().split(b"\n")

for file_to_commit in get_files_to_be_committed:
    if file_to_commit:
        # The file names obtained are in Bytes, need to decode to obtain string.
        file_name = (file_to_commit.split()[1]).decode()
        print((str(file_name) + " : "))
        p_space_list = subprocess.Popen("grep -n -P \"^  *\" " + file_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].split(b"\n")
        p_tabs_list = subprocess.Popen("grep -n -P \"^\\t\\t*\" " + file_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].split(b"\n")
        # Check present of debuggers in file.
        debugger_match_list = subprocess.Popen("grep -n -P \"(?:breakpoint\(\)|set_trace\(\))\" " + file_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].split(b"\n")

        p_space_dict = {}
        p_tabs_dict = {}

        for p in p_space_list:
            if p:
                p_temp = p.strip().split(b":")
                p_space_dict[p_temp[0].decode()] = b":".join(p_temp[1:])

        for p in p_tabs_list:
            if p:
                p_temp = p.strip().split(b":")
                p_tabs_dict[p_temp[0].decode()] = b":".join(p_temp[1:])

        space_keys = [int(x) for x in list(p_space_dict.keys())]
        tabs_keys = [int(x) for x in list(p_tabs_dict.keys())]
        space_keys.sort()
        tabs_keys.sort()

        if space_keys and tabs_keys:
            print("\tmixed indentations!!!!")
            exit_status = 1

        if output:
            if tabs:
                for x in space_keys:
                    if x:
                        print(("\t" + str(x) + ":" + p_space_dict[str(x)].decode()))
                        exit_status = 1
            if spaces:
                for x in tabs_keys:
                    if x:
                        print(("\t" + str(x) + ":" + p_tabs_dict[str(x)].decode()))
                        exit_status = 1
            # Check if break point of set_trace has been applied.
            for debugger_line in debugger_match_list:
                if debugger_line:
                    # The debugger line is a byte text.
                    line_num_debugger_text_list = debugger_line.strip().split(b":")
                    print("\t" + line_num_debugger_text_list[0].decode() + ":" + line_num_debugger_text_list[1].decode().strip())
                    exit_status = 1

    print("\n\n")

if exit_status == 0:
    print("ALL GOOD\n")
else:
    print("CHECK THE ABOVE ERRORS\n")

sys.exit(exit_status)
