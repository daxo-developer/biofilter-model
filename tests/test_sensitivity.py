import numpy as np
from bio_model.sensitivity import sensitivity_analysis

def test_sensitivity_analysis_returns_dict():
    """Ensure Sobol analysis returns a valid dictionary with sensitivity indices."""
    np.random.seed(42)
    time_sec = np.linspace(0, 10, 50) * 86400.0
    inlet = 1.0 + 0.1 * np.sin(time_sec / 86400.0)
    outlet = inlet * 0.9 + 0.01 * np.random.randn(50)

    # Use a small number of samples for fast testing
    result = sensitivity_analysis(time_sec, inlet, outlet, n_samples=64)

    assert isinstance(result, dict)
    # SALib returns keys like 'S1', 'ST', etc.
    assert "S1" in result or "ST" in result
