import sys, os

class PipListComparer():
    def __init__(self):
        pass

    def compare(self, proj):
        print('############################################################')
        print(f'....comparing pip lists for {proj}...')
        print('')
        optics_home = os.environ['OPTICS_HOME']
        if not os.path.exists(optics_home):
            print(f'ERROR - OPTICS_HOME {optics_home} does not exist')
            sys.exit()

        proj = sys.argv[1]
        env_dir = os.path.join(optics_home, 'env')
        fname = f'pip_list_eval6_{proj}.txt'
        pip_list_path = os.path.join(env_dir, fname)
        reference_pip_list = PipList(pip_list_path)

        env_list_fname = 'tmp_pip_list_in_play.txt'
        cmd = f"pip list > {env_list_fname}"
        os.system(cmd)
        pip_list_in_play = PipList(env_list_fname)

        if not reference_pip_list.same_count(pip_list_in_play):
            print('    different package count')

        missing_from_in_play = reference_pip_list.packages_missing(pip_list_in_play)
        missing_from_reference = pip_list_in_play.packages_missing(reference_pip_list)

        

        diff_versions_from_reference = reference_pip_list.diff_versions(pip_list_in_play)

        if len(missing_from_in_play) == 0 and len(missing_from_reference) == 0 and len(diff_versions_from_reference) == 0:
            print('    pip lists identical')
        
        else:
            if len(missing_from_in_play) > 0:
                print('\n\n    packages present in the reference image that are not in the current env')
                for package in missing_from_in_play:
                    print(f'    {package} {reference_pip_list.version_per_package[package]}')

            if len(missing_from_reference) > 0:
                print('\n\n    packages present in the current env that are not in the reference image')
                for package in missing_from_reference:
                    print(f'    {package} {pip_list_in_play.version_per_package[package]}')

            if len(diff_versions_from_reference) > 0:
                print('\n\n    version differences:')
                for package in diff_versions_from_reference:
                    reference_version = reference_pip_list.version_per_package[package]
                    in_play_version = pip_list_in_play.version_per_package[package]
                    print(f'    {package} reference versions: {reference_version.ljust(10)} in play version: {in_play_version}')

        print('\n\n############################################################')

class PipList():
    def __init__(self, pip_list_path):
        self.packages = []
        self.version_per_package = {}
        f = open(pip_list_path, 'r')
        self.lines = f.readlines()
        f.close()
        for line in self.lines:
            if line.startswith('Package'):
                pass
            elif line.startswith('-------'):
                pass
            else:
                parts = line.split(' ')
                package = parts[0]
                version = parts[-1].rstrip()
                self.packages.append(package)
                self.version_per_package[package] = version
                #print(f'p={package};v={version}')

    def same_count(self, other_pip_list):
        if len(self.packages) == len(other_pip_list.packages):
            return True 
        return False

    def packages_missing(self, other_pip_list):
        missing = []
        for package in self.packages:
            if package not in other_pip_list.packages:
                missing.append(package)
        return missing

    def diff_versions(self, other_pip_list):
        diff = []
        for package in self.packages:
            if package in ['Markdown', 'opics-inter','opics_pvoe']:
                continue
            if package in other_pip_list.packages:
                if self.version_per_package[package] != other_pip_list.version_per_package[package]:
                    diff.append(package)
        return diff

