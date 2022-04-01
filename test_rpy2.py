import numpy as np
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

from rpy2.robjects.conversion import localconverter

r = robjects.r
r['source']('R_sources/_test_rpy2_source.r')

x=[1,2,3,4,5]
y=[2,4,6,8,10]

r_func1=robjects.globalenv['func1']

df=pd.read_csv("output/testcase_output2/dataframe_sim_output/m2.csv")[['NAME_1','total_112']].rename(columns={f'total_112':'total'})

with localconverter(robjects.default_converter + pandas2ri.converter):
  r_from_pd_df = robjects.conversion.py2rpy(df)

ans_df_r=r_func1(r_from_pd_df)

with localconverter(robjects.default_converter + pandas2ri.converter):
  ans_df = robjects.conversion.rpy2py(ans_df_r)

print(ans_df)