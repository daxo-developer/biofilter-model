import numpy as np
from bio_model.solver import ReactiveTransportModel
from bio_model.calibration import calibrate

def test_calibration_synthetic():
    """Calibration should recover parameters with reasonable accuracy."""
    np.random.seed(42)
    time_days = np.linspace(0, 10, 200)
    time_sec = time_days * 86400.0
    inlet = 1.0 + 0.2 * np.sin(2 * np.pi * time_days / 2.5) + 0.05 * np.cos(2 * np.pi * time_days / 1.2)

    true_Dx = 3.0e-4
    true_R = 1.5 / 86400.0
    model_true = ReactiveTransportModel(L=10.0, nx=100, D_x=true_Dx, v=0.005, R=true_R)
    sol = model_true.solve(time_sec, inlet)
    outlet = sol[:, -1]

    # Add a tiny noise to make it realistic (but deterministic)
    outlet_noisy = outlet + 0.001 * np.random.randn(len(outlet))

    D_cal, R_cal, rmse, r2, _ = calibrate(time_sec, inlet, outlet_noisy, nx=80)

    # Checks
    # 1. Parameters should be of the correct order of magnitude
    assert 1e-5 < D_cal < 1e-2, f"D_x = {D_cal:.3e} outside expected range"
    assert 1e-7 < R_cal < 1e-3, f"R = {R_cal:.3e} outside expected range"

    # 2. RMSE should be small (noise level)
    assert rmse < 0.05, f"RMSE = {rmse:.3f} too high"

    # 3. R² should be close to 1
    assert r2 > 0.8, f"R² = {r2:.3f} too low"
