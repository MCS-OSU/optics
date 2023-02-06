import sys, os
import configparser
from core.constants import REPLAY_CONTROLLER, MCS_CONTROLLER  #, MCS_RECORDING_CONTROLLER
from opics.common.logging.log_constants import abbrev_types
from core.utils import optics_info, optics_fatal

class OpticsSpec():
    def __init__(self, config_path):
        optics_info(f'loading optics config file {config_path}')
        if not os.path.exists(config_path):
            optics_fatal('{config_path} does not exist')

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
            optics_fatal(f'config file name must start with pvoe_, avoe_ or inter_')

        self.version = self.config_name.replace(self.proj + '_', '')
        self.name = self.proj + '_' + self.version
        f = open(config_path, 'r')
        lines = f.readlines()
        f.close()
        self.load_scene_running_details(lines)
        self.load_container_construction_details(lines)

    def load_scene_running_details(self, lines):
        self.log_level        = self.load_logging_level(lines)
        self.test_sets        = self.load_test_sets(lines)
        self.controller       = self.load_controller(lines)
        self.save_videos      = self.load_save_videos_setting(lines)
        self.mcs_config_path  = self.load_mcs_config_path(self.save_videos)
        self.types_to_run     = self.load_types_to_run(lines)
        self.types_to_skip    = self.deduce_types_to_skip()
        self.print_scene_execution_summary()
        optics_info(f'optics_spec: proj {self.proj}')
        optics_info(f'optics_spec: version {self.version}')
        optics_info(f'optics_spec: test_sets {len(self.test_sets)}')
        optics_info(f'optics_spec: controller {self.controller}')

    def load_container_construction_details(self, lines):
        self.apptainer_repo_to_clone   = self.load_apptainer_repo_to_clone(lines)
        if self.apptainer_repo_to_clone != None:
            self.apptainer_branch_to_pull     = self.load_apptainer_branch_to_pull(lines)
            self.apptainer_lib_config_steps   = self.load_apptainer_config_steps(lines,'apptainer.config_step.libs')
            self.apptainer_model_config_steps = self.load_apptainer_config_steps(lines,'apptainer.config_step.models')

    def load_logging_level(self, lines):
        for line in lines:
            if line.strip().startswith('logging'):
                log_level = line.split(':')[1].upper().strip()
                if log_level in [ 'DEBUG','INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    print(f'logging level to set to {log_level}')
                    return log_level
        print('logging level defaulted to INFO')
        return 'INFO'

    def print_scene_execution_summary(self):
        optics_info('[optics]....which scene types are running')
        optics_info('')
        for t in self.types_to_run:
            optics_info('  ' + t)
        optics_info('')
        optics_info('[optics]....which scene types are being skipped')
        optics_info('')
        for sst in self.types_to_skip:
            optics_info(f'  {sst}')
        optics_info('')

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
                optics_fatal(f'cfg file contains deprecated skip_scene_types line: {line} - revise spec using the do_type:<scene_type> syntax')
            if line.startswith('do_type'):
                type = line.split(':')[1].strip()
                if type not in abbrev_types[self.proj]:
                    optics_fatal(f'cfg file contains type unknown for project {self.proj}: {type}')
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
                

    def load_apptainer_repo_to_clone(self, lines):
        for line in lines:
            if line.startswith('apptainer.repo_to_clone'):
                return line.split(':')[1].strip()
        return 'None'

    
    def load_apptainer_branch_to_pull(self, lines):
        for line in lines:
            if line.startswith('apptainer.branch_to_pull'):
                return line.split(':')[1].strip()
        return 'None'

    def load_apptainer_config_steps(self, lines, key):
        steps = []
        for line in lines:
            if line.startswith(key):
                steps.append(line.split(':')[1].strip())
        return steps


    def load_controller(self, lines):
        controller = MCS_CONTROLLER
        for line in lines:
            if line.startswith('controller'):
                controller = line.split(':')[1].strip()
        
        if controller not in [MCS_CONTROLLER, REPLAY_CONTROLLER]:  #, MCS_RECORDING_CONTROLLER
            optics_fatal(f'controller must be {MCS_CONTROLLER} or {REPLAY_CONTROLLER} in {self.config_path}')
        return controller
        

    def load_mcs_config_path(self, save_videos):
        if save_videos:
            optics_info('optics run configured to save videos')
            return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config_video.ini')
        optics_info('optics run configured to NOT save videos')
        return os.path.join(os.environ['OPICS_HOME'],'cfg','mcs_config.ini')


    def load_save_videos_setting(self, lines):
        for line in lines:
            if line.startswith('save_videos'):
                return True
        return False
        