import os
import subprocess
from remote_control.utils import remote_get_container_quiet, get_remote_container_path, get_local_container_dir

class ClientCommand():
    def __init__(self, cmd_path):
        fname = os.path.basename(cmd_path)
        print(f' ...found command file {fname} in ctor !')
        self.timestamp, _, self.command_name = fname.split('.')[0].split('_')
        self.command_path = cmd_path
        f = open(self.command_path, 'r')
        self.info_lines = f.readlines()
        f.close()
        #os.system(f'rm {self.command_path}')

    def add_response_string(self, response_string):
        self.info_lines.append(response_string)

    def add_response_lines(self, response_lines):
        self.info_lines.extend(response_lines)

        


class PingCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        self.add_response_string('pong')


class GetContainerCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        command_line = self.info_lines[0].strip()
        container = command_line.split(' ')[1]
        remote_path = get_remote_container_path(container)
        local_containers_dir = get_local_container_dir()
        os.makedirs(local_containers_dir, exist_ok=True)
        remote_get_container_quiet(remote_path, local_containers_dir)
        local_container_path = os.path.join(local_containers_dir, container)
        if not os.path.exists(local_container_path):
            self.add_response_string(f'{command_line} failed')
        else:
            self.add_response_string(f'{command_line} succeeded')
        #self.add_response_string('get')
        


class TestRunContainerCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        command_line = self.info_lines[0].strip()
        delay = command_line.split(' ')[1]
        count = command_line.split(' ')[2]
        cmd = "python timer_for_testing_launch_and_stop.py " + delay + " " + count + "&"
        os.system(cmd)
        self.add_response_string(f'launched : timer_for_testing_launch_and_stop')
        


class TestStopContainerCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        cmd = 'ps -edalf | grep "python timer_for_testing_launch" > temp.txt'
        print(f'cmd is {cmd}')
        os.system(cmd)
        f = open('temp.txt', 'r')
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            self.add_response_string(f'no timer_for_testing_launch_and_stop found')
            return
        result = ' '.join(lines[0].split())
        pid = result.split(' ')[3]
        cmd = f'kill -9 {pid}'
        print(f'kill cmd is {cmd}')
        os.system(cmd)
        self.add_response_string(f'killed : timer_for_testing_launch_and_stop')

class RunContainerCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        command_line = self.info_lines[0].strip()
        container_name = command_line.split(' ')[1].replace('.sif','')
        container_path = self.get_local_container_path(container_name)
        if 'not_found' == container_path:
            self.add_response_string(f'container {container_name} not found')
            return
        if 'inter' in container_name:
            cmd = f'apptainer run --nv {container_path} optics scene_type_provided &'
        else:
            cmd = f'apptainer run --nv {container_path} optics &'
        os.system(cmd)
        self.add_response_string(f'launched with: {cmd}')

    def get_local_container_path(self, container_name):
        if os.path.exists(get_local_container_dir() + '/' + container_name + '.sif'):
            return get_local_container_dir() + '/' + container_name + '.sif'
        if os.path.exists('/home/jedirv/main_optics/apptainer/sifs/{container_name}.sif'):
            return '/home/jedirv/main_optics/apptainer/sifs/{container_name}.sif'
        if os.path.exists('/home/jedirv/dev_optics/apptainer/sifs/{container_name}.sif'):
            return '/home/jedirv/dev_optics/apptainer/sifs/{container_name}.sif'
        else:
            return 'not_found'



class StopContainerCommand(ClientCommand):
    def __init__(self, command_path):
        super().__init__(command_path)
        
    def execute(self):
        command_line = self.info_lines[0].strip()
        container = command_line.split(' ')[1].replace('.sif','')
        
        cmd = f'ps -edalf | grep {container} | grep -v grep > temp.txt'
        print(f'running this command to search for container: {cmd}')
        os.system(cmd)
        f = open('temp.txt', 'r')
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            self.add_response_string(f'container {container} not found in process list')
            return
        pids = []
        for line in lines:
            result = ' '.join(line.split())
            pid = result.split(' ')[3]
            pids.append(pid)
            #cmd = f'kill -9 {pid}'
        unity_search_command = f'ps -edalf | grep MCS-AI2-THOR-Unity | grep -v grep > temp.txt'
        os.system(unity_search_command)
        f = open('temp.txt', 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            result = ' '.join(line.split())
            pid = result.split(' ')[3]
            pids.append(pid)
        kill_cmd = 'kill -9 ' + ' '.join(pids)
        print(f'kill cmd is {kill_cmd}')
        os.system(kill_cmd)
        self.add_response_string(f'killed containe process for {container}')