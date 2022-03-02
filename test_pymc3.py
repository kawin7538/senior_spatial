import numpy as np
import pymc3 as pm
import matplotlib.pyplot as plt
import arviz as az

if __name__=='__main__':
    alpha,sigma=5,1
    beta=[3.55,2.5]

    size=10000

    X1=np.random.randn(size)
    X2=np.random.randn(size)

    Y=alpha+beta[0]*X1+beta[1]*X2+np.random.randn(size)*sigma

    basic_model=pm.Model()

    with basic_model:
        alpha=pm.Normal("alpha",mu=0,sigma=10)
        beta=pm.Normal("beta",mu=0,sigma=10,shape=2)
        sigma=pm.HalfNormal("sigma",sigma=1)

        mu=alpha+beta[0]*X1+beta[1]*X2

        Y_obs=pm.Normal("Y_obs",mu=mu,sigma=sigma,observed=Y)

    map_estimate=pm.find_MAP(model=basic_model)
    print(map_estimate)

    with basic_model:
        step=pm.Slice()
        trace = pm.sample(1000, step=step, return_inferencedata=False)
        az.plot_trace(trace)
        plt.savefig("plot_preview.png")