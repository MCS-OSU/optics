


def get_keys_as_tuples(some_dict):
    key_list = []
    for key in some_dict.keys():
        key_list.append(key)
    key_list.sort()
    key_tuples = []
    for key in key_list:
        key_tuples.append((key, key))
    return key_tuples


def get_view_names():
    return ['scores','status','report','scene result']

def remove_warning_lines(s):
    lines = s.split('\n')
    new_lines = []
    for line in lines:
        if 'WARNING' not in line and 'had None for score' not in line:
            new_lines.append(line)
            print(line)
    return '\n'.join(new_lines)
    