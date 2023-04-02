import os
from remote_control.constants import TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR, REMOTE_ROOT

class RemoteClientMessenger():
    def __init__(self, name):
        self.name = name
        self.remote_message_dir_from_user = os.path.join(REMOTE_ROOT, name, FROM_USER_REMOTE_DIR)
        self.remote_message_dir_to_user = os.path.join(REMOTE_ROOT, name, TO_USER_REMOTE_DIR)
        self.local_messages_dir = f'messages_{name}'
        os.makedirs(self.local_messages_dir, exist_ok=True)

    def has_received_command(self):
        pass

    def scan_for_commands(self):
        pass

    def send_response(self, fname):
        pass