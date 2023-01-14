import os
from  core.constants import JOB_REQUEST, JOB_ASSIGN
from core.utils import optics_info, optics_debug
class RunnerSessions():
    def __init__(self,sessions_dir):
        self.sessions_dir = sessions_dir
        
    def get_sessions_with_job_requests(self):
        optics_debug('====================================================================')
        optics_debug('get sessions wqith job requests')
        result = []
        files = os.listdir(self.sessions_dir)
        for file in files:
            path = os.path.join(self.sessions_dir, file)
            optics_debug(f'checking session...{path}')
            #print(f'opening session {path}')
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            last_line = lines[-1]
            optics_debug(f'last line : {last_line}')
            if JOB_REQUEST in last_line:
                optics_debug('job request found - add this session to list')
                result.append(path)
            else:
                optics_debug('no job_request in last line - skip')
        return result
