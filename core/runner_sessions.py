import os
from  core.constants import JOB_REQUEST, JOB_ASSIGN
class RunnerSessions():
    def __init__(self,sessions_dir):
        self.sessions_dir = sessions_dir
        
    def get_sessions_with_job_requests(self):
        result = []
        files = os.listdir(self.sessions_dir)
        for file in files:
            path = os.path.join(self.sessions_dir, file)
            #print(f'opening session {path}')
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            last_line = lines[-1]
            #print(f'last line : {last_line}')
            if JOB_REQUEST in last_line:
                result.append(path)
        return result
