import rpy2.robjects as robjects
r = robjects.r
r['source']('R_sources/_test_rpy2_source.r')

x=[1,2,3,4,5]
y=[2,4,6,8,10]

r_func1=robjects.globalenv['func1']
r_func1(x,y)