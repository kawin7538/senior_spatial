import os
import pandas as pd
from flask import Flask, render_template, url_for, send_from_directory

app = Flask(__name__,static_folder='output/testcase_output', static_url_path='')

@app.route("/")
def main():
    list_allcase=sorted(set([i.split('.')[0] for i in os.listdir("output/testcase_output")]),key=lambda x: (int(x.split('_')[0]),-int(x.split('_precision')[-1])))
    list_casenumber=[i.split('_')[0] for i in list_allcase]
    list_precision=[i.split('_precision')[-1] for i in list_allcase]
    return render_template("index.html",list_allcase=list_allcase,list_casenumber=list_casenumber,list_precision=list_precision)

@app.route("/detail/<int:testcase>/<int:precision>")
def detail(testcase,precision):
    list_allcase=sorted(set([i.split('.')[0] for i in os.listdir("output/testcase_output")]),key=lambda x: (int(x.split('_')[0]),-int(x.split('_precision')[-1])))
    list_casenumber=[i.split('_')[0] for i in list_allcase]
    assert str(testcase) in list_casenumber, "incorrect testcase"
    assert str(testcase)+"_precision"+str(precision) in list_allcase, "incorrect precision"
    target_case=str(testcase)+"_precision"+str(precision)
    dist_table=pd.read_csv("output/testcase_output/"+target_case+".csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    g_global_table=pd.read_csv("output/testcase_output/"+target_case+".g.global.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    gi_table=pd.read_csv("output/testcase_output/"+target_case+".gi.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    gistar_table=pd.read_csv("output/testcase_output/"+target_case+".gistar.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    moran_global_table=pd.read_csv("output/testcase_output/"+target_case+".moran.global.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    lisa_table=pd.read_csv("output/testcase_output/"+target_case+".lisa.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    c_global_table=pd.read_csv("output/testcase_output/"+target_case+".c.global.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    c_local_table=pd.read_csv("output/testcase_output/"+target_case+".c.local.csv").to_html(classes=["table","table-striped","table-hover"],index=False)
    return render_template("detail.html",testcase=testcase,precision=precision,dist_table=dist_table,gi_table=gi_table,g_global_table=g_global_table,gistar_table=gistar_table,moran_global_table=moran_global_table,lisa_table=lisa_table,c_global_table=c_global_table,c_local_table=c_local_table)

if __name__ == "__main__":
    app.run(debug=True)