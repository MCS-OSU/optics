import sys
from env.env_local import EnvLocal


class EnvSnapshot():
    def __init__(self, spec_path):
        self.spec_path = spec_path
        self.env_local = EnvLocal()
        uncommitted_changes = self.env_local.get_uncommitted_changes()
        count = len(uncommitted_changes)
        
        if count > 0:
            print('\n')
            print(f"    *** There are {count} uncommitted changes in the local environment ***")
            print('')
            print("     Please commit or discard changes before taking a snapshot")
            print('')
            for i in range(count):
                print('      ' + uncommitted_changes[i])
            print('')
            print('')
            sys.exit()

        print("[optics]...verified that there are no uncommitted changes in the local environment")

        # collect current most recent commit hash


        # collect branch name


        # gather pip list output

        # gather learned model versions

        # show user and ask if want to save it.

    def save_snapshot_file(self):
        pass

    def git_add_snapshot_file(self):
        pass

    def git_commit_snapshot_file(self):
        pass

    