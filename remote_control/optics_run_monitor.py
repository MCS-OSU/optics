import time, os
from datetime import datetime
from pathlib import Path
from env.process_utils import get_running_optics_processes
from remote_control.constants import max_run_time_for_type

def log_event(event):
    print(event)
    f = open('optics_monitor.log','a')
    timestamp = str(datetime.now()).split('.')[0]
    f.write(timestamp + ' - ' + event + '\n')
    f.close()

class OpticsRunMonitor():
    def __init__(self, run_name):
        self.run_name = run_name
        self.log_name = 'optics_monitor.log'

    def monitor_run(self):
        while True:
            time.sleep(10)
            if self.is_evidence_of_crash(self.run_name):
                log_event(f'\n     {self.run_name} has crashed !! - will clean up processes and relaunch the container...')
                self.kill_processes_related_to_run(self.run_name)
                return False
            if self.is_evidence_of_scene_running_too_long(self.run_name):
                scene_type = self.run_name.split('_')[0]
                log_event(f'\n     Container {self.run_name} will be stopped and restarted...')
                self.kill_processes_related_to_run(self.run_name)
                return False
            if self.is_evidence_of_run_complete(self.run_name):
                log_event(f'\n    The manager for {self.run_name} is either out of scenes or has been stopped for some reason.\n')
                return True

    def is_evidence_of_run_complete(self, run_name):
        optics_processes = get_running_optics_processes(run_name)
        home_dir = str(Path.home())
        root_dir = os.path.join(home_dir, 'test__' + run_name)
        dir = os.path.join(root_dir, 'scripts', 'scenes_being_run')
        files = os.listdir(dir)
        print(f'process count: {len(optics_processes)}, marker file count: {len(files)}')
        if len(files) == 0 and len(optics_processes) == 0:
            return True
        print('NO  evidence of run complete')
        return False

    def is_evidence_of_crash(self, run_name):
        optics_processes = get_running_optics_processes(run_name)
        print(f' matching process count: {len(optics_processes)}')
        running_scene_marker_present = not self.is_scenes_being_run_empty(run_name)
        print(f'running_scene_marker_present: {running_scene_marker_present}')
        if running_scene_marker_present and len(optics_processes) == 0:
            return True
        print('NO  evidence of crash')
        return False

    def is_scenes_being_run_empty(self, run_name):
        home_dir = str(Path.home())
        root_dir = os.path.join(home_dir, 'test__' + run_name)
        dir = os.path.join(root_dir, 'scripts', 'scenes_being_run')
        files = os.listdir(dir)
        if len(files) == 0:
            return True
        return False
        
    def is_evidence_of_scene_running_too_long(self, run_name):
        home_dir = str(Path.home())
        root_dir = os.path.join(home_dir, 'test__' + run_name)
        cur_running_scene_dir = os.path.join(root_dir, 'scripts', 'scenes_being_run')
        files = os.listdir(cur_running_scene_dir)
        if len(files) == 0:
            print('no file in scenes_being_run dir, so no evidence of scene running too long')
            return False
        # will always be at most one file, but just in case
        for file in files:
            file_path = os.path.join(cur_running_scene_dir, file)
            scene_type = file.split('_')[0]
            mtime = os.path.getmtime(file_path)
            max_run_time = max_run_time_for_type[scene_type] * 60
            duration = time.time() - mtime
            print(f'duration: {duration}     max_run_time: {max_run_time}')
            if duration > max_run_time:
                log_event(f'\n         scene {file} exceeded allowed time of {max_run_time_for_type[scene_type]}')
                return True
        print('NO evidence of scene running too long')
        return False


    def kill_processes_related_to_run(self, run_name):
        optics_processes = get_running_optics_processes(run_name)
        for p in optics_processes:
            log_event(f'\nkilling process {p.pid}    {p.line}')
            p.stop()
        unity_processes = get_running_optics_processes('Unity')
        for p in unity_processes:
            log_event(f'\nkilling process {p.pid}    {p.line}')
            p.stop()