import sys
import os
from pathlib import Path
from opics.common.logging.stats_output  import stats_title
from opics.common.logging.log_constants import formal_type
from opics.common.logging.opics_logs    import OpicsLogs
from opics.common.logging.stats_pvoe    import StatsPvoe
from opics.common.logging.stats_avoe    import StatsAvoe
from opics.common.logging.stats_inter   import StatsInter
from core.optics_spec_loader            import OpticsSpec

from core.optics_dirs import SystestDirectories


def usage():
    print('python results_reader.py spec_path')


if __name__ == "__main__":
    if not 'OPICS_HOME' in os.environ:
        print('')
        print("      ERROR - OPICS_HOME not defined.  Please 'export OPICS_HOME=<parent_of_opics_dir>'")
        print('')
        sys.exit()

    if len(sys.argv) < 2:
        usage()
        sys.exit()

    # if sys.argv[1] not in ['avoe', 'pvoe', 'inter']:
    #     usage()
    #     sys.exit()

    optics_spec_path = sys.argv[1]
    optics_spec = OpticsSpec(optics_spec_path)
    
    systest_dirs = SystestDirectories(str(Path.home()), optics_spec) 
    proj_log_dir = systest_dirs.result_logs_dir
    proj = optics_spec.proj
    
    opics_logs = OpicsLogs()
    for scene_type in formal_type:    #just look for all types for all projects - those not present will be ignored
        type_dir = os.path.join(proj_log_dir, scene_type)
        if os.path.exists(type_dir):
            files = os.listdir(type_dir)
            print(type_dir)
            for file in files:
                filepath = os.path.join(type_dir, file)
                if os.path.isfile(filepath):
                    print(f'file:  {filepath}')
                    opics_logs.load_file(filepath, proj, scene_type)
    
    if proj == 'pvoe':
        pvoe_stats = StatsPvoe(opics_logs,'pvoe')
    elif proj == 'avoe':
        avoe_stats = StatsAvoe(opics_logs, 'avoe')
    else:
        inter_stats = StatsInter(opics_logs, 'inter')

    
    
    stats_title(proj_log_dir)
    if proj == 'pvoe':
        pvoe_stats.results_summary()
        pvoe_stats.results_by_scene_type()
        pvoe_stats.results_plausible_by_scene_type()
        pvoe_stats.results_implausible_by_scene_type()
        pvoe_stats.results_by_scene_type_and_cube_id()
        #pvoe_stats.compare_results_to_ta2_eval5_runs(systest_dirs.eval5_answer_keys_dir)
        print('')
    
        # pvoe_stats.outcome_by_category('plausible','correct')
        # pvoe_stats.outcome_by_category('plausible','incorrect')
        # pvoe_stats.outcome_by_category('implausible','correct')
        # pvoe_stats.outcome_by_category('implausible','incorrect')
    elif proj == 'avoe':
        avoe_stats.results_summary()
        avoe_stats.results_by_scene_type()
        avoe_stats.results_expected_by_scene_type()
        avoe_stats.results_unexpected_by_scene_type()
        print('')
        # avoe_stats.pvoe_outcome_by_category('expected','correct')
        # avoe_stats.pvoe_outcome_by_category('expected','incorrect')
        # avoe_stats.pvoe_outcome_by_category('unexpected','correct')
        # avoe_stats.pvoe_outcome_by_category('unexpected','incorrect')
    else:
        # inter
        inter_stats.results_summary()
        inter_stats.results_by_scene_type()
        print('')



