import os
import time
from core.utils import remote_copy_file_quiet, remote_get_file_quiet, remote_delete_file, remote_mv_file
from remote_control.constants import TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR, REMOTE_ROOT


class Messenger():
    def __init__(self, name, position):
        self.name = name
        self.inbound_message_pathnames = []
        self.unanswered_control_messages = []
        self.message_dir_outbound = os.path.join(os.environ['OPTICS_HOME'], f'remote_control_{position}/{name}/messages/out')
        self.message_dir_inbound  = os.path.join(os.environ['OPTICS_HOME'], f'remote_control_{position}/{name}/messages/in')
        self.message_dir_log_out  = os.path.join(os.environ['OPTICS_HOME'], f'remote_control_{position}/{name}/messages/log_out')
        self.message_dir_log_in     = os.path.join(os.environ['OPTICS_HOME'], f'remote_control_{position}/{name}/messages/log_in')
        os.makedirs(self.message_dir_inbound, exist_ok=True)
        os.makedirs(self.message_dir_outbound, exist_ok=True)
        os.makedirs(self.message_dir_log_out, exist_ok=True)
        os.makedirs(self.message_dir_log_in, exist_ok=True)
        # clean the message slate on startup, except for log dirs
        os.system(f'rm -f {self.message_dir_inbound}/*')
        os.system(f'rm -f {self.message_dir_outbound}/*')
        self.scan_count = 0

    def archive_inbound_messages(self):
        for p in self.inbound_message_pathnames:
            os.system(f'mv {p} {self.message_dir_log_in}')
        self.inbound_message_pathnames = []

    def get_incoming_messages(self):
        return self.inbound_message_pathnames

    def has_incoming_messages(self):
        #print(f'found {len(self.inbound_message_pathnames)} messages for {self.name}')
        return bool(self.inbound_message_pathnames)

        
    def send_control_message(self, command_name, command):
        t = int(time.time())
        tmp_message_path= self.create_message_file(t, command_name, command)
        target_path = os.path.join(REMOTE_ROOT, self.name, TO_USER_REMOTE_DIR)
        remote_copy_file_quiet(tmp_message_path, target_path)
        print(f'(sent file)')
        message_fname = os.path.basename(tmp_message_path)
        self.note_unanswered_control_message(message_fname)
        os.system(f'mv {tmp_message_path} {self.message_dir_log_out}')


    def send_response_message(self, client_command):
        message = '\n'.join(client_command.info_lines)
        print(f'sending message {message}')
        tmp_message_path = self.create_message_file(client_command.timestamp, client_command.command_name, message)
        target_path = os.path.join(REMOTE_ROOT, self.name, FROM_USER_REMOTE_DIR)
        remote_copy_file_quiet(tmp_message_path, target_path)
        print(f'(sent response)')
        os.system(f'mv {tmp_message_path} {self.message_dir_log_out}')
       
    def create_message_file(self, t, message_type, message):
        message_fname = f'{t}_{self.name}_{message_type}.txt'
        message_path = f'{self.message_dir_outbound}/{message_fname}'
        f = open(message_path, 'w')
        f.write(message + '\n')
        f.close()
        return message_path 

    def note_unanswered_control_message(self, message_fname):
        print(f'noting unanswered message for {self.name}: {message_fname}')
        self.unanswered_control_messages.append(message_fname)

    def scan_for_inbound_commands(self):
        self.scan_for_incoming_messages(TO_USER_REMOTE_DIR)

    def scan_for_incoming_messages(self, remote_dir):
        if self.scan_count < 100:
            print('.', end='', flush=True)
            self.scan_count += 1
        else:
            print()
            self.scan_count = 0
        remote_src = os.path.join(REMOTE_ROOT, self.name, remote_dir + '/*')
        remote_get_file_quiet(remote_src, self.message_dir_inbound)
        os.system(f'ls {self.message_dir_inbound}')
        if len(os.listdir(self.message_dir_inbound)) > 0:
            print(f'received:')
            self.load_incoming_messages()
            self.reconcile_messages()
            remote_path = os.path.join(REMOTE_ROOT, self.name, remote_dir)
            remote_delete_file(remote_path + '/*')
            self.scan_count = 0
                


    def reconcile_messages(self):
        if len(self.unanswered_control_messages) != 0:
            timestamps = self.get_timestamps_of_inbound_message_pathnames()
            matching_responses = []
            for message_fname in self.unanswered_control_messages:
                unanswered_timestamp = message_fname.split('_')[0]
                if unanswered_timestamp in timestamps:
                    matching_responses.append(message_fname)
            for message_fname in matching_responses:
                #print(f'removing unanswered_control_message {message_fname}')
                self.unanswered_control_messages.remove(message_fname)

    def load_incoming_messages(self):
        #print(f'checking dir {self.message_dir_inbound}')
        files = os.listdir(self.message_dir_inbound)
        if len(files) > 0:
            for fname in files:
                self.inbound_message_pathnames.append(os.path.join(self.message_dir_inbound,fname))
        else:
            print(f'no messages found for {self.name}')

    def get_timestamps_of_inbound_message_pathnames(self):
        timestamps = []
        for message_fname in self.inbound_message_pathnames:
            timestamp = message_fname.split('_')[0]
            timestamps.append(timestamp)
        return timestamps


    def print_responses(self):
        for message_pathname in self.inbound_message_pathnames:
            print(f'repsonse - {self.name}: {message_pathname}')
            f = open(message_pathname, 'r')
            for line in f.readlines():
                print(f'   {line.strip()}')
           