import os
from pathlib import Path
from opics_common.opics_logging.log_loader import LogLoader
from opics_common.scene_type.type_constants import abbrev_types
from core.optics_dirs import SystestDirectories


def get_cube_id_from_filepath(filepath):
    filename = os.path.basename(filepath)
    cube_id = filename.split("_")[4]
    return cube_id


class OpticsLogs():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        self.proj = optics_spec.proj
        self.systest_dirs = SystestDirectories(str(Path.home()), self.optics_spec)
        self.proj_log_dir = self.systest_dirs.result_logs_dir
        self.logs                     = {}
        self.logs["pvoe"]             = {}
        self.logs["avoe"]             = {}
        self.logs["inter"]            = {}

        self.logs_for_cubes           = {}
        self.logs_for_cubes["pvoe"]   = {}
        self.logs_for_cubes["avoe"]   = {}
        self.logs_for_cubes["inter"]  = {}
        self.load_files()

    def load_files(self):
        for scene_type in abbrev_types[self.proj]:
            type_dir = os.path.join(self.proj_log_dir, scene_type)
            if os.path.exists(type_dir):
                files = os.listdir(type_dir)
                #print(type_dir)
                for file in files:
                    filepath = os.path.join(type_dir, file)
                    #print(f'log file {filepath}')
                    if os.path.isfile(filepath):
                        # print(f'file:  {filepath}')
                        self.load_file(filepath, self.proj, scene_type)

    def load_file(self, filepath, proj, scene_type):
        f = open(filepath, "r")
        lines = f.readlines()
        clean_lines = []
        for line in lines:
            clean_lines.append(line.rstrip())
        f.close()

        log_loader = LogLoader(proj, scene_type, clean_lines, filepath)
        if not scene_type in self.logs[proj]:
            self.logs[proj][scene_type] = []
            self.logs_for_cubes[proj][scene_type] = {}
        self.logs[proj][scene_type].append(log_loader.scene_log)

        cube_id = get_cube_id_from_filepath(filepath)
        if not cube_id in self.logs_for_cubes[proj][scene_type]:
            self.logs_for_cubes[proj][scene_type][cube_id] = []
        self.logs_for_cubes[proj][scene_type][cube_id].append(
            log_loader.scene_log
        )


    def remove_logs(self, scene_type, scene_name):
        log_path = os.path.join(self.systest_dirs.result_logs_dir,scene_type,scene_name + '.log')
        stdout_log_path = os.path.join(self.systest_dirs.stdout_logs_dir,scene_type,scene_name + '_stdout.txt')

        print(f'      deleting {log_path}')
        os.system(f'rm {log_path}')
        print(f'      deleting {stdout_log_path}')
        os.system(f'rm {stdout_log_path}')

    def get_logs_with_crash_starting_with(self, crash_start_string):
        logs_matching = []
        for scene_type in self.logs[self.proj]:
            scene_logs_for_type = self.logs[self.proj][scene_type]
            for scene_log in scene_logs_for_type:
                if not scene_log.exception_info == None:
                    if scene_log.exception_info.startswith(crash_start_string):
                        logs_matching.append(scene_log)
        return logs_matching


    def express_exceptions(self, proj):
        exceptions = {}
        for scene_type in abbrev_types[proj]:
            if scene_type in self.logs[proj]:
                for log in self.logs[proj][scene_type]:
                    if not None == log.exception_info:
                        e = log.exception_info
                        if not e in exceptions:
                            exceptions[e] = []
                        exceptions[e].append(log.scene_name)
        print("\n\nException Scenes:\n")
        for e in exceptions:
            scenes = exceptions[e]
            print(f"\n{e}:")
            for scene in scenes:
                print(f"         {scene}")

