import numpy as np
from scipy.special import erfc

class ReactiveTransportModel:
    def __init__(self, L=10.0, nx=100, D_x=1e-4, v=0.005, R=1.3/86400):
        self.L = float(L)
        self.nx = int(nx)
        self.D_x = float(D_x)
        self.v = float(v)
        self.R = float(R)
        self.dx = self.L / (self.nx - 1)
        self.x = np.linspace(0, self.L, self.nx)

    def solve(self, time_seconds, inlet_series):
        nt = len(time_seconds)
        C = np.full(self.nx, inlet_series[0])
        solutions = [C.copy()]

        for n in range(1, nt):
            dt = time_seconds[n] - time_seconds[n - 1]
            if dt <= 0:
                dt = 1.0

            r = self.D_x * dt / (2.0 * self.dx**2)
            s = self.v * dt / (2.0 * self.dx)
            beta = self.R * dt / 2.0

            a = np.zeros(self.nx - 1)
            b = np.zeros(self.nx)
            c = np.zeros(self.nx - 1)
            d = np.zeros(self.nx)

            for i in range(1, self.nx - 1):
                a[i - 1] = -(r + 2 * s)
                b[i] = 1.0 + 2 * r + 2 * s + beta
                c[i] = -r
                d[i] = (r + 2 * s) * C[i - 1] + (1.0 - 2 * r - 2 * s - beta) * C[i] + r * C[i + 1]

            b[0] = 1.0
            c[0] = 0.0
            d[0] = inlet_series[n]

            a[-1] = -1.0
            b[-1] = 1.0
            d[-1] = 0.0

            C = self._thomas_solver(a, b, c, d)
            C = np.clip(C, 0, None)
            solutions.append(C.copy())

        return np.array(solutions)

    def _thomas_solver(self, a, b, c, d):
        n = len(d)
        c_p = np.zeros(n - 1)
        d_p = np.zeros(n)

        c_p[0] = c[0] / b[0]
        d_p[0] = d[0] / b[0]

        for i in range(1, n - 1):
            denom = b[i] - a[i - 1] * c_p[i - 1]
            c_p[i] = c[i] / denom
            d_p[i] = (d[i] - a[i - 1] * d_p[i - 1]) / denom

        d_p[-1] = (d[-1] - a[-1] * d_p[-2]) / (b[-1] - a[-1] * c_p[-2])

        x = np.zeros(n)
        x[-1] = d_p[-1]
        for i in range(n - 2, -1, -1):
            x[i] = d_p[i] - c_p[i] * x[i + 1]

        return x

    def ogata_banks(self, time_seconds, x_eval=None, c0=1.0):
        """Analytical solution for constant inlet (R=0), avoiding division by zero."""
        if x_eval is None:
            x_eval = self.x

        t = np.asarray(time_seconds)
        x = np.asarray(x_eval)

        # Handle scalar inputs
        if t.ndim == 0:
            t = t[None]
        if x.ndim == 0:
            x = x[None]

        # Initialize output array
        c = np.zeros((len(t), len(x)))

        # Mask for t == 0
        zero_mask = (t == 0)
        if np.any(zero_mask):
            # At t=0: c = c0 at x=0, else 0
            c[zero_mask, :] = 0.0
            c[zero_mask, 0] = c0   # assuming x[0] = 0

        # For t > 0, compute using Ogata-Banks formula
        non_zero = ~zero_mask
        if np.any(non_zero):
            t_nz = t[non_zero]
            denom = 2.0 * np.sqrt(self.D_x * t_nz[:, None])
            arg1 = (x[None, :] - self.v * t_nz[:, None]) / denom
            arg2 = (x[None, :] + self.v * t_nz[:, None]) / denom
            c_nz = 0.5 * c0 * (erfc(arg1) + np.exp(self.v * x[None, :] / self.D_x) * erfc(arg2))
            c[non_zero, :] = c_nz

        return c.squeeze()
