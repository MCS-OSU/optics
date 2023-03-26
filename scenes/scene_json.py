import json, os
from scenes.scene_object import SceneObject

class SceneJson:
    def __init__(self, path):
        if not path.endswith('.json'):
            raise f"scene path must end with .json : {scene_path}"
        if not os.path.exists(path):
            raise f"scene path {path} does not exist"
        f = open(path, 'r')
        self.data = json.load(f)
        f.close()
        self.objects = self.data['objects']
        self.object_count = len(self.objects)
    
    def get_objects_json(self):
        return self.objects


    def get_max_room_dimension(self):
        x =int(self.data['roomDimensions']['x'])
        z =int(self.data['roomDimensions']['z'])
        return max(x,z)


    def get_scene_objects(self):
        result = []
        for obj in self.objects:
            result.append(SceneObject(obj))
        return result
        
    def get_object_with_id(self, id):
        for obj in self.objects:
            if obj['id'] == id:
                return obj
    
        raise "no object with id {}".format(id)

    def set_ai_rotation(self, rotation_x, rotation_y):
        self.data['performerStart']['rotation']['x'] = rotation_x
        self.data['performerStart']['rotation']['y'] = rotation_y


    def get_starting_position(self):
        return self.data['performerStart']['position']

    def set_starting_position(self, ai_position_x, ai_position_z):
        self.data['performerStart']['position']['x'] = ai_position_x
        self.data['performerStart']['position']['z'] = ai_position_z


    def get_non_structure_object_names(self):
        result = []
        for obj in self.objects:
            if not 'structure' in obj:
                result.append(obj['type'])
        return result

    def get_room_dimensions(self):
        return self.data['roomDimensions']
        
    def get_focus_objects(self):
        result = []
        objs = self.get_objects_json()
        for obj in objs:
            id = obj['id']
            if not( "platform_" in id or "throwing_device_" in id or "placer_" in id or "occluder_" in id or "dropping_device_" in id):
                result.append(obj)
        return result