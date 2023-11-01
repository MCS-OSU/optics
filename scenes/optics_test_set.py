import os, sys
from scenes.scene_json import SceneJson
from core.constants import MAX_ROOM_DIMENSION
from core.utils import optics_debug

def exit_with(error_msg):
    print(error_msg)
    sys.exit()

class OpticsTestSet():
    def __init__(self, partial_path, systest_dirs):
        root_dir = systest_dirs.systest_dir
        set_full_path = os.path.join(root_dir, partial_path)
        if not os.path.exists(set_full_path):
            exit_with(f'ERROR - test_set path {set_full_path} does not exist')
        self.name = os.path.basename(set_full_path)
        self.scene_paths = self.load_scene_paths(set_full_path,root_dir)
        self.validate_scene_paths(self.scene_paths)

    def load_scene_paths(self, set_full_path, root_dir):
        scene_paths = []
        f = open(set_full_path, 'r')
        lines = f.readlines()
        f.close()
        self.scene_jsons = []
        for line in lines:
            if line.strip() == '':
                continue
            full_path_to_json_scene_file = os.path.join(root_dir, line.strip())
            if self.is_multa_training_scene(full_path_to_json_scene_file):
                continue
            scene_json = SceneJson(full_path_to_json_scene_file)
            max_room_dimension = scene_json.get_max_room_dimension()
            if (max_room_dimension <= MAX_ROOM_DIMENSION or True):
                scene_paths.append(full_path_to_json_scene_file)
                # if 'ramp' in full_path_to_json_scene_file:
                #     print(f'FYI - including scene {full_path_to_json_scene_file}')
            else:
                pass
                # if 'ramp' in full_path_to_json_scene_file:
                #     print(f'FYI - omitting scene {full_path_to_json_scene_file} because max room dimension is {max_room_dimension}')
        return scene_paths

    def validate_scene_paths(self, scene_paths):
        for scene_path in scene_paths:
            if not os.path.exists(scene_path):
                exit_with(f'ERROR - scene path {scene_path} does not exist')
            if not scene_path.endswith('.json'):
                exit_with(f'ERROR - scene path {scene_path} must end with .json')

    def is_multa_training_scene(self, scene_path):
        if 'multa_' in scene_path and '_training_' in scene_path:
            return True
        return False
