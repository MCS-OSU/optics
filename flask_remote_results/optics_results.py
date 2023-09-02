from flask import Flask, render_template, url_for, jsonify
from flask_remote_results.ec2_results import EC2DResults
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
import os, json


ec2d = EC2DResults('avoe')
active_optics_data_json_string = ec2d.get_active_optics_data().rstrip()
#print(f'active_optics_data_json_string: {active_optics_data_json_string}')
active_optics_data = json.loads(active_optics_data_json_string)


def get_most_recent_dated_run(runs_object):
    run_names = runs_object.keys()
    numeric_run_names = []
    for run_name in run_names:
        parts = run_name.split('_')
        if parts[0].isdigit():
            numeric_run_names.append(run_name)
    numeric_run_names.sort()
    return numeric_run_names[-1]

def get_default_run_for_proj(proj):
    most_recent_dated_run = get_most_recent_dated_run(active_optics_data['projects'][proj])
    return most_recent_dated_run

def get_default_scene_type_for_run(proj, run):
    scene_types = active_optics_data['projects'][proj][run].keys()
    scene_type = list(scene_types)[0]
    return scene_type

def get_default_scene_name_for_type(proj, run, scene_type):
    scene_names = active_optics_data['projects'][proj][run][scene_type]
    scene_name = scene_names[0]
    return scene_name

def get_default_view_selection():
    proj = 'inter'
    default_run = get_default_run_for_proj(proj)
    default_view = 'scores'
    return proj, default_run, default_view

def get_default_selections_for_project(proj):
    default_run = get_default_run_for_proj(proj)
    default_scene_type = get_default_scene_type_for_run(proj, default_run)
    default_scene_name = get_default_scene_name_for_type(proj, default_run, default_scene_type)
    return proj, default_run, default_scene_type, default_scene_name

def get_default_scene_type_and_name(proj, run):
    default_scene_type = get_default_scene_type_for_run(proj, run)
    default_scene_name = get_default_scene_name_for_type(proj, run, default_scene_type)
    return default_scene_type, default_scene_name


def get_keys_as_tuples(some_dict):
    key_list = []
    for key in some_dict.keys():
        key_list.append(key)
    key_list.sort()
    key_tuples = []
    for key in key_list:
        key_tuples.append((key, key))
    return key_tuples

def get_list_items_as_tuples(list_object):
    list_tuples = []
    list_object.sort()
    for item in list_object:
        print(f' adding item {item} to list_tuples')
        list_tuples.append((item, item))
    return list_tuples

def get_view_names():
    return ['scores','status','report','scene_result']

def get_populated_view_form(proj, run, view_choice):
    f = ViewSelectForm()
    f.project_select.choices = ['avoe', 'inter','pvoe']
    f.project_select.default = proj

    info = active_optics_data['projects']

    run_tuples = get_keys_as_tuples(info[proj])
    f.run_select.choices = run_tuples

    f.view_select.choices = get_view_names()
    return f

def get_run_tuples(proj):
    info = active_optics_data['projects']
    run_tuples = get_keys_as_tuples(info[proj])
    return run_tuples

def get_scene_type_tuples(proj, run):
    info = active_optics_data['projects']
    scene_type_tuples = get_keys_as_tuples(info[proj][run])
    return scene_type_tuples

def get_scene_name_tuples(proj, run, scene_type):
    info = active_optics_data['projects']
    scene_name_tuples = get_list_items_as_tuples(info[proj][run][scene_type])
    return scene_name_tuples

# def get_populated_form(proj, run, scene_type, scene_name):
#     rsf = ResultSelectForm()
#     rsf.project_select.choices    = ['avoe', 'inter','pvoe']
#     rsf.run_select.choices        = get_run_tuples(proj)
#     rsf.scene_type_select.choices = get_scene_type_tuples(proj, run)
#     rsf.scene_name_select.choices = get_scene_name_tuples(proj, run, scene_type)
#     return rsf

def get_populated_scene_result_form_for_proj(proj):
    srf = SceneResultForm()
    srf.project_select.choices    = ['avoe', 'inter','pvoe']
    srf.run_select.choices        = get_run_tuples(proj)
    srf.view_select.choices       = get_view_names()
    default_run = get_default_run_for_proj(proj)
    srf.scene_type_select.choices = get_scene_type_tuples(proj, default_run)
    return srf

def get_populated_scene_result_form_for_run(proj, run):
    srf = SceneResultForm()
    srf.project_select.choices    = ['avoe', 'inter','pvoe']
    srf.run_select.choices        = get_run_tuples(proj)
    srf.view_select.choices       = get_view_names()
    srf.scene_type_select.choices = get_scene_type_tuples(proj, run)
    return srf



def get_spec_info_for_proj(proj, run):
    ec2d = EC2DResults(proj)
    specs = ec2d.get_specs_for_project()
    specs_list = []
    print(f'specs = {specs}')
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

