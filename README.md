# Bio-Model

**Reactive transport model with calibration, sensitivity, and uncertainty quantification**

This package implements a 1D advection-dispersion-reaction model for solute transport in porous media. It includes:

- Numerical solver (Crank–Nicolson) with Thomas algorithm.
- Verification against the Ogata–Banks analytical solution.
- Real data loader from USGS Water Data (RDB format).
- Parameter calibration (Dₓ and R) via non‑linear least squares.
- Bootstrap confidence intervals for calibrated parameters.
- Global sensitivity analysis (Sobol indices) using SALib.
- Markov Chain Monte Carlo (MCMC) uncertainty estimation using `emcee`.

## Installation

```
git clone https://github.com/daxo-developer/bio-model.git
cd bio-model
pip install -e .

Usage

```
from bio_model import load_usgs_data, calibrate, bootstrap_ci

# Load real data (or use local CSV)
df = load_usgs_data(site='01646500', start='2023-01-01', end='2023-12-31')

# Calibrate
D, R, rmse, r2, _ = calibrate(df['time_sec'], df['inlet'], df['outlet'])

# Bootstrap CI
ci = bootstrap_ci(df['time_sec'], df['inlet'], df['outlet'])
print(ci)
```

Testing

```
pytest tests/ --cov=src/bio_model
```

Documentation

```
cd docs
make html
```

License

MIT
