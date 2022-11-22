from scenes.optics_test_set import OpticsTestSet

class OpticsTestSets():
    def __init__(self, optics_spec, systest_dirs):
        self.optics_spec = optics_spec
        self.test_set_paths = optics_spec.test_sets
        self.test_sets = []
        for partial_path in self.test_set_paths:
            self.test_sets.append(OpticsTestSet(partial_path, systest_dirs))

    def get_all_paths(self):
        paths = []
        for test_set in self.test_sets:
            paths.extend(test_set.scene_paths)
        return paths