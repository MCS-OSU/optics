import os
from core.optics_session import OpticsSession
import core.utils as utils

class OpticsSessions():
    def __init__(self, systest_dirs, scene_state_histories):
        self.systest_dirs = systest_dirs
        self.sessions_dir = systest_dirs.sessions_dir
        self.scene_state_histories = scene_state_histories
        self.sessions = self.load_sessions(self.scene_state_histories)
        
    def load_sessions(self, scene_state_histories):
        sessions = []
        session_files = os.listdir(self.systest_dirs.sessions_dir)
        
        for session_file in session_files:
            try:
                session_path = os.path.join(self.systest_dirs.sessions_dir, session_file)
                f = open(session_path, 'r')
                lines = f.readlines()
                f.close()
                #print(f'session path {session_path}')
                session = OpticsSession(lines,self.scene_state_histories)
                if session.healthy:
                    sessions.append(session)
                else:
                    print(f'session not healthy: {session_path} {session.state}')
            except Exception as err:
                print(f'Error loading session {session_path} {err}')
        return sessions

    def is_log_bad(self, bad_logs, scene_name, exception_start_string):
        for log in bad_logs:
            if log.scene_name == scene_name:
                return True 
        return False

    def show_exceptions_by_session(self, optics_logs, exception_start_string):
        bad_logs = optics_logs.get_logs_with_crash_starting_with(exception_start_string)
        for session in self.sessions:
            print(f'    machine {session.machine}:')
            scenes_attempted = session.get_scenes_attempted()
            for scene_path in scenes_attempted:
                scene_name = os.path.basename(scene_path).split('.')[0]
                if self.is_log_bad(bad_logs, scene_name, exception_start_string):
                    print(f'       {scene_name}')


    def get_session_info(self):
        sessions_details = dict()
        for session in self.sessions:
            session.idle_time = session.convert_to_time_format(session.idle_time)
            session.duration = session.convert_to_time_format(session.duration)
            sessions_details[session]= [session.idle_time, session.machine, session.job_count, session.duration]
        return sessions_details

    def sort_by_idle_time(self):
        self.sessions.sort()

    def display_info_header(self):
        print("\n") #Added a blank line to separate the output 
        print("------------------------------------------------------------------------------------------------------")
        print("idle_time".ljust(15) + "machine_id".ljust(50) + "scene_count".ljust(15) + "duration")
        print("------------------------------------------------------------------------------------------------------")

    def print_session_info(self):
        
        for session in self.sessions:
            session.idle_time = session.convert_to_time_format(session.idle_time)
            session.duration = session.convert_to_time_format(session.duration)
            print(f'{str((session.idle_time)).ljust(15)}{str(session.machine).ljust(50)}{str(session.job_count).ljust(15)}{str(session.duration).ljust(15)}')
