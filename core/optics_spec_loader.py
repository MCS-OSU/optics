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
        self.save_videos      = self.load_save_videos_setting(lines)
        self.mcs_config_path  = self.load_mcs_config_path(self.save_videos)
        self.types_to_run     = self.load_types_to_run(lines)
        self.types_to_skip    = self.deduce_types_to_skip()
        self.print_scene_execution_summary()
        print(f'optics_spec: proj {self.proj}')
        print(f'optics_spec: version {self.version}')
        print(f'optics_spec: test_sets {len(self.test_sets)}')
        print(f'optics_spec: controller {self.controller}')

    def print_scene_execution_summary(self):
        print('[optics]....which scene types are running')
        print('')
        for t in self.types_to_run:
            print('  ' + t)
        print('')
        print('[optics]....which scene types are being skipped')
        print('')
        for sst in self.types_to_skip:
            print(f'  {sst}')
        print('')

    def load_test_sets(self, lines):
        test_sets = []
        for line in lines:
            if line.startswith('test_set'):
                test_sets.append(line.split(':')[1].strip())
        return test_sets

    def load_types_to_run(self, lines):
        types_to_run = []
        # find all valid do_type declarations, complain if unknown type
        for line in lines:
            if line.startswith('skip_scene_types'):
                exit_with(f'ERROR - cfg file contains deprecated skip_scene_types line: {line} - revise spec using the do_type:<scene_type> syntax')
            if line.startswith('do_type'):
                type = line.split(':')[1].strip()
                if type not in abbrev_types[self.proj]:
                    exit_with(f'ERROR - cfg file contains type unknown for project {self.proj}: {type}')
                types_to_run.append(type)
        # if no do_type lines, then run all types
        if len(types_to_run) == 0:
            types_to_run = abbrev_types[self.proj]
        return types_to_run

    def deduce_types_to_skip(self):
        types_to_skip = []
        for scene_type in abbrev_types[self.proj]:
            if scene_type not in self.types_to_run:
                types_to_skip.append(scene_type)
        return types_to_skip
                

    def load_controller(self, lines):
        controller = MCS_CONTROLLER
        for line in lines:
            if line.startswith('controller'):
                controller = line.split(':')[1].strip()
        
        if controller not in [MCS_CONTROLLER, REPLAY_CONTROLLER]:  #, MCS_RECORDING_CONTROLLER
            exit_with(f'OPTICS ERROR - controller must be {MCS_CONTROLLER} or {REPLAY_CONTROLLER} in {self.config_path}')
        return controller
        

    def load_mcs_config_path(self, save_videos):
        if save_videos:
            print('---------optics run configured to save videos ----------')
            return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config_video.ini')
        print('---------optics run configured to NOT save videos ----------')
        return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config.ini')


    def load_save_videos_setting(self, lines):
        for line in lines:
            if line.startswith('save_videos'):
                return True
        return False
        