def get_json_for_proj_run_view(proj, run, view):
    specs_list = get_spec_info_for_proj(proj, run)
    ec2d = EC2DResults(proj)
    if view == 'scores' or view == 'status' or view == 'report':
        content_string = ec2d.run_remote_script('', 'optics.py',  view + ' specs/' + proj + '_' + run + '.cfg')
        return jsonify({'specs': specs_list, 'content': content_string})
    elif view == 'scene_result':
        # TBD
        return jsonify({'specs': specs_list})

def get_json_for_view(proj, run, view):
    ec2d = EC2DResults(proj)
    if view == 'scores' or view == 'status' or view == 'report':
        content_string = ec2d.run_remote_script('', 'optics.py',  view + ' specs/' + proj + '_' + run + '.cfg')
        return jsonify({'content': content_string})
    elif view == 'scene_result':
        # TBD
        return ''

class ViewSelectForm(FlaskForm):
    project_select    = SelectField('Project',    choices = [])
    run_select        = SelectField('Run',        choices = [])
    view_select       = SelectField('View',       choices = [])
    content           = TextAreaField('Content',  render_kw={"rows": 20, "cols": 100})

class ResultSelectForm(FlaskForm):
    
    project_select    = SelectField('Project',    choices = [])
    run_select        = SelectField('Run',        choices = [])
    scene_type_select = SelectField('Scene Type', choices = [])
    scene_name_select = SelectField('Scene Name', choices = [])

class SceneResultForm(FlaskForm):
    project_select    = SelectField('Project',    choices = [])
    run_select        = SelectField('Run',        choices = [])
    view_select       = SelectField('View',       choices = [])
    scene_type_select = SelectField('Scene Type', choices = [])
    # scene_list_area   = TextAreaField('Scene List',    render_kw={"rows": 20, "cols": 40})
    # stdout_log        = TextAreaField('Stdout Log',    render_kw={"rows": 20, "cols": 60})


app = Flask(__name__)
app.config['SECRET_KEY'] = 'moot'
print(f' app.instance_path = {app.instance_path}')
print(f' app.root_path = {app.root_path}')



@app.route("/")
def index():
    proj, run, view = get_default_view_selection()
    vsf = get_populated_view_form(proj, run, view)
    # had to set these defaults outside the constructor
    vsf.project_select.default = proj
    vsf.run_select.default = run
    vsf.view_select.default = view
    ec2d = EC2DResults(proj)
    vsf.content = ec2d.run_remote_script('', 'optics.py', view + ' specs/' + proj + '_' + run + '.cfg')
    vsf.process()
    return render_template('view_select.html', form=vsf)



@app.route("/view_select/proj/<string:proj>/<string:view>")
def get_default_runs_for_project(proj, view):
    most_recent_dated_run = get_most_recent_dated_run(active_optics_data['projects'][proj])
    return get_json_for_proj_run_view(proj, most_recent_dated_run, view)


@app.route("/view_select/run/<string:run>/proj/<string:proj>/<string:view>")
def get_runs_for_project(proj, run, view):
    return get_json_for_proj_run_view(proj, run, view)


@app.route("/view_select/view/<string:view>/proj/<string:proj>/run/<string:run>")
def get_view_for_project_run(view, proj, run):
    if view == 'scene_result':
        return 'not implemented yet'
    return get_json_for_view(proj, run, view)

def get_video_url (proj, run, scene_type, scene_name):
    ec2d = EC2DResults(proj)
    video_parent_rel_path = f'{run}/videos/{scene_type}'
    video_rel_path        = f'{run}/videos/{scene_type}/{scene_name}_visual.mp4'
    url_rel_video_path = ec2d.retrieve_video(video_parent_rel_path, video_rel_path)
    if url_rel_video_path is None:
        video_url = None
    else:
        video_url = url_for('static',filename=url_rel_video_path)
    return video_url

def get_result_info(proj,run,scene_type, scene_name):
    info = active_optics_data['projects']
    scene_names = info[proj][run][scene_type]
    ec2d = EC2DResults(proj)
    stdout_log_rel_path = f'{run}/stdout_logs/{scene_type}/{scene_name}_stdout.txt'
    log_content = ec2d.get_file_contents_for_rel_path(stdout_log_rel_path)
    video_url = None
    if proj == 'inter':
        video_url = get_video_url(proj, run, scene_type, scene_name)
    return scene_names, log_content, video_url

def set_scene_result_form_values(srf, proj, run, view, scene_type):
    srf.project_select.default = proj
    srf.run_select.default = run
    srf.view_select.default = view
    srf.scene_type_select.default = scene_type
    srf.process()

@app.route("/scene_result/proj/<string:proj>")
def get_scene_result_for_project(proj):
    srf = get_populated_scene_result_form_for_proj(proj)
    default_run = get_default_run_for_proj(proj)
    scene_type, scene_name = get_default_scene_type_and_name(proj, default_run)
    set_scene_result_form_values(srf, proj, default_run, 'scene_result', scene_type)
    scene_names, log_content, video_url = get_result_info(proj, default_run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)

