import sys, os
import configparser
from core.constants import REPLAY_CONTROLLER, MCS_CONTROLLER  #, MCS_RECORDING_CONTROLLER
from opics.common.logging.log_constants import abbrev_types

def exit_with(msg):
    print(msg)
    sys.exit()

class OpticsSpec():
    def __init__(self, config_path):
        print(f'loading optics config file {config_path}')
        if not os.path.exists(config_path):
            exit_with(f'ERROR - {config_path} does not exist')

        self.config_path = config_path
        self.config_fname = os.path.basename(config_path)
        self.config_name = self.config_fname.split('.')[0]
        if self.config_name.startswith('pvoe_'):
            self.proj = 'pvoe'
        elif self.config_name.startswith('avoe_'):
            self.proj = 'avoe'
        elif self.config_name.startswith('inter_'):
            self.proj = 'inter'
        else:
            exit_with(f'ERROR - config file name must start with pvoe_, avoe_ or inter_')

        self.version = self.config_name.replace(self.proj + '_', '')
        self.name = self.proj + '_' + self.version
        f = open(config_path, 'r')
        lines = f.readlines()
        f.close()
        self.test_sets        = self.load_test_sets(lines)
        self.controller       = self.load_controller(lines)
        self.mcs_config_path  = self.load_mcs_config_path(lines)
        self.skip_scene_types = self.load_skip_scene_types(lines)
        for sst in self.skip_scene_types:
            print(f'skipping scene type {sst}')
        print(f'optics_spec: proj {self.proj}')
        print(f'optics_spec: version {self.version}')
        print(f'optics_spec: test_sets {len(self.test_sets)}')
        print(f'optics_spec: controller {self.controller}')
          
    def load_test_sets(self, lines):
        test_sets = []
        for line in lines:
            if line.startswith('test_set'):
                test_sets.append(line.split(':')[1].strip())
        return test_sets

    def load_skip_scene_types(self, lines):
        skip_scene_types = []
        for line in lines:
            if line.startswith('skip_scene_types'):
                skip_scene_types = list(map(str.strip, line.split(':')[1].strip().split(',')))
        for scene_type in skip_scene_types:
            if scene_type not in abbrev_types[self.proj]:
                exit_with(f'OPTICS ERROR - scene type {scene_type} unknown for {self.proj}')
        return skip_scene_types


    def load_controller(self, lines):
        controller = MCS_CONTROLLER
        for line in lines:
            if line.startswith('controller'):
                controller = line.split(':')[1].strip()
        
        if controller not in [MCS_CONTROLLER, REPLAY_CONTROLLER]:  #, MCS_RECORDING_CONTROLLER
            exit_with(f'OPTICS ERROR - controller must be {MCS_CONTROLLER} or {REPLAY_CONTROLLER} in {self.config_path}')
        return controller
        

    def load_mcs_config_path(self, lines):
        for line in lines:
            if line.startswith('save_videos'):
                print('---------optics run configured to save videos ----------')
                return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config_video.ini')
        print('---------optics run configured to NOT save videos ----------')
        return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config.ini')
        