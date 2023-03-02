import os
import opics_common.opics_logging.log_constants as log_constants
from datetime import datetime

pvoe_plausible_string    = 'plausible'
pvoe_implausible_string  = 'implausible'

def create_bogus_logfile(log_dir, scene_path, results_format, scene_correct=True):
    if results_format == 'avoe':
        return create_bogus_logfile_avoe(log_dir, scene_path, scene_correct)
    elif results_format == 'pvoe':
        return create_bogus_logfile_pvoe(log_dir, scene_path, scene_correct)
    elif results_format == 'inter':
        return create_bogus_logfile_inter(log_dir, scene_path, scene_correct)
    else:
        raise Exception(f'ERROR - unknown results_format {results_format}')
    

def write_log(log_name_root, log_dir, lines):
    current_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    log_name = f'{log_name_root}__{current_time}.txt'
    log_path = os.path.join(log_dir, log_name)
    with open(log_path, 'w') as f:
        for line in lines:
            f.write(line+ '\n')
    return log_path


def create_bogus_logfile_avoe(log_dir, scene_path, scene_correct=True):
    # 2022-07-11 16:58:39,683 ; INFO ; root ; SCENE_START ; eval5_validation_avoe_effic_irrat_0001_01_unexpected ; scene_type_not_recognized_to_lookup_formal_name
    # 2022-07-11 17:14:56,063 ; INFO ; root ; RESULT ; eval5_validation_avoe_effic_irrat_0001_01_unexpected ; unexpected
    # 2022-07-11 17:14:56,064 ; INFO ; root ; SCORE ; eval5_validation_avoe_effic_irrat_0001_01_unexpected ; rating:4.045076238834177e-05 ; score:0.364754269742797
    # assume its a scene with answer 'expected'
    fname_root = os.path.basename(scene_path).split('.')[0] 
    if scene_correct:
        answer = log_constants.avoe_expected_string
    else:
        answer = log_constants.avoe_unexpected_string
    lines = []
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["scene_start"]} ; {fname_root} ; bl_barr')
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["result"]} ; {fname_root} ; {answer} ; steps:0')
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["score"]} ; {fname_root} ; {log_constants.avoe_rating_string}:4.04 ; {log_constants.avoe_score_string}:0.36')
    return write_log(fname_root, log_dir, lines)
    


def create_bogus_logfile_pvoe(log_dir, scene_path, scene_correct=True):
    # 2022-07-18 18:43:20,126 ; INFO ; root ; SCENE_START ; eval_5_validation_passive_coll_0001_01_plaus ; collision
    # 2022-07-18 18:45:47,672 ; INFO ; root ; SCORE ; eval_5_validation_passive_coll_0001_01_plaus ; rating:0.0 ; score:0.4395565706996697
    # 2022-07-18 18:45:47,673 ; INFO ; root ; RESULT ; eval_5_validation_passive_coll_0001_01_plaus ; implausible
    fname_root = os.path.basename(scene_path).split('.')[0] 
    if scene_correct:
        answer = pvoe_plausible_string
    else:
        answer = pvoe_implausible_string

    lines = []
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["scene_start"]} ; {fname_root} ; coll')
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["score"]} ; {fname_root} ; {log_constants.pvoe_rating_string}:5.05 ; {log_constants.pvoe_score_string}:0.76')
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["result"]} ; {fname_root} ; {answer}')
    return write_log(fname_root, log_dir, lines)

def create_bogus_logfile_inter(log_dir, scene_path, scene_correct=True):
    # 2022-07-18 23:28:40,911 ; INFO ; root ; SCENE_START ; eval_5_validation_interactive_agent_identification_0001_03 ; agent_identification
    # 2022-07-18 23:29:35,400 ; INFO ; root ; RESULT ; eval_5_validation_interactive_agent_identification_0001_03 ; succeeded ; steps:0
    fname_root = os.path.basename(scene_path).split('.')[0]
    if scene_correct:
        success = log_constants.inter_succeeded_string
    else:
        success = log_constants.inter_failed_string
    lines = []
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["scene_start"]} ; {fname_root} ; suprel')
    lines.append(f'time ; INFO ; root ; {log_constants.line_flag["result"]} ; {fname_root} ; {success} ; steps:0')
    return write_log(fname_root, log_dir, lines)
