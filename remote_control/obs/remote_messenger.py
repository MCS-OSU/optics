import time
import os
from core.utils import remote_copy_file_quiet, remote_get_file_quiet


class Obsolete_RemoteMessenger():
    def __init__(self, name):
        self.name = name
        self.remote_message_dir = f'/home/ubuntu/optics_remote_control/{name}/messages'
        self.messages_dir = f'messages_{name}'
        os.makedirs(self.messages_dir, exist_ok=True)


    def send_control_command(self, cmd, window):
        cmd = cmd.lower()
        #window[f'status_{self.name}'].update(f'{cmd} {self.name}')
        if cmd == 'stop':
            self.stop_run(window)
        elif cmd == 'run':
            self.start_run(window)
        elif cmd == 'load':
            self.load_run(window)
        elif cmd == 'clean':
            self.clean_run(window)
        else:
            print(f'Unknown command: {cmd}')

    def log_message_sent(self, message):
        print(f'Sent message: {message}...')

    def log_message_received(self, message):
        pass

    def create_message_file(self, t, message, message_type):
        fname = f'{t}_{self.name}_{message_type}.txt'
        f = open(fname, 'w')
        f.write(message)
        f.close()
        return fname

    def send_message(self, message_path):
        remote_copy_file_quiet(message_path, self.remote_message_dir)

    def get_response_file_with_time_prefix(self, t):
        response_fname = f'{t}_{self.name}_response.txt'
        remote_src = os.path.join(self.remote_message_dir, response_fname)
        local_dest = os.path.join(os.getcwd(), response_fname)
        if remote_get_file_quiet(remote_src, local_dest):
            if os.path.exists(response_fname):
                return response_fname
        return None

    def await_control_commands(self, window, key):
        count = 1
        while True:
            window[key].update(f'waiting for control command... {str(count)}')
            files = os.listdir(self.messages_dir)
            if len(files) > 0:
                for fname in files:
                    # each file has a time prefix, we need to respond with same prefix
                    t = fname.split('_')[0]
                    path = os.path.join(self.messages_dir, fname)
                    f = open(path, 'r')
                    lines = f.readlines()
                    for line in lines:
                        
            else:
                time.sleep(2)
                count += 1

    def send_message_and_wait_for_response(self, message, message_type, status_message, window):
        t = int(time.time())
        message_path = self.create_message_file(t, message, message_type)
        self.send_message(message_path)
        self.log_message_sent(message)
        count = 1
        while True:
            window[f'{message}_status_{self.name}'].update(f'{status_message} {self.name}... {str(count)}')
            response_path = self.get_response_file_with_time_prefix(t)
            if response_path is not None:
                response = self.read_response(response_path)
                self.log_message_received(response)
                break
            count += 1
            time.sleep(1)

    def stop_run(self, window):
        count = 0
        while count < 8 :
            time.sleep(1)
            self.send_message_and_wait_for_response('stop', 'control', 'stopping', window)
            #element = window[f'status_{self.name}']
            #window[f'stop_status_{self.name}'].update(f'{str(count)}...')
            count += 1
        window[f'stop_status_{self.name}'].update(f'{self.name} stopped')

    def start_run(self, window):
        
        count = 0
        while count < 8 :
            time.sleep(1)
            self.send_message_and_wait_for_response('start', 'control', 'starting', window)
            #window[f'run_status_{self.name}'].update(f'{str(count)}...')
            count += 1
        window[f'run_status_{self.name}'].update(f'{self.name} running')

    def load_run(self, window):
        count = 0
        while count < 8 :
            time.sleep(1)
            self.send_message_and_wait_for_response('load', 'control', 'loading', window)
            #window[f'load_status_{self.name}'].update(f'{str(count)}...')
            count += 1
        window[f'load_status_{self.name}'].update(f'{self.name} loaded')

    def clean_run(self, window):
        count = 0
        while count < 8:
            time.sleep(1)
            self.send_message_and_wait_for_response('clean', 'control', 'cleaning', window)
            #window[f'clean_status_{self.name}'].update(f'{str(count)}...')
            count += 1
        window[f'clean_status_{self.name}'].update(f'{self.name} cleaned')