import os

class RunnerNames():
    def __init__(self):
        self.names = []
        optics_home = os.environ['OPTICS_HOME']
        self.runner_names_file = os.path.join(optics_home, 'remote_control/runner_names.txt')
        f = open(self.runner_names_file, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            self.names.append(line.strip())
        f.close()
        self.names.sort()
        
