import sys
import os
from pathlib import Path
from opics_common.scene_type.type_constants import formal_type
from opics_common.opics_logging.opics_logs import OpicsLogs
from opics_common.opics_logging.stdout_logs import StdoutLogs
from opics_common.results.stats_output import stats_title
from opics_common.results.stats_pvoe import StatsPvoe
from opics_common.results.stats_avoe import StatsAvoe
from opics_common.results.stats_inter import StatsInter
from opics_common.results.avoe_pairs import AvoePairs
from core.optics_dirs import SystestDirectories
from core.test_register import TestRegisterLocal
from optics_results.scene_state_histories import SceneStateHistories

class OpticsScores:
    def __init__(self, proj, optics_spec):
        self.proj = proj
        self.optics_spec = optics_spec
        self.systest_dirs = SystestDirectories(str(Path.home()), self.optics_spec)
        self.scene_state_histories = SceneStateHistories(self.systest_dirs)
        self.test_register = TestRegisterLocal(self.systest_dirs)
        self.proj_log_dir = self.systest_dirs.result_logs_dir
        self.proj_stdout_log_dir = self.systest_dirs.stdout_logs_dir

        if 'OPTICS_HOME' not in os.environ:            
            print('')
            print("      ERROR - OPTICS_HOME not defined.  Please 'export OPTICS_HOME=<parent_of_opics_dir>'")
            print('')
            sys.exit()

        self.stdout_logs = StdoutLogs()
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
            for scene_type in formal_type:
                type_dir = os.path.join(self.proj_stdout_log_dir, scene_type)
                if os.path.exists(type_dir):
                    files = os.listdir(type_dir)
                    #print(type_dir)
                    for file in files:
                        filepath = os.path.join(type_dir, file)
                        #print(f'log file {filepath}')
                        if os.path.isfile(filepath):
                            # print(f'file:  {filepath}')
                            self.stdout_logs.load_file(filepath, proj, scene_type)
        else:
            self.inter_stats = StatsInter(self.opics_logs,'inter')
    
    def get_all_scene_types_in_play(self, logs_for_scene_types, other_logs_for_scene_types):
        all_types = []
        all_types.extend(logs_for_scene_types)
        for scene_type in other_logs_for_scene_types:
            if not scene_type in all_types:
                all_types.append(scene_type)
        return sorted(all_types)

    def show_totals_diff(self, other_run_scores):
        other_scores_logs_for_scene_types = other_run_scores.opics_logs.logs[self.proj]
        proj_logs_for_scene_types = self.opics_logs.logs[self.proj]
        print(f'comparing    {self.optics_spec.config_name}   and   {other_run_scores.optics_spec.config_name}')
        all_scene_types_in_play = self.get_all_scene_types_in_play(proj_logs_for_scene_types, other_scores_logs_for_scene_types)
        for scene_type in all_scene_types_in_play:
            if scene_type in other_scores_logs_for_scene_types and scene_type in proj_logs_for_scene_types:
                self.show_comparison_report_for_scene_type(scene_type, other_run_scores)
            elif not(scene_type in other_scores_logs_for_scene_types) and scene_type in proj_logs_for_scene_types:
                self.show_this_run_report_for_scene_type(scene_type)
            else:
                self.show_other_run_report_for_scene_type(scene_type, other_run_scores)

    def get_value_change(self, pc, pc_other, label):
        if pc == pc_other:
            return f'{label}'
        if pc > pc_other:
            return f'-{pc - pc_other} {label}'
        else:
            return f'+{pc_other - pc} {label}'

    def show_other_run_report_for_scene_type(self, other_run_scores):
        ol = other_run_scores.opics_logs
        o_total       = ol.get_count_for_proj_scene(proj,scene_type)
        o_unknowns    = ol.count_results_unknown(proj,scene_type)
        o_fails       = ol.count_results_fail(proj,scene_type)
        o_successes   = ol.count_results_successes(proj,scene_type)
        o_exceptions  = ol.count_results_exceptions(proj,scene_type)
        pc_other = int((float(o_successes) / float(o_total)) * 100)

        print(f'')
        print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(o_total).ljust(10)} total')
        if successes != 0 or o_successes != 0:
            print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(o_successes).ljust(10)} success')
        if fails != 0 or o_fails != 0:
            print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(o_fails).ljust(10)} fails')
        if exceptions != 0 or o_exceptions != 0:
            print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(o_exceptions).ljust(10)} exception')
        if unknowns != 0 or o_unknowns != 0:
            print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(o_unknowns).ljust(10)} unknown')
        print(f'{scene_type.ljust(14)}   {" ".ljust(10)}{str(pc_other).ljust(10)} %')

    def show_this_run_report_for_scene_type(self, scene_type):
        proj = self.proj
        total = self.opics_logs.get_count_for_proj_scene(proj,scene_type)
        unknowns = self.opics_logs.count_results_unknown(proj,scene_type)
        fails    = self.opics_logs.count_results_fail(proj,scene_type)
        successes= self.opics_logs.count_results_successes(proj,scene_type)
        exceptions = self.opics_logs.count_results_exceptions(proj,scene_type)
        pc = int((float(successes) / float(total)) * 100)

        print(f'')
        print(f'{scene_type.ljust(14)}   {str(total).ljust(10)}{" ".ljust(10)} total')
        if successes != 0:
            print(f'{scene_type.ljust(14)}   {str(successes).ljust(10)}{" ".ljust(10)} success')
        if fails != 0:
            print(f'{scene_type.ljust(14)}   {str(fails).ljust(10)}{" ".ljust(10)} fails')
        if exceptions != 0:
            print(f'{scene_type.ljust(14)}   {str(exceptions).ljust(10)}{" ".ljust(10)} exception')
        if unknowns != 0:
            print(f'{scene_type.ljust(14)}   {str(unknowns).ljust(10)}{" ".ljust(10) } unknown')
        print(f'{scene_type.ljust(14)}   {str(pc).ljust(10)}{" ".ljust(10)} %')

    def show_comparison_report_for_scene_type(self, scene_type, other_run_scores):
        proj = self.proj
        other = other_run_scores
        total = self.opics_logs.get_count_for_proj_scene(proj,scene_type)
        unknowns = self.opics_logs.count_results_unknown(proj,scene_type)
        fails    = self.opics_logs.count_results_fail(proj,scene_type)
        successes= self.opics_logs.count_results_successes(proj,scene_type)
        exceptions = self.opics_logs.count_results_exceptions(proj,scene_type)
        #print(f' {scene_type} \ttotal{total} \tsuccess{successes}  \tfails {fails} \texcep {exceptions} \tunknowns {unknowns}')
        ol = other_run_scores.opics_logs
        o_total       = ol.get_count_for_proj_scene(proj,scene_type)
        o_unknowns    = ol.count_results_unknown(proj,scene_type)
        o_fails       = ol.count_results_fail(proj,scene_type)
        o_successes   = ol.count_results_successes(proj,scene_type)
        o_exceptions  = ol.count_results_exceptions(proj,scene_type)
        #print(f' {scene_type} \ttotal{o_total} \tsuccess{o_successes}  \tfails {o_fails} \texcep {o_exceptions} \tunknowns {o_unknowns}')
        
        pc = int((float(successes) / float(total)) * 100)
        pc_other = int((float(o_successes) / float(o_total)) * 100)
        pc_delta = self.get_value_change(pc,         pc_other,      '%')
        t_delta  = self.get_value_change(total,      o_total,       'total')
        s_delta  = self.get_value_change(successes,  o_successes,   'success')
        f_delta  = self.get_value_change(fails,      o_fails,       'fail')
        e_delta  = self.get_value_change(exceptions, o_exceptions,  'exception')
        u_delta  = self.get_value_change(unknowns,   o_unknowns,    'unknown')
        print(f'')
        print(f'{scene_type.ljust(14)}   {str(total).ljust(10)}{str(o_total).ljust(10)}{t_delta}')
        if successes != 0 or o_successes != 0:
            print(f'{scene_type.ljust(14)}   {str(successes).ljust(10)}{str(o_successes).ljust(10)}{s_delta}')
        if fails != 0 or o_fails != 0:
            print(f'{scene_type.ljust(14)}   {str(fails).ljust(10)}{str(o_fails).ljust(10)}{f_delta}')
        if exceptions != 0 or o_exceptions != 0:
            print(f'{scene_type.ljust(14)}   {str(exceptions).ljust(10)}{str(o_exceptions).ljust(10)}{e_delta}')
        if unknowns != 0 or o_unknowns != 0:
            print(f'{scene_type.ljust(14)}   {str(unknowns).ljust(10)}{str(o_unknowns).ljust(10)}{u_delta}')
        print(f'{scene_type.ljust(14)}   {str(pc).ljust(10)}{str(pc_other).ljust(10)}{pc_delta}')

    def show_details_diff(self, other_run_scores):
        other_scores_logs_for_scene_types = other_run_scores.opics_logs.logs[self.proj]
        proj_logs_for_scene_types = self.opics_logs.logs[self.proj]
        print(f'comparing    {self.optics_spec.config_name}   and   {other_run_scores.optics_spec.config_name}')
        for scene_type in proj_logs_for_scene_types:
            if scene_type in other_scores_logs_for_scene_types:
                self.show_totals_report_for_scene_type(scene_type, other_run_scores)


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
            # self.avoe_stats.results_summary()
            # self.avoe_stats.results_by_scene_type()
            # self.avoe_stats.results_expected_by_scene_type()
            # self.avoe_stats.results_unexpected_by_scene_type()
            # self.avoe_stats.results_noexpectation_by_scene_type()

            pairs = AvoePairs(self.stdout_logs)
            pairs.results_pairwise_by_scene_type()
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

        self.test_register.gather_do_types_from_spec(self.optics_spec.types_to_run)
        completed_scene_count = self.test_register.get_completed_scene_count()
        active_scenes = self.test_register.gather_active_scene_state_paths()
        percent = int((float(completed_scene_count) / float(len(active_scenes)) ) * 100)
        print('')
        print(f' <<<  {completed_scene_count} completed out of {len(active_scenes)} scenes specified to run in optics spec {percent}%  >>>')
    