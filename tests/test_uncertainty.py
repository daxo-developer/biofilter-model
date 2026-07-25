import numpy as np
from bio_model.calibration import bootstrap_ci

def test_bootstrap_ci_returns_valid_bounds():
    """Check that bootstrap returns proper confidence intervals."""
    np.random.seed(42)
    time_sec = np.linspace(0, 10, 50) * 86400.0
    inlet = 1.0 + 0.1 * np.sin(time_sec / 86400.0)
    outlet = inlet * 0.9 + 0.01 * np.random.randn(50)

    # Run bootstrap with small number of iterations for speed
    ci = bootstrap_ci(time_sec, inlet, outlet, n_bootstrap=10)

    assert "D_x" in ci and "R" in ci
    assert ci["D_x"][0] < ci["D_x"][1]   # Lower bound < upper bound
    assert ci["R"][0] < ci["R"][1]
