import numpy as np
from SALib.sample import sobol
from SALib.analyze import sobol as sobol_analyze
from .solver import ReactiveTransportModel

def sensitivity_analysis(time_sec, inlet_obs, outlet_obs, L=10.0, nx=60, v_fixed=0.005,
                         problem=None, n_samples=1024):
    """
    Global sensitivity analysis using Sobol indices (SALib).

    Parameters
    ----------
    problem : dict, optional
        SALib problem definition. Default: Dₓ∈[1e-6,1e-1], R∈[1e-7,1e-3].
    n_samples : int
        Number of samples for Sobol sequence.

    Returns
    -------
    Si : dict
        Sobol indices (first-order, total, etc.).
    """
    if problem is None:
        problem = {
            'num_vars': 2,
            'names': ['D_x', 'R'],
            'bounds': [[1e-6, 1e-1], [1e-7, 1e-3]]
        }

    # Generate Sobol samples (new API)
    param_values = sobol.sample(problem, n_samples)

    def evaluate(params):
        rmse_list = []
        for p in params:
            D_x, R = p
            model = ReactiveTransportModel(L=L, nx=nx, D_x=D_x, v=v_fixed, R=R)
            sol = model.solve(time_sec, inlet_obs)
            sim_outlet = sol[:, -1]
            rmse = np.sqrt(np.mean((sim_outlet - outlet_obs) ** 2))
            rmse_list.append(rmse)
        return np.array(rmse_list)

    Y = evaluate(param_values)
    Si = sobol_analyze.analyze(problem, Y)
    return Si
