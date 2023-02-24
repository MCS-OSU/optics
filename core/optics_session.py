from core.constants import JOB_REQUEST, JOB_ASSIGN, SESSION_KILLED
import time
## trun_session;v5_final2;ip-172-31-72-254;1667607584
#1667607584;ip-172-31-72-254;TRUN_JOB_REQUEST;v5_final2
#1667607586;ip-172-31-72-254;TMAN_JOB_ASSIGN;/home/ubuntu/eval6_systest/scenes_source_all/full/pvoe/coll/coll_alpha_0001_01_A2_plaus.json

SESSION_STATE_EMPTY_FILE    = 'empty_file'
SESSION_STATE_LACKS_REQUEST = 'lacks_request'

class OpticsSession():
    def __init__(self, lines):
        self.lines = lines
        if len(lines) == 0:
            self.healthy = False
            self.state = SESSION_STATE_EMPTY_FILE
        elif len(lines) == 1:
            self.healthy = False
            self.state = SESSION_STATE_LACKS_REQUEST
        else:
            self.healthy = True
            header = lines[0]
            [_,_,machine, start_time] = header.split(';')
            self.machine = machine
            self.start_time = start_time
            self.jobs = []
            for i in range(1, len(lines)):
                line = lines[i]
                if JOB_ASSIGN in line:
                    self.jobs.append(line.split(';')[3].split('/')[-1].split('.')[0])
            self.job_count = len(self.jobs)
            
            if len(lines) == 2:
                self.end_time = self.start_time
                self.duration = 0
                self.last_activity = self.start_time
            else:
                self.end_time = lines[-1].split(';')[0]
                self.duration = '{0:.2f}'.format((int(self.end_time) - int(self.start_time))/60.0)
                self.last_activity = lines[-1].split(';')[0]
            current_time = int(time.time())
            self.idle_time = int((current_time - int(self.last_activity))/60.0)
            self.session_killed_message = ''
            if SESSION_KILLED in lines[-1]:
                self.session_killed_message = SESSION_KILLED
    
    def __lt__(self, other):
        return self.idle_time < other.idle_time
        
    def summary(self):
        print(f'    {self.machine}  {self.job_count} scenes   {self.duration} mins  {self.idle_time} mins idle    {self.session_killed_message}')

    def convert_to_time_format(self, time_in_seconds):
        days = time_in_seconds // (24 * 3600)
        hours = (time_in_seconds // 3600) % 24
        minutes = (time_in_seconds // 60) % 60
        seconds = time_in_seconds % 60
        
        time_format = ''
        if days > 0:
            time_format += f'{days}d '

        # Add leading zero to hours 
        time_format += f'{hours:02d}h '

        # Add leading zero to minutes 
        time_format += f'{minutes:02d}m '

        if seconds > 0:
            time_format += f'{seconds}s '

        return time_format