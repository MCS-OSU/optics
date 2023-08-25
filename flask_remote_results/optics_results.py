from flask import Flask, render_template, url_for
from flask_remote_results.ec2_results import EC2DResults
import os

app = Flask(__name__)
print(f' app.instance_path = {app.instance_path}')
print(f' app.root_path = {app.root_path}')

@app.route("/")
def hello_world():
    return "<h1>Optics Results List</h1>"

@app.route("/<string:proj>")
def show_project_runs(proj):
    if not proj in ['avoe', 'pvoe', 'inter']:
        return f'ERROR:  project must be one of avoe, pvoe, inter'
    ec2d = EC2DResults(proj)
    specs_as_lines = ec2d.get_specs_for_project()
    s = make_links_from_list(f'{proj}', specs_as_lines)
    return s


@app.route("/<string:proj>/<string:spec_name>")
def show_spec_types(proj, spec_name):
    ec2d = EC2DResults(proj)
    types = ec2d.get_types_for_run(spec_name)
    rel_path = f'{proj}/{spec_name}'
    s = make_links_from_list(rel_path, types)
    return s

# @app.route("/<string:proj>/<string:spec_name>")
# def show_project_run_dirs(proj, spec_name):
#     if proj == 'inter':
#         dirs = ['logs','stdout_logs','videos']
#     else:
#         dirs = ['logs','stdout_logs']
#     rel_path = f'{proj}/{spec_name}'
#     s = make_links_from_list(rel_path, dirs)
#     return s


@app.route("/<string:proj>/<string:spec_name>/<string:scene_type>")
def show_log_scene_types(proj, spec_name, scene_type):
    ec2d = EC2DResults(proj)
    proj_rel_path = f'{spec_name}/stdout_logs/{scene_type}'
    stdout_logfile_names = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
    
    scene_names = get_scene_names_from_filenames(stdout_logfile_names, '_stdout.txt')
    url_path =  f'{spec_name}/{scene_type}'
    s = make_links_from_list(f'{proj}/{url_path}', scene_names)
    return s

# @app.route("/<string:proj>/<string:spec_name>/logs")
# def show_log_scene_types(proj, spec_name):
#     ec2d = EC2DResults(proj)
#     proj_rel_path = f'{spec_name}/logs'
#     log_scene_types = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
#     s = make_links_from_list(f'{proj}/{proj_rel_path}', log_scene_types)
#     return s

# @app.route("/<string:proj>/<string:spec_name>/stdout_logs")
# def show_stdout_log_scene_types(proj, spec_name):
#     ec2d = EC2DResults(proj)
#     proj_rel_path = f'{spec_name}/stdout_logs'
#     stdout_log_scene_types = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
#     s = make_links_from_list(f'{proj}/{proj_rel_path}', stdout_log_scene_types)
#     return s

# @app.route("/<string:proj>/<string:spec_name>/videos")
# def show_videos_scene_types(proj, spec_name):
#     ec2d = EC2DResults(proj)
#     proj_rel_path = f'{spec_name}/videos'
#     videos_scene_types = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
#     s = make_links_from_list(f'{proj}/{proj_rel_path}', videos_scene_types)
#     return s

# @app.route("/<string:proj>/<string:spec_name>/<string:log_type>/<string:scene_type>")
# def show_log_list_for_scene_types(proj, spec_name, log_type, scene_type):
#     if proj == 'inter':
#         if not log_type in ['logs', 'stdout_logs', 'videos']:
#             return f'ERROR:  log_type must be one of logs, stdout_logs, videos'
#     else:
#         if not log_type in ['logs', 'stdout_logs']:
#             return f'ERROR:  log_type must be one of logs, stdout_logs'
#     ec2d = EC2DResults(proj)
#     proj_rel_path = f'{spec_name}/{log_type}/{scene_type}'
#     logs = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
#     s = make_links_from_list(f'{proj}/{proj_rel_path}', logs)
#     return s

# @app.route("/<string:proj>/<string:spec_name>/<string:log_type>/<string:scene_type>/<string:log_name>")
# def show_log(proj, spec_name, log_type, scene_type, log_name):
#     ec2d = EC2DResults(proj)
#     proj_rel_path        = f'{spec_name}/{log_type}/{scene_type}/{log_name}'
#     proj_rel_parent_path = f'{spec_name}/{log_type}/{scene_type}'
#     if log_name.endswith('.mp4'):
#         url_rel_video_path = ec2d.retrieve_video(proj_rel_parent_path, proj_rel_path)
#         url = url_for('static',filename=url_rel_video_path)
#         s = f'<video width="960" height="720" controls><source src="{url}" type="video/mp4"></video>'
#         return s
#     else:
#         s = ec2d.get_file_contents_for_rel_path(proj_rel_path)
#         return f'<span style="white-space:pre-wrap;font-family:\'Courier New\'">\n{s}\n</span>'


@app.route("/<string:proj>/<string:spec_name>/<string:scene_type>/<string:scene_name>")
def show_result(proj, spec_name, scene_type, scene_name):
    ec2d = EC2DResults(proj)
    # all rel_paths are relative to the project dir
    scene_log_rel_path = f'{spec_name}/logs/{scene_type}/{scene_name}.log'
    scene_log_content = ec2d.get_file_contents_for_rel_path(scene_log_rel_path)

    stdout_log_rel_path = f'{spec_name}/stdout_logs/{scene_type}/{scene_name}_stdout.txt'
    stdout_log_content = ec2d.get_file_contents_for_rel_path(stdout_log_rel_path)
    if proj == 'inter':
        video_parent_rel_path = f'{spec_name}/videos/{scene_type}'
        video_rel_path        = f'{spec_name}/videos/{scene_type}/{scene_name}_visual.mp4'
        url_rel_video_path = ec2d.retrieve_video(video_parent_rel_path, video_rel_path)
        if url_rel_video_path is None:
            return render_template('inter_result.html', scene_name=scene_name, scene_log_content=scene_log_content, stdout_log_content=stdout_log_content, video_url=None)
        else:
            video_url = url_for('static',filename=url_rel_video_path)
            print(f'video_url={video_url}')
            return render_template('inter_result.html', scene_name= scene_name, scene_log_content=scene_log_content, stdout_log_content=stdout_log_content, video_url=video_url)
    else:
        return render_template('result.html', scene_name= scene_name, scene_log_content=scene_log_content, stdout_log_content=stdout_log_content)



    #return f'<span style="white-space:pre-wrap;font-family:\'Courier New\'">\n{specs}\n</span>'
def get_scene_names_from_filenames(filenames, suffix_to_remove):
    result = []
    for filename in filenames:
        scene_name = filename.replace(suffix_to_remove, '')
        result.append(scene_name)
    return result

def make_links_from_list(rel_path, list):
    s = ''
    for item in list:
        s += f'<a href="http://localhost:5000/{rel_path}/{item}">{item}</a><br>'
    return s


if __name__ == '__main__':
    app.run(debug=True)

