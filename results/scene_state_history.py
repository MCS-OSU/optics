
# # test history for scene: coll_alpha_0001_01_A2_plaus
# 1667607576;ip-172-31-72-254;ready
# 1667607586;ip-172-31-72-254;IN_PROGRESS__SCENE_ASSIGNED
# 1667607587;ip-172-31-72-254;IN_PROGRESS__SCENE_STARTED
# 1667607587;ip-172-31-72-254;IN_PROGRESS__CONTROLLER_LAUNCHED
# 1667607607;ip-172-31-72-254;IN_PROGRESS__CONTROLLER_UP
# 1667607661;ip-172-31-72-254;IN_PROGRESS__SCENE_RUNNING
from core.optics_run_state import FAILED_GPU_MEM, COMPLETED, IN_PROGRESS_SCENE_STARTED, NOT_ATTEMPTED
from core.constants import TEST_HISTORY_FIRST_LINE_PREFIX
import logging

class SceneStateHistory():
    def __init__(self, scene_name, lines):
        self.is_well_formatted = self.is_well_formatted(lines)
        if not self.is_well_formatted:
            return
        logger = logging.getLogger()
        logger.debug(f'SceneStateHistory {scene_name}')
        end_line = lines[-1]
        self.end_state = end_line.split(';')[2].strip()
        self.scene_name = scene_name
        self.scene_type = scene_name.split('_')[0]
        
        #print(f'scene_type: {self.scene_type}')
        self.lines = lines
        header = lines[0]
        self.end_time = end_line.split(';')[0].strip()
        self.start_time = self.get_most_recent_scene_started_time()
        
        if self.is_completed():
            self.completion_duration = int(self.end_time) - int(self.start_time)
        else:
            self.completion_duration = None
       
        self.duration_since_last_retry = self.get_duration_since_last_retry()
        if False:
        #if self.is_completed():
            print(f'start_time: {self.start_time}')
            print(f'end_time: {self.end_time}')
            print(f'completion_duration: {self.completion_duration}')
            print(f'duration_since_last_retry: {self.duration_since_last_retry}')
            print(f'scene_name: {scene_name}')
            for line in lines:
                print(line)

    def is_well_formatted(self, lines):
        # should have at least the header comment and the 'ready' line
        if len(lines) < 2:
            return False
        # first line should be header
        if not TEST_HISTORY_FIRST_LINE_PREFIX in lines[0]:
            return False
        #second line should be 'ready' state
        if not NOT_ATTEMPTED in lines[1]:
            return False
        return True
        
    def get_most_recent_scene_started_time(self):
        for line in reversed(self.lines):
            if IN_PROGRESS_SCENE_STARTED in line:
                return line.split(';')[0].strip()
        return None

    def is_completed(self):
        return self.end_state == 'COMPLETED'

    def get_duration_since_last_retry(self):
        # Find the last retry
        last_retry_time = None
        #print(f'last_retry_time: {last_retry_time}')
        for line in self.lines:
            if 'RETRY' in line:
                last_retry_time = line.split(';')[0].strip()
                #print(f'last_retry_time after retry found: {last_retry_time}')
        if last_retry_time is None:
            return None
        else:
            return int(self.end_time) - int(last_retry_time)

    def get_gpu_mem_fail_count(self):
        count = 0
        for line in self.lines:
            if FAILED_GPU_MEM in line:
                count += 1
        return count
        
