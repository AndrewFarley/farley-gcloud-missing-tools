#!/usr/bin/env python
#
###############################################################################
#
#    gcloud-choose-project.py    Written by Farley <farley@neonsurge.com>
#
# This script helps you easily choose which project you wish to be working with
# based on available gcloud projects.
#
###############################################################################

# Global includes
from subprocess import Popen, PIPE
import shlex
import sys

# Helper to run subshell command and capture output/stderr/exitcode easily
def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    
    return exitcode, out, err

# Simple int checker
def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

# Python-fu is weak, should be able to one-line this
def contains_value(array, string):
    for item in array:
        try:
            if string == item['project_id']:
                return True
        except:
            pass
    return False

def max_element_length(array, element):
    maxlen = 0
    for item in array:
        if len(item[element]) > maxlen:
            maxlen = len(item[element])
    return maxlen

# Get our list of GCloud projects
def get_project_list():
    exitcode, out, err = get_exitcode_stdout_stderr('gcloud projects list')
    if exitcode != 0:
        print("Error while trying to run 'gcloud projects list'")
        print(err)
        exit(1)

    projects_list = []
    for item in out.split("\n"):
        try:
            cleaned_split_string = item.split(' ')
            project = {}
            project['project_id']     = cleaned_split_string.pop(0)
            project['project_number'] = cleaned_split_string.pop()
            if not is_int(project['project_number']):  # Skipping non-int project number
                continue
            project['project_name'] = ' '.join(cleaned_split_string).strip()
            projects_list.append(project)
        except:
            pass

    return projects_list

# Get our current project
def get_current_project():
    exitcode, out, err = get_exitcode_stdout_stderr("gcloud config list --format 'value(core.project)'")
    if exitcode != 0:
        return False
    return out.strip()

# Set our current project
def set_current_project(project_id):
    exitcode, out, err = get_exitcode_stdout_stderr("gcloud config set project {}".format(project_id))
    if exitcode != 0:
        print("Error while setting project")
        print(err)
        exit(1)

# Get the projects list
projects_list = get_project_list()

# Check for CLI args (used to set the project without prompting for the project)
if len(sys.argv) >= 2:
    project = sys.argv.pop(1)
    if not contains_value(projects_list, project):
        print("Error: {} is not a valid project".format(project))
    else:
        print("Selecting project: {}".format(project))
        set_current_project(project)
        exit(0)

# Sort alphabetically
projects_list = sorted(projects_list, key=lambda k: k['project_id'])
# Get our current project
current_project = get_current_project()

# Print projects available list
print("{} maxlen".format(max_element_length(projects_list, 'project_id')))

print("================================================================================")
print(" Projects available")
print("================================================================================")
count = 1
for project in projects_list:
    print("{}. {}{} {} {}".format(
        count, 
        "*" if current_project == project['project_id'] else " ", 
        project['project_id'].ljust( max_element_length(projects_list, 'project_id') + 1),
        project['project_number'].ljust( max_element_length(projects_list, 'project_number') + 1),
        project['project_name']
    ))
    count = count + 1
print("================================================================================")
count = count - 1

# Ask the user to choose a profile infinitely
while True:
    var = raw_input("Choose a project number: [1-" + str(count) + "]: ")

    if is_int(var) and int(var) > 0 and int(var) <= count:
        break;
    else:
        print("Invalid input")
var = str(int(var) - 1)

# Set this project
project = projects_list.pop(int(var))
print("Selecting project: {}".format(project['project_id']))
set_current_project(project['project_id'])

exit(0)