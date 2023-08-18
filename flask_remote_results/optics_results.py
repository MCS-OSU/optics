from flask import Flask
from flask_remote_results.ec2_results import EC2DResults

app = Flask(__name__)

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
def show_project_run_dirs(proj, spec_name):
    dirs = ['logs','stdout_logs']
    rel_path = f'{proj}/{spec_name}'
    s = make_links_from_list(rel_path, dirs)
    return s


@app.route("/<string:proj>/<string:spec_name>/logs")
def show_log_scene_types(proj, spec_name):
    ec2d = EC2DResults(proj)
    proj_rel_path = f'{spec_name}/logs'
    log_scene_types = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
    s = make_links_from_list(f'{proj}/{proj_rel_path}', log_scene_types)
    return s

@app.route("/<string:proj>/<string:spec_name>/stdout_logs")
def show_stdout_log_scene_types(proj, spec_name):
    ec2d = EC2DResults(proj)
    proj_rel_path = f'{spec_name}/stdout_logs'
    stdout_log_scene_types = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
    s = make_links_from_list(f'{proj}/{proj_rel_path}', stdout_log_scene_types)
    return s

@app.route("/<string:proj>/<string:spec_name>/<string:log_type>/<string:scene_type>")
def show_log_list_for_scene_types(proj, spec_name, log_type, scene_type):
    if not log_type in ['logs', 'stdout_logs']:
        return f'ERROR:  log_type must be one of logs, stdout_logs'
    ec2d = EC2DResults(proj)
    proj_rel_path = f'{spec_name}/{log_type}/{scene_type}'
    logs = ec2d.get_dir_contents_for_rel_path(proj_rel_path)
    s = make_links_from_list(f'{proj}/{proj_rel_path}', logs)
    return s

@app.route("/<string:proj>/<string:spec_name>/<string:log_type>/<string:scene_type>/<string:log_name>")
def show_log(proj, spec_name, log_type, scene_type, log_name):
    ec2d = EC2DResults(proj)
    proj_rel_path = f'{spec_name}/{log_type}/{scene_type}/{log_name}'
    s = ec2d.get_file_contents_for_rel_path(proj_rel_path)
    return f'<span style="white-space:pre-wrap;font-family:\'Courier New\'">\n{s}\n</span>'



    #return f'<span style="white-space:pre-wrap;font-family:\'Courier New\'">\n{specs}\n</span>'

def make_links_from_list(rel_path, list):
    s = ''
    for item in list:
        s += f'<a href="http://localhost:5000/{rel_path}/{item}">{item}</a><br>'
    return s

# @app.route("/runs")
# def show_runs():
#     ec2d = EC2DResults()
#     scores = ec2d.get_remote_scores('avoe_053123_eval6.cfg')
#     return f'<span style="white-space:pre-wrap;font-family:\'Courier New\'">\n{scores}\n</span>'

if __name__ == '__main__':
    app.run(debug=True)

