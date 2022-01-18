import os
import pandas as pd
from flask import Flask, render_template, url_for, send_from_directory
from turbo_flask import Turbo
import threading
import time
import markdown
from markdown.extensions import fenced_code, codehilite
from pygments.formatters import HtmlFormatter

app = Flask(__name__, static_folder='output/testcase_output',
            static_url_path='')
turbo = Turbo(app)


@app.route("/")
def main():
    # list_allcase=sorted(set([i.split('.')[0] for i in os.listdir("output/testcase_output")]),key=lambda x: (int(x.split('_')[0]),-int(x.split('_precision')[-1])))
    # list_casenumber=[i.split('_')[0] for i in list_allcase]
    # list_precision=[i.split('_precision')[-1] for i in list_allcase]
    # return render_template("index.html",list_allcase=list_allcase,list_casenumber=list_casenumber,list_precision=list_precision)
    return render_template("index.html")


# Custom static data
@app.route('/testcase_modules/<path:filename>')
def custom_static(filename):
    # return send_from_directory(app.config['CUSTOM_STATIC_PATH'], filename)
    assert filename[-4:] == '.PNG', "What the FUCK are you DOING!!!!"
    return send_from_directory("testcase_modules", filename)


@app.route('/readme')
def readme():
    readme_file = open("testcase_modules/README_TestCase.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=['fenced_code', 'codehilite']
    )
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()
    md_css_string = "<style>" + css_string + "</style>"
    md_template = md_css_string + md_template_string
    return md_template


@app.route("/detail/<int:testcase>/<int:precision>")
def detail(testcase, precision):
    list_allcase = sorted(set([i.split('.')[0] for i in os.listdir(
        "output/testcase_output")]), key=lambda x: (int(x.split('_')[0]), -int(x.split('_precision')[-1])))
    list_casenumber = [i.split('_')[0] for i in list_allcase]
    assert str(testcase) in list_casenumber, "incorrect testcase"
    assert str(testcase)+"_precision" + \
        str(precision) in list_allcase, "incorrect precision"
    target_case = str(testcase)+"_precision"+str(precision)
    dist_table = pd.read_csv("output/testcase_output/"+target_case+".csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    g_global_table = pd.read_csv("output/testcase_output/"+target_case+".g.global.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    gi_table = pd.read_csv("output/testcase_output/"+target_case+".gi.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    gistar_table = pd.read_csv("output/testcase_output/"+target_case+".gistar.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    moran_global_table = pd.read_csv("output/testcase_output/"+target_case+".moran.global.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    lisa_table = pd.read_csv("output/testcase_output/"+target_case+".lisa.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    c_global_table = pd.read_csv("output/testcase_output/"+target_case+".c.global.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    c_local_table = pd.read_csv("output/testcase_output/"+target_case+".c.local.csv").to_html(
        classes=["table", "table-striped", "table-hover"], index=False)
    return render_template("detail.html", testcase=testcase, precision=precision, dist_table=dist_table, gi_table=gi_table, g_global_table=g_global_table, gistar_table=gistar_table, moran_global_table=moran_global_table, lisa_table=lisa_table, c_global_table=c_global_table, c_local_table=c_local_table)


@app.context_processor
def inject_load():
    list_allcase = sorted(set([i.split('.')[0] for i in os.listdir(
        "output/testcase_output")]), key=lambda x: (int(x.split('_')[0]), -int(x.split('_precision')[-1])))
    list_casenumber = [i.split('_')[0] for i in list_allcase]
    list_precision = [i.split('_precision')[-1] for i in list_allcase]
    return {'list_allcase': list_allcase, 'list_casenumber': list_casenumber, 'list_precision': list_precision}


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        while True:
            time.sleep(10)
            turbo.push(turbo.replace(
                render_template('_case_catalog.html'), 'load'))


if __name__ == "__main__":
    app.run(debug=True)
