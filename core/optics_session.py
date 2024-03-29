from core.constants import JOB_REQUEST, JOB_ASSIGN, SESSION_KILLED
from core.ec2_mappings import get_ec2_machine_name_for_uname_output
import time

## trun_session;v5_final2;ip-172-31-72-254;1667607584
#1667607584;ip-172-31-72-254;TRUN_JOB_REQUEST;v5_final2
#1667607586;ip-172-31-72-254;TMAN_JOB_ASSIGN;/home/ubuntu/eval6_systest/scenes_source_all/full/pvoe/coll/coll_alpha_0001_01_A2_plaus.json

SESSION_STATE_EMPTY_FILE    = 'empty_file'
SESSION_STATE_LACKS_REQUEST = 'lacks_request'
SESSION_STATE_REQUEST_UNANSWERED = 'lacks_assigment'

class OpticsSession():
    def __init__(self, lines,scene_state_histories):
        self.lines = lines
        self.scene_state_histories = scene_state_histories
        if len(lines) == 0:
            self.healthy = False
            self.state = SESSION_STATE_EMPTY_FILE
        elif len(lines) == 1:
            self.healthy = False
            self.state = SESSION_STATE_LACKS_REQUEST
        elif len(lines) == 2:
            self.healthy = False
            self.state = SESSION_STATE_REQUEST_UNANSWERED
        else:
            self.healthy = True
            header = lines[0]
            [_,_,machine, start_time] = header.split(';')
            self.machine = get_ec2_machine_name_for_uname_output(machine)
            self.start_time = start_time
            self.jobs = []
            for i in range(1, len(lines)):
                line = lines[i]
                if JOB_ASSIGN in line:
                    self.jobs.append(line.split(';')[3].split('/')[-1].split('.')[0])
                    # print(f'JOB: {self.jobs[-1]}')
            self.job_count = self.scene_state_histories.get_completed_job_count(self.jobs)
            
            if len(lines) == 2:
                self.end_time = self.start_time
                self.duration = 0
                self.last_activity = self.start_time
            else:
                self.end_time = lines[-1].split(';')[0]
                self.duration = int(float(int(self.end_time) - int(self.start_time))/60.0) # in minutes
                self.last_activity = lines[-1].split(';')[0]
            current_time = int(time.time())
            self.idle_time = int(float(current_time - int(self.last_activity))/60.0) # in minutes
            self.session_killed_message = ''
            if SESSION_KILLED in lines[-1]:
                self.session_killed_message = SESSION_KILLED
    
    def __lt__(self, other):
        return self.idle_time < other.idle_time
        
    

    def summary(self):
        print(f'    {self.machine}  {self.job_count} scenes   {self.duration} mins  {self.idle_time} mins idle    {self.session_killed_message}')

    def get_scenes_attempted(self):
        paths = []
        for line in self.lines:
            if JOB_ASSIGN in line:
                [_,_,_,path] = line.split(';')
                paths.append(path)
        return paths


    def convert_to_time_format(self, time_in_minutes):
        
        n  = int(time_in_minutes)
        # print(f'N:{n}')
        days = int(n // 1440)
        # print(f'Days:{days}')
        n = n % (1440)
        hours = int(n // 60)
        # print(f'Hours:{hours}')
        n %= 60
        minutes = n
        # print(f'Minutes:{minutes}\n')
       
        time_format = ''
        if days > 0:
            time_format += f'{days}d '
        
        # Add leading zero to hours 
        time_format += f'{hours:02d}h '

        # Add leading zero to minutes 
        time_format += f'{minutes:02d}m '

        return time_format