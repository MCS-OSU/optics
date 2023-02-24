import os
from core.optics_session import OpticsSession
import core.utils as utils

class OpticsSessions():
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs
        self.sessions_dir = systest_dirs.sessions_dir
        self.sessions = self.load_sessions()

    def load_sessions(self):
        sessions = []
        session_files = os.listdir(self.systest_dirs.sessions_dir)
        
        print(utils.header(f' sessions: {len(session_files)}'))
        for session_file in session_files:
            session_path = os.path.join(self.systest_dirs.sessions_dir, session_file)
            f = open(session_path, 'r')
            lines = f.readlines()
            f.close()
            #print(f'session path {session_path}')
            session = OpticsSession(lines)
            if session.healthy:
                sessions.append(session)
            else:
                print(f'session not healthy: {session_path} {session.state}')
        return sessions

    def sort_by_idle_time(self):
        self.sessions.sort()

    def display_info_header(self):
        print("\n") #Added a blank line to separate the output 
        print("------------------------------------------------------------------------------------------------------")
        print("idle_time".ljust(15) + "machine_id".ljust(50) + "scene_count".ljust(15) + "duration")
        print("------------------------------------------------------------------------------------------------------")

    def print_machine_names(self):
        for session in self.sessions:
            numeric_duration = ''.join(filter(str.isdigit, session.duration))
            session.idle_time = session.convert_to_time_format(session.idle_time*60)
            session.duration = session.convert_to_time_format(int(float(numeric_duration)*60))
            print(f'{str(session.idle_time).ljust(15)}{str(session.machine).ljust(50)}{str(session.job_count).ljust(15)}{str(session.duration).ljust(15)}')