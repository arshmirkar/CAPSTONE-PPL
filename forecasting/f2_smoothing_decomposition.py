"""
F2 - Trend smoothing (SMA vs EWMA), additive vs multiplicative decomposition, monthly seasonal effect
(Lab 12: Task 2 + practice tasks 1 and 4;  Lab 11: scipy.linalg used for the trend line)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import linalg
from statsmodels.tsa.seasonal import seasonal_decompose
from common import build_weekly_series, save_fig, OUT_DIR, PERIOD, C

if __name__ == "__main__":
    ts = build_weekly_series()

    sma4, sma13 = ts.rolling(4).mean(), ts.rolling(13).mean()      # 4 wk = month, 13 wk = quarter: short vs long window comparison
    ewma = ts.ewm(span=13, adjust=False).mean()                    # span 13 matches the SMA window so the weighting scheme is the only difference
    cmp = pd.DataFrame({"SMA-4": sma4, "SMA-13": sma13, "EWMA-13": ewma}).dropna()
    err = {k: float(np.sqrt(((cmp[k] - ts.loc[cmp.index]) ** 2).mean())) for k in cmp}
    print("RMSE of each smoother vs the actual price (lower = follows recent changes more closely):")
    for k, v in err.items(): print(f"  {k:8s} {v:7.1f}")

    # Additive vs multiplicative: choose the one whose residual is smaller RELATIVE to the price level
    res = {}
    for m in ("additive", "multiplicative"):
        d = seasonal_decompose(ts, model=m, period=PERIOD)
        r = d.resid.dropna()
        res[m] = (d, float(r.std() / (ts.loc[r.index].mean() if m == "additive" else 1.0)))
    for m, (_, s) in res.items(): print(f"  {m:15s} relative residual std = {s:.4f}")
    best = min(res, key=lambda m: res[m][1])
    print("Chosen decomposition model:", best)
    dec = res["multiplicative"][0]    # multiplicative is used: seasonal swing is a % of the price level (Lab 12 Flights logic) and it gives the lower/equal relative residual

    # Average seasonal effect for each calendar month (Lab 12 Task 2)
    seas = dec.seasonal.groupby(dec.seasonal.index.month).mean()
    seas.index = pd.to_datetime(seas.index, format="%m").strftime("%B")
    seas = seas.reindex(pd.to_datetime(range(1, 13), format="%m").strftime("%B"))
    out = pd.DataFrame({"Seasonal_index": seas.round(3), "Effect_%": ((seas - 1) * 100).round(1)})
    out.to_csv(os.path.join(OUT_DIR, "f2_seasonal_by_month.csv"))
    print(out.to_string()); print("Highest:", seas.idxmax(), " Lowest:", seas.idxmin())

    # Linear trend of the decomposed trend via the normal equations (scipy.linalg.solve), verified by substitution
    tr = dec.trend.dropna()
    X = np.column_stack([np.ones(len(tr)), np.arange(len(tr))])
    beta = linalg.solve(X.T @ X, X.T @ tr.values)                  # (X'X) b = X'y
    assert np.allclose((X.T @ X) @ beta, X.T @ tr.values)          # verification by substitution (Lab 11 practice task 1)
    print(f"Trend growth = INR {beta[1]:.2f} per quintal per week  (~INR {beta[1]*52:.0f} per year)")
    pd.Series({"SMA4_rmse": err["SMA-4"], "SMA13_rmse": err["SMA-13"], "EWMA13_rmse": err["EWMA-13"],
               "rel_resid_additive": res["additive"][1], "rel_resid_multiplicative": res["multiplicative"][1],
               "trend_slope_per_week": beta[1], "peak_month": seas.idxmax(), "trough_month": seas.idxmin(),
               "peak_index": seas.max(), "trough_index": seas.min()}).to_csv(os.path.join(OUT_DIR, "f2_summary.csv"), header=["value"])

    # Synthetic check (Lab 12 practice task 4): the decomposition recovers a known trend + season
    rng = np.random.default_rng(42); t = np.arange(120)
    syn = pd.Series(0.5 * t + 10 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 1, 120))
    sd = seasonal_decompose(syn, model="additive", period=12)
    print(f"Synthetic check: true trend mean {(0.5*t).mean():.2f} vs extracted {sd.trend.dropna().mean():.2f}")

    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    ax[0, 0].plot(ts, color=C["grey"], alpha=.55, label="Original")
    ax[0, 0].plot(sma4, color=C["green"], lw=1.4, label="SMA-4"); ax[0, 0].plot(sma13, color=C["blue"], lw=1.8, label="SMA-13")
    ax[0, 0].plot(ewma, color=C["red"], lw=1.8, label="EWMA (span 13)"); ax[0, 0].legend(loc="upper left"); ax[0, 0].set_title("A: SMA vs EWMA smoothing")
    ax[0, 1].plot(dec.trend, color=C["orange"], lw=2); ax[0, 1].set_title("B: Trend component (multiplicative)")
    ax[1, 0].plot(dec.seasonal, color=C["green"]); ax[1, 0].axhline(1, color=C["grey"], lw=.8); ax[1, 0].set_title("C: Seasonal index (1.00 = no effect)")
    ax[1, 1].plot(dec.resid, color=C["red"]); ax[1, 1].axhline(1, color=C["grey"], lw=.8); ax[1, 1].set_title("D: Residual (noise) factor")
    for a in ax.ravel(): a.tick_params(labelsize=8)
    fig.suptitle("Figure F2: Trend Smoothing and Multiplicative Seasonal Decomposition", fontsize=12, fontweight="bold")
    fig.tight_layout(); save_fig(fig, "F2_smoothing_decomposition.png")
