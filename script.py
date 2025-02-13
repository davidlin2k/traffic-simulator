#!/usr/bin/env python3
"""
Bounded Pareto CDF Plotter

This script computes and plots the CDF of a bounded Pareto distribution,
where the CDF is defined as:

    F(x; L, H, α) = 0,                              for x < L,
                  = (1 - L^α x^{-α}) / (1 - (L/H)^α),  for L ≤ x ≤ H,
                  = 1,                              for x > H.

Three datasets are considered:
    1. Web Search:
         L = 3 KB       (3 * 1024 bytes)
         H = 29.2 MB    (29.2 * 1024^2 bytes)
         α = 0.125

    2. Data Mining:
         L = 100 B      (100 bytes)
         H = 973.34 MB  (973.34 * 1024^2 bytes)
         α = 0.26

    3. ML Workload Flow Size:
         L = 512 kB     (512 * 1024 bytes)
         H = 1048576 kB (1048576 * 1024 bytes)
         α = 1.5

Note: 1 KB = 1024 bytes, 1 MB = 1024^2 bytes.
"""

import numpy as np
import matplotlib.pyplot as plt


def bounded_pareto_cdf(x, L, H, alpha):
    """
    Compute the CDF of a bounded Pareto distribution.

    Parameters:
        x     : scalar or numpy array
                The point(s) at which to evaluate the CDF.
        L     : float
                The lower bound (minimum value) of the distribution.
        H     : float
                The upper bound (maximum value) of the distribution.
        alpha : float
                The Pareto exponent.

    Returns:
        cdf_x : scalar or numpy array
                The CDF evaluated at x.
    """
    # Ensure x is a numpy array for vectorized operations.
    x = np.array(x, dtype=float)
    cdf_x = np.zeros_like(x)

    # For x in [L, H], apply the bounded Pareto formula.
    mask = (x >= L) & (x <= H)
    cdf_x[mask] = (1 - (L**alpha) * (x[mask] ** (-alpha))) / (1 - (L / H) ** alpha)

    # For x > H, the CDF is 1.
    cdf_x[x > H] = 1.0

    return cdf_x


def plot_cdfs():
    # Conversion factors.
    KB = 1024
    MB = 1024 * 1024

    # Parameters for Web Search distribution.
    L_web = 3 * KB  # 3 KB in bytes.
    H_web = 29.2 * MB  # 29.2 MB in bytes.
    alpha_web = 0.125

    # Parameters for Data Mining distribution.
    L_dm = 100  # 100 bytes.
    H_dm = 973.34 * MB  # 973.34 MB in bytes.
    alpha_dm = 0.26

    # Parameters for ML Workload Flow Size distribution.
    L_ml = 512 * KB  # 512 kB converted to bytes.
    H_ml = 1048576 * KB  # 1048576 kB converted to bytes.
    alpha_ml = 1.5

    # Generate logarithmically spaced x-values for each distribution.
    x_web = np.logspace(np.log10(L_web), np.log10(H_web), num=500)
    x_dm = np.logspace(np.log10(L_dm), np.log10(H_dm), num=500)
    x_ml = np.logspace(np.log10(L_ml), np.log10(H_ml), num=500)

    # Compute the CDF values for each dataset.
    cdf_web = bounded_pareto_cdf(x_web, L_web, H_web, alpha_web)
    cdf_dm = bounded_pareto_cdf(x_dm, L_dm, H_dm, alpha_dm)
    cdf_ml = bounded_pareto_cdf(x_ml, L_ml, H_ml, alpha_ml)

    # Create the plot.
    fig, ax = plt.subplots(figsize=(10, 7))

    ax.plot(x_web, cdf_web, label="Web Search (L=3KB, H=29.2MB, α=0.125)", color="blue")
    ax.plot(x_dm, cdf_dm, label="Data Mining (L=100B, H=973.34MB, α=0.26)", color="red")
    ax.plot(
        x_ml,
        cdf_ml,
        label="ML Workload Flow Size (L=512kB, H=1048576kB, α=1.5)",
        color="green",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Size (Bytes)", fontsize=12)
    ax.set_ylabel("Cumulative Probability", fontsize=12)
    ax.set_title("CDF of Bounded Pareto Distributions", fontsize=14)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_cdfs()
