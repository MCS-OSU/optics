import os
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
        