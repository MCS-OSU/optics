
from core.optics_dirs import SystestDirectories
from opics_common.scene_type.type_constants import formal_type
from opics_common.opics_logging.opics_logs    import OpicsLogs
from core.optics_spec_loader            import OpticsSpec
from pathlib import Path
import os

class ErrorDetails():
    def __init__(self, optics_spec):
        systest_dirs = SystestDirectories(str(Path.home()), optics_spec) 
        proj_log_dir = systest_dirs.result_logs_dir
        self.proj = optics_spec.proj
        
        self.opics_logs = OpicsLogs()
        for scene_type in formal_type:    #just look for all types for all projects - those not present will be ignored
            type_dir = os.path.join(proj_log_dir, scene_type)
            if os.path.exists(type_dir):
                files = os.listdir(type_dir)
                print(type_dir)
                for file in files:
                    filepath = os.path.join(type_dir, file)
                    if os.path.isfile(filepath):
                        #print(f'file:  {filepath}')
                        self.opics_logs.load_file(filepath, self.proj, scene_type)

    def show_error_type_counts_inter(self):
        error_counts = {}
        for scene_type in self.opics_logs.logs[self.proj]:
            print(f'scene_type {scene_type}')
            logs_for_scene_type = self.opics_logs.logs[self.proj][scene_type]
            for log in logs_for_scene_type:
                if not log.exception_info == 'NA':
                    if not log.exception_info in error_counts:
                        error_counts[log.exception_info] = 0
                    error_counts[log.exception_info] += 1
            error_count_infos = []
            for error_name in error_counts:
                error_count_info = {'type':error_name, 'count':error_counts[error_name]}
                error_count_infos.append(error_count_info)
            error_count_infos = sorted(error_count_infos, key=lambda d: d['count'])
            for error_count_info in error_count_infos:
                print(f"{error_count_info['type']} {error_count_info['count']}")

    def show_errors_by_scene_type_inter(self):
        for scene_type in self.opics_logs.logs[self.proj]:
            print(f'scene_type {scene_type}')
            logs_for_scene_type = self.opics_logs.logs[self.proj][scene_type]
            for log in logs_for_scene_type:
                if not log.exception_info == 'NA':
                    print(f'{log.scene_name} {log.exception_info}')
