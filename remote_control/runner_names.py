import os

class RunnerNames():
    def __init__(self):
        self.names = []
        opics_home = os.environ['OPICS_HOME']
        self.runner_names_file = os.path.join(opics_home, 'remote_control/runner_names.txt')
        f = open(self.runner_names_file, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            self.names.append(line.strip())
        f.close()
        self.names.sort()
        
