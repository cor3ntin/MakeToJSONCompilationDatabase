#!/usr/bin/python
# Most clang tools require a "compile_command.json" file, 
# which contains the list of clang invocation commands
# needed to build the various sources file of an project.
# You can learn more about the clang "compilation database here
# http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# Sadly, only CMake knows how to generate such file.
# this python script generate it from a regular Makefile
#
# The script works by replacing CC and CXX in the make invocation by 
# itself and write its command line to "compile_commands.json"
#
#
# Usage
# ==========================
# just invoke it from the path
# where you would usually run "make"
#
# Tested with python 27 et 3 on Linux

import os, json, sys, shlex
from subprocess import call

COMPILEDB_FILENAME = "compile_commands.json"
root_directory = directory =  os.getcwd()

if len(sys.argv) == 1:
    print(os.path.abspath(sys.argv[0]))
    compile_commands_file = os.path.join(root_directory, COMPILEDB_FILENAME)
    with open(compile_commands_file, "w") as f:
        f.write("[\n")
    call(["make", 
        "-B", #make all targets
        "-i", "-k", #ignore errors
        "CXX="+os.path.abspath(sys.argv[0]), #use our phoony compiler"
        "CC="+os.path.abspath(sys.argv[0])
        ])
    #remove trailing ',' and close the json list
    file_size = os.path.getsize(compile_commands_file)
    with open(compile_commands_file, "r+") as f:
        i = 1
        while i < 10:
            f.seek(file_size - i, 0)
            if f.read(1) == ",": 
                f.seek(file_size - i)
                f.write("\n]\n")
                break;
            i+=1
    exit(0)

while root_directory != '/' and not os.path.exists(os.path.join(root_directory, COMPILEDB_FILENAME)):
    root_directory = os.path.dirname(root_directory)
if directory == '/':
    print("no compilation_comands.json")
    exit(1)
directory = os.path.relpath(directory, root_directory)

args = sys.argv[1:]

found = False
for arg in args[1:]:
    for ext in [".cpp"]:
        if arg.endswith(ext):
            compilation_unit = arg
            found = True
            break
    if found:break

if not found:
    print("no compilation unit")
    exit(1)

#Special handling of moc files for Qt, for which this script
#was first intented
if os.path.basename(compilation_unit).startswith("moc_"):
    exit(0)

args.insert(0, "clang")

with open(os.path.join(root_directory, COMPILEDB_FILENAME), "a") as f:
    f.write(json.dumps({ 
        "directory": directory, 
        "command": " ".join(args), #TODO: better quotes handling
        "file": compilation_unit
        }))
    f.write(",\n")
