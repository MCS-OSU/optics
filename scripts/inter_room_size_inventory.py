from opics.common.logging.log_constants import abbrev_types
import os
import json

widths = []
depths = []
def is_too_big_dimension_sum(path, limit):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    width = int(data['roomDimensions']['x'])
    depth = int(data['roomDimensions']['z'])
    
    if width + depth > limit:
        return True
    else:
        return False

def is_too_big_dimension(path, limit):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    width = int(data['roomDimensions']['x'])
    depth = int(data['roomDimensions']['z'])
    
    if width > limit or depth > limit:
        return True
    else:
        return False

def is_scene_too_big_area(path, area_limit):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    width = int(data['roomDimensions']['x'])
    depth = int(data['roomDimensions']['z'])
    widths.append(width)
    depths.append(depth)
    area = width * depth
    if area <= area_limit:
        return False
    else:
        return True

if __name__ == '__main__':
    #for limit in range(50, 70):
    #for limit in range(25,35):
    for limit in range(1073,1074):
        if 1 == (limit%2):
            continue
        counts = {}
        print('')
        print('')
        print(f'with limit {limit}...')
        inter_root = '/home/ubuntu/eval6_systest/inter/test_sets/eval5_weighted'
        files = os.listdir(inter_root)
        for fname in files:
            if not 'smoke' in fname:
                test_set_path = os.path.join(inter_root, fname)
                f = open(test_set_path,'r')
                lines = f.readlines()
                f.close()
                for rel_path in lines:
                    scene_name = os.path.basename(rel_path).split('.')[0]
                    path = os.path.join('/home/ubuntu/eval6_systest', rel_path.rstrip())
                    parts = scene_name.split('_')
                    scene_type = parts[0]
                    if scene_type in ['ramps','tool','lava','holes']:
                        
                        cube = parts[4]
                        type_with_cube = scene_type + ' ' + cube
                        if not type_with_cube in counts:
                            counts[type_with_cube] = {}
                            counts[type_with_cube]['ok'] = 0
                            counts[type_with_cube]['too_big'] = 0
                        too_big = is_scene_too_big_area(path, limit)
                        if too_big:
                            counts[type_with_cube]['too_big'] += 1
                        else:
                            counts[type_with_cube]['ok'] += 1

        for type_with_cube in counts:
            total = counts[type_with_cube]["ok"] + counts[type_with_cube]["too_big"]
            print(f'{type_with_cube}  {total} ok: {counts[type_with_cube]["ok"]}   too big: {counts[type_with_cube]["too_big"]}')

        width_hist = {}
        depth_hist = {}
        depths_unique = []
        widths_unique = []
        for w in widths:
            if not w in width_hist:
                width_hist[w] = 0
                widths_unique.append(w)
            width_hist[w] += 1
        for d in depths:
            if not d in depth_hist:
                depth_hist[d] = 0
                depths_unique.append(d)
            depth_hist[d] += 1

        depths_unique = sorted(depths_unique)
        widths_unique = sorted(widths_unique)
        print('WIDTH HIST')
        for w in range(25,51):
            if w in width_hist:
                print(f'{w} {width_hist[w]}')
            else:
                print(f'{w} 0')

        print('DEPTH HIST')
        for d in range(25, 51):
            if d in depth_hist:
                print(f'{d} {depth_hist[d]}')
            else:
                print(f'{d} 0')

        # for scene_type in ['ramps','tool','lava','holes']:
        #     scene_root = os.path.join(inter_root, scene_type)
        #     files = os.listdir(scene_root)
        #     good_count = 0
        #     too_big_count = 0
        #     for fname in files:
        #         path = os.path.join(scene_root, fname)
        #         f = open(path, 'r')
        #         data = json.load(f)
        #         f.close()
        #         width = int(data['roomDimensions']['x'])
        #         depth = int(data['roomDimensions']['z'])
        #         area = width * depth
        #         #if width <= 25 and depth <= 25:
        #         if area <= (limit * limit):
        #             good_count += 1
        #         else:
        #             too_big_count += 1

        #     print(f'{scene_type} ok {good_count}     too big {too_big_count}')
