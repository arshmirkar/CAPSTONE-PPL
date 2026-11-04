"""
F1 - Time-series object, rolling statistics, ADF stationarity test and differencing
(Lab 12: Task 1 + practice tasks 2 and 3)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from common import build_weekly_series, save_fig, OUT_DIR, C
import os


def adf_row(name, x):
    stat, p, _, _, crit, _ = adfuller(x, autolag="AIC")   # AIC lag selection: lets the data pick the augmentation lags
    return {"Series": name, "ADF_stat": round(stat, 3), "p_value": round(p, 4), "crit_5%": round(crit["5%"], 3),
            "Stationary(alpha=0.05)": "Yes" if p < 0.05 else "No"}


def difference_until_stationary(ts, max_d=2):
    """Difference once or twice (as the lab asks) until ADF p < 0.05; return series, d and every ADF row."""
    rows, x, d = [adf_row("Original (d=0)", ts)], ts, 0
    while rows[-1]["Stationary(alpha=0.05)"] == "No" and d < max_d:
        d += 1
        x = ts.diff(d).dropna() if d == 1 else x.diff().dropna()   # d=2 is a second difference of the first difference
        rows.append(adf_row(f"Differenced (d={d})", x))
    return x, d, rows


if __name__ == "__main__":
    ts = build_weekly_series()                         # DatetimeIndex weekly series = the "time series object"
    print(ts.head(3), "\n...", len(ts), "weekly observations,", ts.index.min().date(), "->", ts.index.max().date())
    print("Subset (Oct-Dec 2024):\n", ts["2024-10":"2024-12"].round(0).to_string())   # label-based subsetting

    roll_mean = ts.rolling(window=13).mean()           # 13 weeks = one quarter, long enough to smooth noise, short enough to show drift
    roll_std = ts.rolling(window=13).std()

    final, d_used, rows = difference_until_stationary(ts)

    # ---- sanity check of the ADF test itself (white noise vs random walk), as in Lab 12 practice task 2 ----
    rng = np.random.default_rng(42)
    wn = pd.Series(rng.normal(0, 1, 200))
    rw = wn.cumsum()                                   # a random walk is white noise accumulated -> has a unit root
    rows += [adf_row("Check: white noise", wn), adf_row("Check: random walk", rw), adf_row("Check: random walk, d=1", rw.diff().dropna())]
    # ---- practice task 3: a quadratic trend needs d=2 ----
    t = np.arange(200)
    quad = pd.Series(t ** 2 + rng.normal(0, 1, 200))
    rows += [adf_row("Check: quadratic, d=1", quad.diff().dropna()), adf_row("Check: quadratic, d=2", quad.diff().diff().dropna())]

    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT_DIR, "f1_adf_results.csv"), index=False)
    print(res.to_string(index=False))
    print(f"\nADF-based differencing order for the raw price series: d = {d_used} (ADF only tests for a unit root; it does NOT remove trend/seasonality - see F2/F3)")

    fig, ax = plt.subplots(2, 1, figsize=(11, 7.2))
    ax[0].plot(ts, color=C["blue"], lw=1.5, label="Weekly modal price (simulated benchmark)")
    ax[0].plot(roll_mean, color=C["orange"], lw=2.2, label="13-week rolling mean")
    ax2 = ax[0].twinx(); ax2.grid(False)
    ax2.plot(roll_std, color=C["red"], lw=1.4, ls="--", label="13-week rolling std (right axis)")
    ax[0].set_ylabel("INR / quintal"); ax2.set_ylabel("Rolling std (INR)")
    h1, l1 = ax[0].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax[0].legend(h1 + h2, l1 + l2, loc="upper left")
    ax[0].set_title("A: Rolling mean and standard deviation (visual stationarity check)")
    d1 = ts.diff().dropna()                            # first difference always shown: Lab 12 asks for original vs differenced comparison
    adf_d1 = adf_row("d1", d1)
    ax[1].plot(d1, color=C["green"], lw=1.3)
    ax[1].axhline(0, color=C["grey"], lw=0.8)
    ax[1].set_title(f"B: First difference (week-on-week change)   |   ADF original p = {rows[0]['p_value']:.4f}, ADF first difference p = {adf_d1['p_value']:.4f}")
    ax[1].set_ylabel("Change (INR / quintal)"); ax[1].set_xlabel("Week")
    fig.suptitle("Figure F1: Stationarity Assessment of the Weekly Price Series", fontsize=12, fontweight="bold", y=1.0)
    fig.tight_layout()
    save_fig(fig, "F1_stationarity.png")
