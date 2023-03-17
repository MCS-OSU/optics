import os
from core.optics_session import OpticsSession
from optics_results.scene_state_history import SceneStateHistory

class SceneStateHistories:
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs
        self.scene_state_dir = systest_dirs.scene_state_dir
        self.histories = self.load_histories()

    def get_completed_job_count(self,scene_names):
        # print(f'HISTORY KEYS: {self.histories.keys()[0]}')
        # print(f'SCENE NAMES:{scene_names[0]}')
        count = 0
        for scene_name in scene_names:
            history = self.histories[scene_name]
            # print(f'history {history}')
            if history.is_completed():
                count += 1
        
        return count

    def load_histories(self):
        histories = {}
        scene_state_scene_type = os.listdir(self.systest_dirs.scene_state_dir)
        # print(f'SCENE STATE SCENE TYPE:  {scene_state_scene_type}')
        for scene_state_file in scene_state_scene_type:
            
            scene_state_path = os.path.join(self.systest_dirs.scene_state_dir, scene_state_file)

            for scene_state_filename in os.listdir(scene_state_path):
                scene_state_filename_path = os.path.join(scene_state_path, scene_state_filename)
                # print(f'SCENE_STATE_FILENAME_PATH: {scene_state_filename_path}')
                f = open(scene_state_filename_path, 'r')
                lines = f.readlines()
                f.close()
                scene_name = scene_state_filename.split('.')[0].replace('_state','')
                history = SceneStateHistory(scene_name,lines)
                # print(scene_name)
                histories[scene_name] = history
        # print(f'HISTORIES: {histories}')   
            # f = open(scene_state_path, 'r')
            # lines = f.readlines()
            # f.close()
            # scene_name = scene_state_file.split('.')[0]
            # history = SceneStateHistory(scene_name,lines)
            # histories[scene_name] = history
        return histories