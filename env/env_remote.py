import core.utils as utils

# use remoite utility functions in the utils.py file (or add some if needed) to 
# find the info in play on ec2b, under the ~/eval6 dir
class EnvRemote():
    def __init__(self):
        self.cmd_dict ={ 
            'branchname':'git rev-parse --abbrev-ref HEAD',
            'gitcommithash' : 'git log --format="%H" -n 1',
            'lib_list' : 'pip list',
            'uncommitedstatus' : 'git status --porcelain | wc -l' }

    def get_git_branchname(self):
        utils.ensure_dir_exists('sync_branch.txt')
        utils.remote_run_os_command_and_return_results('/home/ubuntu/eval6/scripts/ec2',self.cmd_dict["branchname"],'sync_branch.txt')
        val_branchname = utils.get_last_line('sync_branch.txt')
        return val_branchname
        
    def get_git_commit(self):
        utils.ensure_dir_exists('sync_commit.txt')
        utils.remote_run_os_command_and_return_results('/home/ubuntu/eval6/scripts/ec2',self.cmd_dict["gitcommithash"],'sync_commit.txt')
        val_commit = utils.get_last_line('sync_commit.txt')
        return val_commit

    def get_pip_list(self):
        utils.ensure_dir_exists('sync_pip.txt')
        utils.remote_run_os_command_and_return_results('/home/ubuntu/eval6/scripts/ec2',self.cmd_dict["lib_list"],'sync_pip_list.txt')
        val_pip_list = utils.read_file('sync_pip_list.txt')
        return val_pip_list

    def get_learned_model_versions(self):
        pass

    def get_uncommitted_changes(self):
        utils.remote_run_os_command_and_return_results('/home/ubuntu/eval6/scripts/ec2',self.cmd_dict["uncommitedstatus"],'sync_uncommited.txt')
        val_uncommited = utils.read_file('sync_uncommited.txt')
        return val_uncommited


# e = EnvRemote()
# print(e.get_git_branchname())
# e.get_git_commit()
# e.get_pip_list()
# e.get_uncommitted_changes()