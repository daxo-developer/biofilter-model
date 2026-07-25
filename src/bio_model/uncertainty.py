import numpy as np
import emcee
from .solver import ReactiveTransportModel

def log_likelihood(params, time_sec, inlet_obs, outlet_obs, L, nx, v_fixed):
    D_x, R = params
    if D_x <= 0 or R <= 0:
        return -np.inf
    model = ReactiveTransportModel(L=L, nx=nx, D_x=D_x, v=v_fixed, R=R)
    sol = model.solve(time_sec, inlet_obs)
    sim_outlet = sol[:, -1]
    sigma = np.std(outlet_obs - sim_outlet)
    if sigma <= 0:
        return -np.inf
    return -0.5 * np.sum(((outlet_obs - sim_outlet) / sigma) ** 2) - len(outlet_obs) * np.log(sigma)

def log_prior(params):
    D_x, R = params
    if 1e-6 < D_x < 1e-1 and 1e-7 < R < 1e-3:
        return 0.0
    return -np.inf

def log_posterior(params, time_sec, inlet_obs, outlet_obs, L, nx, v_fixed):
    lp = log_prior(params)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(params, time_sec, inlet_obs, outlet_obs, L, nx, v_fixed)

def mcmc_uncertainty(time_sec, inlet_obs, outlet_obs, L=10.0, nx=60, v_fixed=0.005,
                     n_walkers=32, n_steps=5000, initial_params=(1e-3, 1e-5)):
    """MCMC sampling of posterior distributions using emcee."""
    ndim = 2
    p0 = np.array(initial_params) + 1e-5 * np.random.randn(n_walkers, ndim)
    sampler = emcee.EnsembleSampler(
        n_walkers, ndim, log_posterior,
        args=(time_sec, inlet_obs, outlet_obs, L, nx, v_fixed)
    )
    sampler.run_mcmc(p0, n_steps, progress=True)
    return sampler.get_chain()
