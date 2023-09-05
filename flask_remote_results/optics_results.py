from flask import Flask, render_template, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from utils import get_view_names
from optics_data import OpticsData
from ec2_results import EC2DResults
import os, json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'moot'
print(f' app.instance_path = {app.instance_path}')
print(f' app.root_path = {app.root_path}')

optics_data = OpticsData()


#####################################################
#
# View Selection Form
#
#####################################################

class ViewSelectForm(FlaskForm):
    project_select    = SelectField('Project',    choices = [])
    run_select        = SelectField('Run',        choices = [])
    view_select       = SelectField('View',       choices = [])
    content           = TextAreaField('Content',  render_kw={"rows": 20, "cols": 100})


def get_populated_view_form(proj, run, view_choice):
    f = ViewSelectForm()
    f.project_select.choices = ['avoe', 'inter','pvoe']
    f.project_select.default = proj
    run_tuples = optics_data.get_run_tuples(proj)
    f.run_select.choices = run_tuples
    f.view_select.choices = get_view_names()
    return f


def set_view_select_form_values(f, proj, run, view):
    f.project_select.default = proj
    f.run_select.default = run
    f.view_select.default = view
    f.process()

#####################################################
#
# View Selection Routes
#
#####################################################


@app.route("/")
def index():
    proj, run, view = optics_data.get_default_view_selection('inter')
    vsf = get_populated_view_form(proj, run, view)
    set_view_select_form_values(vsf, proj, run, view)
    ec2d = EC2DResults()
    vsf.content = ec2d.run_remote_script('', 'optics.py', view + ' specs/' + proj + '_' + run + '.cfg')
    return render_template('view_select.html', form=vsf)


@app.route("/view_select/to_proj/<string:proj>/view/<string:view>")
def get_chosen_view_for_default_run(proj, view):
    most_recent_dated_run = optics_data.get_most_recent_dated_run(proj)
    return optics_data.get_json_for_proj_run_view(proj, most_recent_dated_run, view)


@app.route("/view_select/proj/<string:proj>/to_run/<string:run>/view/<string:view>")
def get_chosen_view_for_specified_run(proj, run, view):
    return optics_data.get_json_for_proj_run_view(proj, run, view)


@app.route("/return_to_view_select/proj/<string:proj>/run/<string:run>/view/<string:view>")
def get_runs_for_project(proj, run, view):
    vsf = get_populated_view_form(proj, run, view)
    set_view_select_form_values(vsf, proj, run, view)
    ec2d = EC2DResults()
    vsf.content = ec2d.run_remote_script('', 'optics.py', view + ' specs/' + proj + '_' + run + '.cfg')
    return render_template('view_select.html', form=vsf)

@app.route("/view_select/proj/<string:proj>/run/<string:run>/to_view/<string:view>")
def get_view_for_project_run(view, proj, run):
    if view == 'scene result':
        return 'not implemented yet'
    return optics_data.get_json_for_view(proj, run, view)


#####################################################
#
# Scene Result Form
#
#####################################################


class SceneResultForm(FlaskForm):
    project_select    = SelectField('Project',    choices = [])
    run_select        = SelectField('Run',        choices = [])
    view_select       = SelectField('View',       choices = [])
    scene_type_select = SelectField('Scene Type', choices = [])

def get_populated_scene_result_form_for_proj(proj):
    srf = SceneResultForm()
    srf.project_select.choices    = ['avoe', 'inter','pvoe']
    srf.run_select.choices        = optics_data.get_run_tuples(proj)
    srf.view_select.choices       = get_view_names()
    default_run = optics_data.get_default_run_for_proj(proj)
    srf.scene_type_select.choices = optics_data.get_scene_type_tuples(proj, default_run)
    return srf

def get_populated_scene_result_form_for_run(proj, run):
    srf = SceneResultForm()
    srf.project_select.choices    = ['avoe', 'inter','pvoe']
    srf.run_select.choices        = optics_data.get_run_tuples(proj)
    srf.view_select.choices       = get_view_names()
    srf.scene_type_select.choices = optics_data.get_scene_type_tuples(proj, run)
    return srf

def set_scene_result_form_values(srf, proj, run, view, scene_type):
    srf.project_select.default = proj
    srf.run_select.default = run
    srf.view_select.default = view
    srf.scene_type_select.default = scene_type
    srf.process()

#####################################################
#
# Scene Result Routes
#
#####################################################

@app.route("/scene_result/proj/<string:proj>")
def get_scene_result_for_project(proj):
    srf = get_populated_scene_result_form_for_proj(proj)
    default_run = optics_data.get_default_run_for_proj(proj)
    scene_type, scene_name = optics_data.get_default_scene_type_and_name(proj, default_run)
    set_scene_result_form_values(srf, proj, default_run, 'scene result', scene_type)
    scene_names, log_content, video_url = optics_data.get_result_info(proj, default_run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)

@app.route("/scene_result/proj/<string:proj>/run/<string:run>")
def get_scene_result_for_project_run(proj, run):
    srf = get_populated_scene_result_form_for_run(proj, run)
    scene_type, scene_name = optics_data.get_default_scene_type_and_name(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene result', scene_type)
    scene_names, log_content, video_url = optics_data.get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)


@app.route("/scene_result/proj/<string:proj>/run/<string:run>/scene_type/<string:scene_type>")
def get_scene_result_for_project_run_type(proj, run, scene_type):
    srf = get_populated_scene_result_form_for_run(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene result', scene_type)
    scene_name = optics_data.get_default_scene_name_for_type(proj, run, scene_type)
    scene_names, log_content, video_url = optics_data.get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)


@app.route("/scene_result/proj/<string:proj>/run/<string:run>/scene_type/<string:scene_type>/scene_name/<string:scene_name>")
def get_scene_result_for_project_run_type_scene(proj, run, scene_type, scene_name):
    srf = get_populated_scene_result_form_for_run(proj, run)
    set_scene_result_form_values(srf, proj, run, 'scene result', scene_type)
    scene_names, log_content, video_url = optics_data.get_result_info(proj, run, scene_type, scene_name)
    return render_template('scene_result_view.html', form=srf, scene_name=scene_name, scene_names=scene_names, log_content=log_content, video_url=video_url)


@app.route("/scene_result/proj/<string:proj>/run/<string:run>/scene_type/<string:scene_type>/other_scene_name/<string:scene_name>")
def get_other_scene_result_for_project_run_type_scene(proj, run, scene_type, scene_name):
    _, log_content, _ = optics_data.get_result_info(proj, run, scene_type, scene_name)
    return jsonify({'log_content': log_content})



if __name__ == '__main__':
    app.run(debug=True)
