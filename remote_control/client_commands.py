
import os

from remote_control.constants import PING, CONTAINER_GET, CONTAINER_RUN, CONTAINER_STOP, CONTAINER_RUN_TEST, CONTAINER_STOP_TEST
from remote_control.client_command import PingCommand, GetContainerCommand, RunContainerCommand, StopContainerCommand
from remote_control.client_command import TestRunContainerCommand, TestStopContainerCommand

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
            elif command_name == CONTAINER_RUN:
                print(f'found run command')
                self.commands.append(RunContainerCommand(p))
            elif command_name == CONTAINER_STOP:
                print(f'found stop command')
                self.commands.append(StopContainerCommand(p))
            elif command_name == CONTAINER_RUN_TEST:
                print(f'found run test command')
                self.commands.append(TestRunContainerCommand(p))
            elif command_name == CONTAINER_STOP_TEST:
                print(f'found run test command')
                self.commands.append(TestStopContainerCommand(p))
            else:
                raise Exception(f'unknown command: {command_name}')
        messenger.archive_inbound_messages()
