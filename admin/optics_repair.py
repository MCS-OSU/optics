import os, sys
from pathlib import Path
from core.optics_logs import OpticsLogs
from core.optics_dirs import SystestDirectories
from optics_results.scene_state_histories import SceneStateHistories
from optics_results.optics_sessions import OpticsSessions

class OpticsRepair():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        self.proj = optics_spec.proj
        home_dir = str(Path.home())
        self.systest_dirs = SystestDirectories(home_dir, optics_spec)


    def reset_unity_exceptions(self, optics_logs):
        unity_crash_scenes = optics_logs.get_logs_with_crash_starting_with("Unity")
        if len(unity_crash_scenes) > 0:
            scene_state_histories = SceneStateHistories(self.systest_dirs)
            for scene_log in unity_crash_scenes:
                print(f'Unity issue found with {scene_log.scene_name}\n')
                for line in scene_log.lines:
                    print(f'    {line}')
                answer = input('reset this scene?  y/n')
                if answer.lower() == 'y':
                    print(f'\n....resetting {scene_log.scene_name} \n')
                    optics_logs.remove_logs(scene_log.scene_type, scene_log.scene_name)
                    scene_state_histories.reset_scene(scene_log.scene_type, scene_log.scene_name)
                else:
                    print(f'\n....leaving {scene_log.scene_name} intact\n')

    def show_summary(self, optics_logs):
        schs = SceneStateHistories(self.systest_dirs)
        optics_sessions = OpticsSessions(self.systest_dirs, schs)
        optics_sessions.show_exceptions_by_session(optics_logs, 'Unity')


    def reset_scenes(self):
        optics_logs = OpticsLogs(self.optics_spec)
        self.show_summary(optics_logs)
        self.reset_unity_exceptions(optics_logs)