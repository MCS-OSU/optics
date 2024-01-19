
from optics_results.scene_state_histories import SceneStateHistories
from core.optics_dirs import SystestDirectories
from core.optics_spec_loader import OpticsSpec

def resolve_given_optics_spec_path(given_path):
    if given_path.startswith('/'):
        return given_path
    return os.path.join(os.getcwd(), given_path)
    
 
def usage():
    print("python reset_hung_optics_scenes.py <proj> <spec_path> <scene_name>|*")

def propose_reset_for_scene(systest_dirs, scene_path, proj, optics_spec)
    scene_fname = os.basename(scene_path)
    scene_name = scene_fname.split(','[0])
    sshs = SceneStateHistories(systest_dirs)
    ssh = sshs.histories[scene_name]
    print(f'current state of scene {scene_name}')
    ssh.print()
    answer = input('reset this scene? y/n')
    if answer.lower() == 'y':
        optics_scores = OpticsScores(proj,optics_spec)
        scene_type = scene_name.split['_'][0]
        scene_logs = optics_scores.opics_logs.logs[proj][scene_type]
        for scene_log in scene_logs:
            if scene_log.scene_name == scene_name:
                scene_log.delete()
        optics_scores.stdout_logs.
        ssh.reset()


def find_hung_scenes(systest_dirs)
    sshs = SceneStateHistories(systest_dirs)
    ssh = ssh.histories

if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
        sys.exit()

    proj = sys.argv[1]
    if not proj in ['avoe', 'pvoe', 'inter']
        print(f'project must be avie, inter, or pvoe')
        usage()
        sys.exit()

    spec_path = sys.argv[2]
    optics_spec_path = resolve_given_optics_spec_path(spec_path)
    if not os.path.isfile(optics_spec_path):
        print(f'specified optics_spec not found')
    
    
    optics_spec = OpticsSpec(optics_spec_path)
    systest_dirs = SystestDirectories(home_dir, optics_spec)
    

    scope = sys.argv[3]
    if scope == '*':
        print('not yet implemented')
        #find_hung_scenes(systest_dirs)
    else:
        scene_path = get_scene_path_for_scene(scope)
        if scene_path == 'None':
            print(f'Could not find the scene named {scope}')
        else:
            propose_reset_for_scene(systest_dirs, scene_path, proj, optics_spec)

