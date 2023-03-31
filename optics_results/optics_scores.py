import sys
import os
from pathlib import Path
from opics_common.scene_type.type_constants import formal_type
from opics_common.opics_logging.opics_logs import OpicsLogs
from opics_common.results.stats_output import stats_title
from opics_common.results.stats_pvoe import StatsPvoe
from opics_common.results.stats_avoe import StatsAvoe
from opics_common.results.stats_inter import StatsInter
from core.optics_dirs import SystestDirectories

class OpticsScores:
    def __init__(self, proj, optics_spec):
        self.proj = proj
        self.optics_spec = optics_spec
        self.systest_dirs = SystestDirectories(str(Path.home()), self.optics_spec)
        self.proj_log_dir = self.systest_dirs.result_logs_dir

        if 'OPTICS_HOME' not in os.environ:            
            print('')
            print("      ERROR - OPTICS_HOME not defined.  Please 'export OPTICS_HOME=<parent_of_opics_dir>'")
            print('')
            sys.exit()

        self.opics_logs = OpicsLogs()

        for scene_type in formal_type:
            type_dir = os.path.join(self.proj_log_dir, scene_type)
            if os.path.exists(type_dir):
                files = os.listdir(type_dir)
                #print(type_dir)
                for file in files:
                    filepath = os.path.join(type_dir, file)
                    #print(f'log file {filepath}')
                    if os.path.isfile(filepath):
                        # print(f'file:  {filepath}')
                        self.opics_logs.load_file(filepath, proj, scene_type)
        
        
        #load_file(self, filepath, proj, scene_type):
        if self.proj == 'pvoe':
            self.pvoe_stats = StatsPvoe(self.opics_logs,'pvoe')
        
        elif self.proj == 'avoe':
            self.avoe_stats = StatsAvoe(self.opics_logs,'avoe')
        
        else:
            self.inter_stats = StatsInter(self.opics_logs,'inter')
    
    def show_exceptions(self):
        self.opics_logs.express_exceptions(self.proj)

    def show_scores(self):
        stats_title(self.proj_log_dir)

        if self.proj == 'pvoe':
            self.pvoe_stats.results_summary()
            self.pvoe_stats.results_by_scene_type()
            self.pvoe_stats.results_plausible_by_scene_type()
            self.pvoe_stats.results_implausible_by_scene_type()
            self.pvoe_stats.results_by_scene_type_and_cube_id()
            # self.pvoe_stats.compare_results_to_ta2_eval5_runs(systest_dirs.eval5_answer_keys_dir)
            print('')
            
            # self.pvoe_stats.outcome_by_category('plausible','correct')
            # self.pvoe_stats.outcome_by_category('plausible','incorrect')
            # self.pvoe_stats.outcome_by_category('implausible','correct')
            # self.pvoe_stats.outcome_by_category('implausible','incorrect')
            
        elif self.proj == 'avoe':
            self.avoe_stats.results_summary()
            self.avoe_stats.results_by_scene_type()
            self.avoe_stats.results_expected_by_scene_type()
            self.avoe_stats.results_unexpected_by_scene_type()
            print('')
            # self.avoe_stats.pvoe_outcome_by_category('expected','correct')
            # self.avoe_stats.pvoe_outcome_by_category('expected','incorrect')
            # self.avoe_stats.pvoe_outcome_by_category('unexpected','correct')
            # self.avoe_stats.pvoe_outcome_by_category('unexpected','incorrect')
        else:
            # inter
            self.inter_stats.results_summary()
            self.inter_stats.results_scene_classifier()
            self.inter_stats.results_by_scene_type()
            self.inter_stats.results_by_scene_type_and_cube_id()
            print('')
    