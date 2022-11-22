
import os
import subprocess

class EnvLocal():
    
    def __init__(self):
        self.cmd_dict ={ 
            'branchname':'git rev-parse --abbrev-ref HEAD',
            'gitcommithash' : 'git log --format="%H" -n 1',
            'lib_list' : 'pip list',
            #'uncommitedstatus' : 'git status --porcelain | wc -l' }
            'uncommitedstatus' : 'git status --porcelain' }

    def get_git_branchname(self):
        # cmd = 'git branch'
        branch_loc = subprocess.check_output(self.cmd_dict["branchname"].split())
        branch_loc = branch_loc.decode("utf-8").rstrip()
        return branch_loc

    def get_git_commit(self):
        # cmd = 'git log --format="%H" -n 1'
        commit_name_loc = subprocess.check_output(self.cmd_dict["gitcommithash"].split())
        commit_name_loc = commit_name_loc.decode("utf-8").rstrip()
        return commit_name_loc

    def get_pip_list(self):
        # cmd = 'pip list'
        pip_list_loc = subprocess.check_output(self.cmd_dict["lib_list"].split())
        pip_list_loc= pip_list_loc.decode("utf-8")
        return pip_list_loc
    def get_learned_model_versions(self):
        pass

    def get_uncommitted_changes(self):
        # cmd = 'git status --porcelain'
        loc_commit_stat = subprocess.check_output(self.cmd_dict["uncommitedstatus"].split())
        loc_commit_stat = loc_commit_stat.decode("utf-8").rstrip()
        lines = loc_commit_stat.splitlines()
        mod_lines = []
        for line in lines:
            if line.lstrip().startswith('M'):
                mod_lines.append(line)
        return mod_lines

# e = EnvLocal()
# print (e.get_git_branchname())
# print(e.get_git_commit())
# print(e.get_pip_list())
# print(e.get_uncommitted_changes())
