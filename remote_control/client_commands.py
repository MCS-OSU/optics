
import os

from remote_control.constants import PING, SHOW_CLIENT_LOG, CONTAINER_GET, CONTAINER_RUN, CONTAINER_STOP
from remote_control.constants import CONTAINER_RUN_TEST, CONTAINER_STOP_TEST, CONTAINER_LIST, CONTAINER_DELETE
from remote_control.client_command import PingCommand, ShowLogCommand, GetContainerCommand, RunContainerCommand, StopContainerCommand
from remote_control.client_command import TestRunContainerCommand, TestStopContainerCommand, ListContainerCommand, DeleteContainerCommand

class ClientCommands():
    def __init__(self, messenger):
        self.commands = []
        for p in messenger.inbound_message_pathnames:
            fname = os.path.basename(p)
            timestamp, _, command_name = fname.split('.')[0].split('_')
            f = open(p, 'r')
            lines = f.readlines()
            f.close()
            full_command = lines[0].strip()
            print(f'\n<- {timestamp} {full_command}')
            if command_name == PING:
                self.commands.append(PingCommand(p))
            elif command_name == CONTAINER_GET:
                self.commands.append(GetContainerCommand(p))
            elif command_name == CONTAINER_RUN:
                self.commands.append(RunContainerCommand(p))
            elif command_name == CONTAINER_STOP:
                self.commands.append(StopContainerCommand(p))
            elif command_name == CONTAINER_RUN_TEST:
                self.commands.append(TestRunContainerCommand(p))
            elif command_name == CONTAINER_STOP_TEST:
                self.commands.append(TestStopContainerCommand(p))
            elif command_name == CONTAINER_LIST:
                self.commands.append(ListContainerCommand(p))
            elif command_name == CONTAINER_DELETE:
                self.commands.append(DeleteContainerCommand(p))
            elif command_name == SHOW_CLIENT_LOG:
                self.commands.append(ShowLogCommand(p))
            else:
                raise Exception(f'unknown command: {command_name}')
        messenger.archive_inbound_messages()
