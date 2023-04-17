class SceneObject:
    def __init__(self, obj):
        self.obj = obj

    def get_object_rotation(self):
        return self.obj['shows'][0]['rotation']
        
    def clear_object_rotation(self):
        self.obj['shows'][0]['rotation'] = {"x": 0.0,"y": 0.0,"z": 0.0}

    def set_position(self, x, z):
        self.obj['shows'][0]['position']['x'] = x
        self.obj['shows'][0]['position']['z'] = z


    def get_object_scale(self):
        return self.obj['shows'][0]['scale']


    def get_object_position(self):
        return self.obj['shows'][0]['position']

    def get_scale_x(self):
        return float(self.obj['shows'][0]['scale']['x'])

    def set_scale_x(self, scale_x):
        self.obj['shows'][0]['scale']['x'] = scale_x

    def set_scale_z(self, scale_z):
        self.obj['shows'][0]['scale']['z'] = scale_z

    def get_name(self):
        return self.obj['type']

    def has_force(self):
        if 'forces' in self.obj:
            if len(self.obj['forces']) > 0:
                return True
        return False

    def get_force_x(self):
        return self.obj['forces'][0]['vector']['x']

    def get_force_y(self):
        return self.obj['forces'][0]['vector']['y']

    def get_force_z(self):
        return self.obj['forces'][0]['vector']['z']