@app.route("/scene_result/proj/<string:proj>/run/<string:run>")
def get_scene_result_for_project_run(proj, run):
    srf = get_populated_scene_result_form_for_run(proj, run)
    scene_type, scene_name = get_default_scene_type_and_name(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene_result', scene_type)
    scene_names, log_content, video_url = get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)


@app.route("/scene_result/proj/<string:proj>/run/<string:run>/scene_type/<string:scene_type>")
def get_scene_result_for_project_run_type(proj, run, scene_type):
    srf = get_populated_scene_result_form_for_run(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene_result', scene_type)
    scene_name = get_default_scene_name_for_type(proj, run, scene_type)
    scene_names, log_content, video_url = get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)


@app.route("/scene_result/proj/<string:proj>/run/<string:run>/scene_type/<string:scene_type>/scene_name/<string:scene_name>")
def get_scene_result_for_project_run_type_scene(proj, run, scene_type, scene_name):
    srf = get_populated_scene_result_form_for_run(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene_result', scene_type)
    scene_names, log_content, video_url = get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)

# @app.route("/proj/<string:proj>")
# def show_project_runs(proj):
#     proj, run, scene_type, scene_name = get_default_selections_for_project(proj)
#     rsf = get_populated_form(proj, run, scene_type, scene_name)
#     rsf.project_select.default = proj
#     rsf.run_select.default = run
#     rsf.scene_type_select.default = scene_type
#     rsf.scene_name_select.default = scene_name
#     rsf.process()
#     return render_template('index.html', form=rsf)

# @app.route("/proj/<string:proj>")
# def show_project_runs(proj):
#     print(f' in show_project_runs, proj = {proj}')
#     proj, default_run, default_scene_type, default_scene_name = get_default_selections_for_project(proj)

#     print(f' in show_project_runs, proj = {proj}, default_run = {default_run}, default_scene_type = {default_scene_type}, default_scene_name = {default_scene_name}')
#     projects = active_optics_data['projects']
#     run_tuples = get_keys_as_tuples(projects[proj])
#     print(f'run_tuples = {run_tuples}')
#     global rsf
#     rsf.optics_run.choices = run_tuples
#     rsf.optics_run.default = default_run

#     scene_type_tuples = get_keys_as_tuples(projects[proj][default_run])
#     rsf.scene_types.choices = scene_type_tuples
#     rsf.scene_types.default = default_scene_type

#     scene_name_tuples = get_list_items_as_tuples(projects[proj][default_run][default_scene_type])
#     rsf.scene_names.choices = scene_name_tuples
#     rsf.scene_names.default = default_scene_name
#     rsf.process()
#     return render_template('index.html', form=rsf)
#     # if not proj in ['avoe', 'pvoe', 'inter']:
#     #     return f'ERROR:  project must be one of avoe, pvoe, inter'
#     # ec2d = EC2DResults(proj)
#     # specs_as_lines = ec2d.get_specs_for_project()
#     # s = make_links_from_list(f'{proj}', specs_as_lines)
#     # return s


@app.route("/<string:proj>/optics_run_names")
def get_optics_run_names(proj):
    print('fetched optics_run_names')
    ec2d = EC2DResults(proj)
    specs = ec2d.get_specs_for_project()
    specs_list = []
    print(f'specs = {specs}')
    for spec in specs:
        spec_obj = {}
        spec_obj['id'] = spec
        spec_obj['name'] = spec
        specs_list.append(spec_obj)
    return jsonify({'specs': specs_list})


@app.route("/<string:proj>/<run_name>/scene_type_names")
def get_scene_types_for_run(proj, run_name):
    ec2d = EC2DResults(proj)
    scene_types = ec2d.get_scene_types_for_run(run_name)
    scene_type_list = []
    print(f'scene_types = {scene_types}')
    for scene_type in scene_types:
        spec_obj = {}
        spec_obj['id'] = scene_type
        spec_obj['name'] = scene_type
        scene_type_list.append(spec_obj)
    return jsonify({'scene_types': scene_type_list})

# @app.route("/<string:proj>/<string:spec_name>")
# def show_spec_types(proj, spec_name):
#     ec2d = EC2DResults(proj)
#     types = ec2d.get_types_for_run(spec_name)
#     rel_path = f'{proj}/{spec_name}'
#     s = make_links_from_list(rel_path, types)
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


# @app.route("/<string:proj>/<string:spec_name>")
# def show_project_run_dirs(proj, spec_name):
#     if proj == 'inter':
#         dirs = ['logs','stdout_logs','videos']
#     else:
#         dirs = ['logs','stdout_logs']
#     rel_path = f'{proj}/{spec_name}'
#     s = make_links_from_list(rel_path, dirs)
#     return s

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

