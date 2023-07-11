import os
from remote_control.constants import TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR, REMOTE_ROOT
from core.utils import remote_copy_file_quiet, remote_get_file_quiet, remote_copy_file, remote_get_file

class RemoteClientMessenger():
    def __init__(self, name):
        self.name = name
        self.remote_message_dir_from_user = os.path.join(REMOTE_ROOT, name, FROM_USER_REMOTE_DIR)
        self.remote_message_dir_to_user = os.path.join(REMOTE_ROOT, name, TO_USER_REMOTE_DIR)
        self.message_dir_outbound = os.path.join(os.environ['OPTICS_HOME'], f'remote_control/{name}/messages/out')
        self.message_dir_inbound = os.path.join(os.environ['OPTICS_HOME'], f'remote_control/{name}/messages/in')
        os.makedirs(self.message_dir_outbound, exist_ok=True)
        os.makedirs(self.message_dir_inbound, exist_ok=True)

    def has_received_command(self):
        pass

    def scan_for_commands(self):
        print(f'...scanning for commands for {self.name}')
        remote_src = os.path.join(self.remote_root, {self.name}, TO_USER_REMOTE_DIR + '/*')
        remote_get_file(remote_src, self.message_dir_inbound)
        print(f'after remote_get_file, ls of {self.message_dir_inbound}')
        os.system(f'ls {self.message_dir_inbound}')
        self.load_messages(user, user_inbound_dir)
        os.system(f'rm {user_inbound_dir}/*')
        self.reconcile_messages(user)

    def send_response(self, fname):
        pass

    def get_commands(self):
        pass
    