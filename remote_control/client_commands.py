
import os

from remote_control.constants import PING, CONTAINER_GET
from remote_control.client_command import PingCommand, GetContainerCommand

class ClientCommands():
    def __init__(self, messenger):
        self.commands = []
        for p in messenger.inbound_message_pathnames:
            fname = os.path.basename(p)
            _, _, command_name = fname.split('.')[0].split('_')
            if command_name == PING:
                print(f'found ping command')
                self.commands.append(PingCommand(p))
            elif command_name == CONTAINER_GET:
                print(f'found get command')
                self.commands.append(GetContainerCommand(p))
            else:
                raise Exception(f'unknown command: {command_name}')
        messenger.archive_inbound_messages()
