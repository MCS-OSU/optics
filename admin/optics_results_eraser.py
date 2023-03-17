import sys
from pathlib            import Path
from core.optics_dirs   import SystestDirectories
from core.test_register import TestRegisterLocal
from opics_common.scene_type.type_constants import abbrev_types
class OpticsResultsEraser():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        self.project_name = optics_spec.proj
        home_dir = str(Path.home())
        systest_dirs = SystestDirectories(home_dir, optics_spec)
        self.test_register = TestRegisterLocal(systest_dirs)
        print('')
        print('')
        print('[optics]...!!! PREPARING TO ERASE RESULTS...!!!')
        print(f'systest data landscape for {optics_spec.name} looks like:')
        print(f'    trun session count: {self.test_register.get_session_count()}')
        print(f'    stdout_logs       : {self.test_register.get_stdout_log_count()}')
        print(f'    mcs_logs          : {self.test_register.get_mcs_log_count()}')
        print(f'    project name      : {systest_dirs.sessions_dir}')
       

        

    def erase_results(self):
        
        scene_type_list = abbrev_types[self.project_name]
        result = input(f' ***  Are you ABSOLUTELY sure you want to delete systest data for {self.optics_spec.name}.  Press enter to Y or N\n')
        print("Printing all the scene types for this project: ")
        print(*scene_type_list, sep = ", ")
        scene_type_choice = input(f' Select the scene type to erase or write all to delete all the scene_type: \n')
        if result == 'Y' or result == 'y':          
            print('[optics]...deleting systest data')
            self.test_register.clean_systest_data(scene_type_choice)
        else:
            print('[optics]...abandoned erase maneuver - exiting')
            sys.exit()
        

    