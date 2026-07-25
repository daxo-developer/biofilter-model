import numpy as np
from scipy.optimize import minimize
from .solver import ReactiveTransportModel

def calibrate(time_sec, inlet_obs, outlet_obs, L=10.0, nx=100, v_fixed=0.005,
              x0=(1e-3, 1e-5), bounds=((1e-6, 1e-1), (1e-7, 1e-3))):
    """
    Calibrate D_x and R by minimizing RMSE.
    Returns (D_cal, R_cal, rmse, r2, optim_result).
    """
    def objective(params):
        D_x, R = params
        if D_x <= 0 or R <= 0:
            return 1e9
        model = ReactiveTransportModel(L=L, nx=nx, D_x=D_x, v=v_fixed, R=R)
        sol = model.solve(time_sec, inlet_obs)
        sim_outlet = sol[:, -1]
        return np.sqrt(np.mean((sim_outlet - outlet_obs) ** 2))

    res = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
    D_cal, R_cal = res.x
    rmse = res.fun

    model = ReactiveTransportModel(L=L, nx=nx, D_x=D_cal, v=v_fixed, R=R_cal)
    sol = model.solve(time_sec, inlet_obs)
    sim_outlet = sol[:, -1]
    ss_res = np.sum((outlet_obs - sim_outlet) ** 2)
    ss_tot = np.sum((outlet_obs - np.mean(outlet_obs)) ** 2)
    r2 = 1.0 - ss_res / ss_tot

    return D_cal, R_cal, rmse, r2, res

def bootstrap_ci(time_sec, inlet_obs, outlet_obs, n_bootstrap=100, alpha=0.05,
                 L=10.0, nx=100, v_fixed=0.005, x0=(1e-3, 1e-5)):
    """Bootstrap confidence intervals for D_x and R."""
    n = len(outlet_obs)
    D_list, R_list = [], []
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        outlet_boot = outlet_obs[idx]
        inlet_boot = inlet_obs[idx]
        try:
            D_boot, R_boot, _, _, _ = calibrate(
                time_sec, inlet_boot, outlet_boot, L, nx, v_fixed, x0)
            D_list.append(D_boot)
            R_list.append(R_boot)
        except Exception:
            continue
    D_arr = np.array(D_list)
    R_arr = np.array(R_list)
    low_dx, high_dx = np.percentile(D_arr, [100*alpha/2, 100*(1-alpha/2)])
    low_r, high_r = np.percentile(R_arr, [100*alpha/2, 100*(1-alpha/2)])
    return {'D_x': (low_dx, high_dx), 'R': (low_r, high_r)}
