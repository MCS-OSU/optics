from env.env_local import *
from env.env_remote import *
from difflib import Differ


# verify that environments on local machine and ec2b are in sync
class SyncedEnvironments():
    def __init__(self, local_env, remote_env):
        self.local_env = local_env
        self.remote_env = remote_env
        
        #ASKJED which method for calling the function is efficient
        # self.func_dict ={ 
        #     'branch name':self.is_git_branch_same,
        #     'git commit hash' : self.is_git_commit_same,
        #     'pip list' : self.is_pip_list_same,
        #     'uncommited status' : self.no_uncommitted_changes_on_either_side}

    # prints (True) if 
    #    - git branch is the same
    #    - git commit is the same
    #    - pip list output is the same
    #    - learned model versions are the same
    #    - there are no files under git control that are currently being edited on either side
    #    -
    def isSynced(self):
        print("Checking if local and remote environments are in sync...")
        val_git_branch = self.is_git_branch_same()
        
        if val_git_branch is not True:
            print("git branch is different")
            return False
        
        val_git_commit = self.is_git_commit_same()
        if val_git_commit is not True:
            print("git commit is different")
            return False   
        
        val_pip_list = self.is_pip_list_same()
        if val_pip_list is not True:
            print("pip list is different")
            return False
        
        val_uncommitted_changes = self.no_uncommitted_changes_on_either_side()
        if val_uncommitted_changes is not True:
            print("There are some uncommitted changes on either side")
            return False
        
        print("Local and remote environments are in sync")
        return True
        

        # # call all the other methods and return True if they all return True
        # # or print out error message for the first one that prints (False)
        
    def is_git_branch_same(self):
        val_local = self.local_env.get_git_branchname()
        val_remote = self.remote_env.get_git_branchname()
        print("local git branch: ", self.val_local)
        print("remote git branch: ", self.val_remote)
        if val_local == val_remote:

            return True
        else:
            return False

    def is_git_commit_same(self):    

        val_local = self.local_env.get_git_commit()
        val_remote = self.remote_env.get_git_commit()
        print("local commit: ", val_local)
        print("remote commit: ", val_remote)
        if val_local == val_remote:
            return True
        else:
            return False
        
    def is_pip_list_same(self):
        val_local = self.local_env.get_pip_list()
        val_remote = self.remote_env.get_pip_list()

        #TODO the below code is could be written in utils
        # different_package_names = []
        # for i,j in zip(val_local.strip(), val_remote.strip()):
        #     differ = Differ()
        #     for line in differ.compare(i, j):
        #         different_package_names.append(line)
        # # print("PIP LIST LOCAL: ", val_local)
        # # print("PIP LIST REMOTE: ", val_remote)
        # print("DIFFERENT PACKAGE NAMES: ", different_package_names)
        
        if val_local == val_remote:
            return True
        else:
            return False

    def is_learned_model_versions_same(self):
        pass

    def no_uncommitted_changes_on_either_side(self):
        val_local = self.local_env.get_uncommitted_changes()
        val_remote = self.remote_env.get_uncommitted_changes()
        if val_local != "0" and val_remote != "0":
            return False
        else:
            return True


if __name__ == '__main__':
    local_env = EnvLocal()
    remote_env = EnvRemote()
    synced_env = SyncedEnvironments(local_env, remote_env)
    synced_env.isSynced()



# e = SyncedEnvironments(EnvLocal(), EnvRemote())
# e.isSynced()
# e.is_pip_list_same()
