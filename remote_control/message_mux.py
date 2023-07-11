import time
import os
from core.utils import remote_copy_file_quiet, remote_get_file_quiet, remote_copy_file, remote_get_file
from remote_control.constants import TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR
from remote_control.messenger import Messenger

class MessageMux():
    def __init__(self, users):
        self.users = users
        self.messengers = {}
        for user in self.users:
            self.messengers[user] = Messenger(user)
      

    def send_control_message(self, user, message):
        print(f'sending {message} to {user}')
        if not user in self.users:
            raise Exception(f'invalid user: {user}')
        self.messengers[user].send_control_message(message)
        
    def has_incoming_messages(self):
        print(f'checking if have messages that were received...')
        for user in self.users:
            if self.messengers[user].has_incoming_messages():
                return True
        return False

    def scan_for_user_responses(self):
        print(f'scanning for responses from users...')
        for user in self.users:
            self.messengers[user].scan_for_incoming_messages(FROM_USER_REMOTE_DIR)

    def print_responses(self):
        for user in self.users:
            self.messengers[user].print_responses()
        
