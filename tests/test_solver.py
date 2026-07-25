import numpy as np
from bio_model.solver import ReactiveTransportModel

def test_solver_outputs_finite():
    L = 10.0; nx = 50; D_x = 1e-4; v = 0.005; R = 1.3 / 86400.0
    model = ReactiveTransportModel(L=L, nx=nx, D_x=D_x, v=v, R=R)
    time_days = np.linspace(0, 10, 100)
    time_sec = time_days * 86400.0
    inlet = 1.0 + 0.2 * np.sin(2 * np.pi * time_days / 2.5)
    sol = model.solve(time_sec, inlet)
    assert not np.any(np.isnan(sol)), "Solution contains NaN"
    assert np.all(sol >= -1e-12), "Negative concentrations found"
    outlet = sol[:, -1]
    assert np.all(outlet <= inlet + 1e-6), "Outlet exceeds inlet (unphysical)"
    max_inlet = np.max(inlet)
    assert np.all(sol <= max_inlet + 1e-6), "Concentration exceeds inlet maximum"
    grad = np.gradient(sol, axis=1)
    assert np.all(np.abs(grad) < 1e-1), "Unreasonably large gradients"

def test_ogata_banks_analytic_consistency():
    """Check Ogata-Banks solution against known behavior at t->0 and t->inf."""
    L = 10.0
    nx = 10
    D_x = 1e-4
    v = 0.005
    model = ReactiveTransportModel(L=L, nx=nx, D_x=D_x, v=v, R=0.0)

    # Use two time points to ensure 2D output
    t_small = np.array([1e-6, 2e-6]) * 86400.0
    c_ana = model.ogata_banks(t_small, x_eval=model.x, c0=1.0)
    # At x=0, should be ~c0
    assert np.abs(c_ana[0, 0] - 1.0) < 0.01
    # At x=L, should be very small (since diffusion hasn't reached)
    assert c_ana[0, -1] < 0.01

    # At very large time, concentration should approach c0 everywhere (no reaction)
    t_large = np.array([1e6, 2e6]) * 86400.0
    c_ana_large = model.ogata_banks(t_large, x_eval=model.x, c0=1.0)
    assert np.all(c_ana_large > 0.99)
