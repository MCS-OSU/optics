import time
import os
from core.utils import remote_copy_file_quiet, remote_get_file_quiet, remote_copy_file, remote_get_file
from remote_control.constants import TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR

class MessageMux():
    def __init__(self, users, remote_root):
        self.users = users
        self.remote_root = remote_root
        self.users_with_pending_responses = []
        self.unanswered_messages = {}
        self.message_dir_outbound = os.path.join(os.environ['OPTICS_HOME'], 'remote_control/messages/out')
        self.message_dir_inbound = os.path.join(os.environ['OPTICS_HOME'], 'remote_control/messages/in')
        os.makedirs(self.message_dir_outbound, exist_ok=True)
        os.makedirs(self.message_dir_inbound, exist_ok=True)
        self.messages_received = {}

    def create_and_send_message(self, user, message):
        print(f'sending message to {user}: {message}')
        t = int(time.time())
        user_out_dir = os.path.join(self.message_dir_outbound, user)
        os.makedirs(user_out_dir, exist_ok=True)
        (message_fname , tmp_message_path) = self.create_message_file(t, message, user, 'syscmd')
        self.send_message(tmp_message_path, user)
        self.note_unanswered_message(user, message_fname)

    def create_message_file(self, t, message, user, message_type):
        message_fname = f'{t}_{user}_{message_type}.txt'
        message_path = f'{self.message_dir_outbound}/{user}/{message_fname}'
        f = open(message_path, 'w')
        f.write(message + '\n')
        f.close()
        return ( message_fname, message_path )

    def send_message(self, message_path, user):
        # send to /home/ubuntu/optics_remote_control/<user>/messages_for_user
        target_path = os.path.join(self.remote_root, user, 'messages_to_user')
        remote_copy_file(message_path, target_path)
        print(f'(sent file)')
        if not user in self.users_with_pending_responses:
            self.users_with_pending_responses.append(user)

    def note_unanswered_message(self, user, message_fname):
        print(f'noting unanswered message for {user}: {message_fname}')
        if user in self.unanswered_messages:
            self.unanswered_messages[user].append(message_fname)
        else:
            self.unanswered_messages[user] = [message_fname]

    def scan_for_responses(self):
        print('scanning starts')
        if len(self.users_with_pending_responses) == 0:
            return
        for user in self.users_with_pending_responses:
            print(f'...scanning for responses from {user}')
            remote_src = os.path.join(self.remote_root, user, 'messages_from_user/*')
            user_inbound_dir = os.path.join(self.message_dir_inbound, user)
            os.makedirs(user_inbound_dir, exist_ok=True)
            remote_get_file(remote_src, user_inbound_dir)
            print(f'after remote_get_file, ls of {user_inbound_dir}')
            os.system(f'ls {user_inbound_dir}')
            self.load_messages(user, user_inbound_dir)
            os.system(f'rm {user_inbound_dir}/*')
            self.reconcile_messages(user)

    def load_messages(self, user, user_inbound_dir):
        print(f'checking dir {user_inbound_dir}')
        files = os.listdir(user_inbound_dir)
        print(f'files: {files}')
        if len(files) > 0:
            for fname in files:
                print(f'found response for {user}: {fname}')
                f = open(os.path.join(user_inbound_dir, fname), 'r')
                lines = f.readlines()
                f.close()
                if not user in self.messages_received:
                    self.messages_received[user] = {}
                print('loading this message from file:')
                for line in lines:
                    print(line.strip())
                self.messages_received[user][fname] = lines
        else:
            print(f'no messages found for {user}')
        
    def reconcile_messages(self, user):
        if user in self.unanswered_messages:
            if len(self.unanswered_messages[user]) != 0:
                timestamps = self.get_timestamps_of_messages_received(user)
                matching_responses = []
                for message_fname in self.unanswered_messages[user]:
                    unanswered_timestamp = message_fname.split('_')[0]
                    if unanswered_timestamp in timestamps:
                        matching_responses.append(message_fname)
                for message_fname in matching_responses:
                    self.unanswered_messages[user].remove(message_fname)
                    if len(self.unanswered_messages[user]) == 0:
                        self.users_with_pending_responses.remove(user)

    def has_responses(self):
        print('in has_responses')
        for user in self.users:
            print(f'checking for responses from {user}...')
            if user in self.messages_received:
                print(f'found {len(self.messages_received[user])} messages for {user}')
                if bool(self.messages_received[user]):
                    return True
        return False

    def get_timestamps_of_messages_received(self, user):
        timestamps = []
        if user in self.messages_received:
            for message_fname in self.messages_received[user]:
                timestamp = message_fname.split('_')[0]
                timestamps.append(timestamp)
        return timestamps

    def print_responses(self):
        for user in self.messages_received:
            for message_fname in self.messages_received[user]:
                print(f'{user}: {message_fname}')
                for line in self.messages_received[user][message_fname]:
                    print(f'   {line.strip()}')