
import os
import sys
import argparse
import traceback
import json

container_for_project = {}
container_for_project['avoe' ] = '???.sif'
container_for_project['inter'] = '???.sif'
container_for_project['pvoe' ] = 'pvoe_040123_eval5_cuda_11.sif'

    
def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', default='undefined')
    #parser.add_argument('--log_dir', default='logs')
    return parser


def get_proj_for_json_scene_category(json_scene_category):
    if json_scene_category == "intuitive physics":
        return 'pvoe'
    elif json_scene_category == 'agents':
        return 'avoe'
    elif json_scene_category in ['retrieval', 'imitation','multi retrieval', 'passive']:
        return 'inter'
    else:
        raise Exception(f'unkown json_scene_category: {json_scene_category}')


def get_scene_type_from_scene_file(path):
    f = open(path, 'r')
    scene_json = json.load(f)
    f.close()
    return  scene_json['goal']['category']


def usage():
    print('usage:  python opics_eval6_run_scene.py --scene <scene_path>')
    
if __name__ == '__main__':
    
    args  = make_parser().parse_args()
    
    scene_path = args.scene
    if not os.path.isfile(scene_path):
        print(f'ERROR given scene path {scene_path} does not exist')
        usage()
        sys.exit()
        
    if not scene_path.endswith('.json'):
        print(f'ERROR given scene path {scene_path} is not a json file')
        usage()
        sys.exit()
    
    print(f'scene path given : {scene_path}')
    #log_dir = args.log_dir
    scene_name = os.path.basename(scene_path).split('.')[0]
    json_scene_category = get_scene_type_from_scene_file(scene_path)
    proj = get_proj_for_json_scene_category(json_scene_category)
    os.makedirs('logs', exist_ok=True)

    containers_dir = '/home/ubuntu/containers'
    container_fname = container_for_project[proj]
    container_path = os.path.join(containers_dir, container_fname)
    print(f'container_path is {container_path}')
    cmd = f'apptainer run --nv {container_path} run_opics_scene {scene_path} 2>&1 | tee -a logs/{scene_name}_stdout.log'
    try:
        os.system(cmd)
    except Exception as err:
        traceback.print_exc()
        sys.exit()
    