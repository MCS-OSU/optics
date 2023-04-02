import os


def get_running_optics_processes(run_name):
    processes = []
    cmd = f'ps -ef | grep {run_name} | grep -v grep > tmp_ps.txt'
    os.system(cmd)
    with open('tmp_ps.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'optics_run_scene.py' in line:
                processes.append(OpticsProcess(line))
            elif 'container_run' in line:
                processes.append(OpticsProcess(line))
    os.system('rm tmp_ps.txt')
    return processes


class OpticsProcess():
    def __init__(self, line):
        parts = line.split()
        self.pid = parts[1]

    def stop(self):
        cmd = f'kill -9 {self.pid}'
        os.system(cmd)