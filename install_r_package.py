import rpy2.robjects as robjects
r = robjects.r
r['source']('R_sources/_install_r_package_source.r')

r_install_package_func=robjects.globalenv['custom_package_install']
r_install_package_func()