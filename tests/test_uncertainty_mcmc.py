import numpy as np
from bio_model.uncertainty import mcmc_uncertainty

def test_mcmc_runs_without_error():
    """Check that MCMC sampler runs and returns a chain."""
    np.random.seed(42)
    time_sec = np.linspace(0, 5, 20) * 86400.0
    inlet = 1.0 + 0.1 * np.sin(time_sec / 86400.0)
    outlet = inlet * 0.9 + 0.01 * np.random.randn(20)

    # Run MCMC with very few steps for testing
    chain = mcmc_uncertainty(time_sec, inlet, outlet,
                             n_walkers=4, n_steps=10,
                             initial_params=(1e-3, 1e-5))
    assert chain.shape == (10, 4, 2)  # (steps, walkers, params)
    assert not np.any(np.isnan(chain))
