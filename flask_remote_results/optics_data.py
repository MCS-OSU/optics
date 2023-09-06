from flask_remote_results.ec2_results import EC2DResults
import json
from utils import get_keys_as_tuples, remove_warning_lines
from flask import jsonify, url_for

class OpticsData():
    def __init__(self):
        
        self.ec2d = EC2DResults()
        self.active_optics_data_json_string = self.ec2d.get_active_optics_data().rstrip()
        self.data = json.loads(self.active_optics_data_json_string)

    def get_most_recent_dated_run(self, proj):
        runs_object = self.data['projects'][proj]
        run_names = runs_object.keys()
        numeric_run_names = []
        for run_name in run_names:
            parts = run_name.split('_')
            if parts[0].isdigit():
                numeric_run_names.append(run_name)
        numeric_run_names.sort()
        return numeric_run_names[-1]

    def get_default_run_for_proj(self, proj):
        most_recent_dated_run = self.get_most_recent_dated_run(proj)
        return most_recent_dated_run

    def get_default_scene_type_for_run(self, proj, run):
        scene_types = self.data['projects'][proj][run].keys()
        scene_type = list(scene_types)[0]
        return scene_type

    def get_default_scene_name_for_type(self, proj, run, scene_type):
        scene_names = sorted(self.data['projects'][proj][run][scene_type]['scene_names'])
        #print(f'scene_names = {scene_names}')
        scene_name = scene_names[0]
        return scene_name


    def get_default_view_selection(self, proj):
        default_run = self.get_default_run_for_proj(proj)
        default_view = 'scores'
        return proj, default_run, default_view
    
    def get_default_scene_type_and_name(self, proj, run):
        default_scene_type = self.get_default_scene_type_for_run(proj, run)
        default_scene_name = self.get_default_scene_name_for_type(proj, run, default_scene_type)
        return default_scene_type, default_scene_name

    def get_run_tuples(self, proj):
        info = self.data['projects']
        run_tuples = get_keys_as_tuples(info[proj])
        return run_tuples


    def get_scene_type_tuples(self, proj, run):
        info = self.data['projects']
        scene_type_tuples = get_keys_as_tuples(info[proj][run])
        return scene_type_tuples


    def get_spec_info_for_proj(self, proj, run):
        specs = self.ec2d.get_specs_for_project(proj)
        specs_list = []
        #print(f'specs = {specs}')
        for spec in specs:
            spec_obj = {}
            spec_obj['id'] = spec
            spec_obj['name'] = spec
            if spec == run:
                spec_obj['selected'] = True
            else:
                spec_obj['selected'] = False
            specs_list.append(spec_obj)
        return specs_list

    def get_json_for_proj_run_view(self, proj, run, view):
        specs_list = self.get_spec_info_for_proj(proj, run)
        if view == 'scores' or view == 'status' or view == 'report':
            content_string = self.ec2d.run_remote_script('', 'optics.py',  view + ' specs/' + proj + '_' + run + '.cfg')
            return jsonify({'specs': specs_list, 'content': content_string})
        elif view == 'scene result':
            # TBD
            return jsonify({'specs': specs_list})

    
    def get_json_for_view(self, proj, run, view):
        if view == 'scores' or view == 'status' or view == 'report':
            content_string = self.ec2d.run_remote_script('', 'optics.py',  view + ' specs/' + proj + '_' + run + '.cfg')
            return jsonify({'content': content_string})
        elif view == 'scene result':
            # not relevant to this context
            return ''

    def get_video_url (self, proj, run, scene_type, scene_name):
        video_parent_rel_path = f'{run}/videos/{scene_type}'
        video_rel_path        = f'{run}/videos/{scene_type}/{scene_name}_visual.mp4'
        url_rel_video_path = self.ec2d.retrieve_video(proj, video_parent_rel_path, video_rel_path)
        if url_rel_video_path is None:
            video_url = None
        else:
            video_url = url_for('static',filename=url_rel_video_path)
        return video_url

    def get_result_info(self, proj,run,scene_type, scene_name):
        info = self.data['projects']
        scene_names = sorted(info[proj][run][scene_type]['scene_names'])
        print(f'scene_names = {scene_names}')
        ec2d = EC2DResults()
        stdout_log_rel_path = f'{run}/stdout_logs/{scene_type}/{scene_name}_stdout.txt'
        log_content = ec2d.get_file_contents_for_rel_path(proj, stdout_log_rel_path)
        video_url = None
        if proj == 'inter':
            video_url = self.get_video_url(proj, run, scene_type, scene_name)
        correctness_info_json_string = ec2d.get_correctness_for_scene_type(proj, run, scene_type)
        correctness_info_json_string = remove_warning_lines(correctness_info_json_string)
        correctness_info = json.loads(correctness_info_json_string)
        return scene_names, log_content, video_url, correctness_info