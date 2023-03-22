import os


def get_osu_name(file):
    file = file.replace('eval_6_level2_opics-v2-p2_interactive_','')
    parts = file.split('_')
    type = parts[0]
    test = parts[1]
    scene_num = parts[2]
    return f'{type}_{test}_{scene_num}'

def is_correct(dir, file):
    path = os.path.join(dir, file)
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '; RESULT ; True ;' in line:
                return True
        return False

# eval_6_level2_opics-v2-p2_interactive_solidity_0002_01_20230321-195044_log.txt
if __name__ == '__main__':
    dir = '/home/jedirv/Downloads/opics-validation-2-run-log'
    files = os.listdir(dir)
    result_counts = {}
    for file in files:
        osu_name = get_osu_name(file)
        scene_type = osu_name.split('_')[0]
        if not scene_type in result_counts:
            result_counts[scene_type] = {}
            result_counts[scene_type]['correct'] = []
            result_counts[scene_type]['incorrect'] = []
        if is_correct(dir, file):
            result_counts[scene_type]['correct'].append(osu_name)
        else:
            result_counts[scene_type]['incorrect'].append(osu_name)

    
    for scene_type in result_counts:
        print(f'{scene_type} correct: {len(result_counts[scene_type]["correct"])}')
        print(f'{scene_type} incorrect: {len(result_counts[scene_type]["incorrect"])}')
        total = len(result_counts[scene_type]["correct"]) + len(result_counts[scene_type]["incorrect"])
        percent = 100 * (len(result_counts[scene_type]["correct"]) / total)
        print(f'{scene_type} percent correct: {percent}')
        print(f'scenes correct:')
        for scene in result_counts[scene_type]['correct']:
            print(f'\t{scene}')
        print(f'scenes incorrect:')
        for scene in result_counts[scene_type]['incorrect']:
            print(f'\t{scene}')
            