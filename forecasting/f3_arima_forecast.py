"""
F3 - ARIMA model identification (ACF/PACF, AIC), seasonal-adjusted ARIMA forecast, validation, future forecast
(Lab 12: Task 3 + practice task 5)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from common import build_weekly_series, metrics, save_fig, OUT_DIR, PERIOD, TEST_WEEKS, C

HORIZON = 16   # weeks forecast beyond the last observation

def seasonal_pattern(series):
    """52 multiplicative seasonal factors (week-of-cycle) estimated ONLY from the series passed in."""
    return seasonal_decompose(series, model="multiplicative", period=PERIOD).seasonal.values[:PERIOD]

def fit_best_arima(y, d):
    """Grid-search p,q in 0..2 with fixed d and keep the lowest AIC (Lab 12 practice task 5)."""
    rows = [(p, d, q, ARIMA(y, order=(p, d, q)).fit().aic) for p in range(3) for q in range(3) if not (p == 0 and q == 0)]
    tab = pd.DataFrame(rows, columns=["p", "d", "q", "AIC"]).sort_values("AIC").reset_index(drop=True)
    b = tab.iloc[0]
    return ARIMA(y, order=(int(b.p), d, int(b.q))).fit(), tab

def choose_d(y):
    """d = 0/1/2: smallest order whose ADF p-value < 0.05 (justified by the ADF null of a unit root)."""
    for d in range(3):
        x = y if d == 0 else y.diff(d).dropna()
        if adfuller(x)[1] < 0.05:
            return d, adfuller(x)[1]
    return 2, adfuller(y.diff(2).dropna())[1]

def seasonal_adjusted_forecast(series, steps, start_pos):
    """Deseasonalise -> ARIMA -> reseasonalise. Returns mean, lower, upper, model, aic table, d."""
    sp = seasonal_pattern(series)
    adj = series / np.resize(sp, len(series))                         # remove the annual cycle so ARIMA only models trend + noise
    d, p_adf = choose_d(adj)
    model, tab = fit_best_arima(adj, d)
    fc = model.get_forecast(steps)
    f = np.resize(np.roll(sp, 0), start_pos + steps)[start_pos:]       # seasonal factors for the forecast weeks
    ci = fc.conf_int(alpha=0.05)
    return fc.predicted_mean.values * f, ci.iloc[:, 0].values * f, ci.iloc[:, 1].values * f, model, tab, d, p_adf, adj

if __name__ == "__main__":
    ts = build_weekly_series()
    n = len(ts); tr, te = ts.iloc[:n - TEST_WEEKS], ts.iloc[n - TEST_WEEKS:]
    print(f"Train {tr.index[0].date()} -> {tr.index[-1].date()} ({len(tr)} wk) | Test {te.index[0].date()} -> {te.index[-1].date()} ({len(te)} wk)")

    mean, lo, hi, model, aic_tab, d, p_adf, adj = seasonal_adjusted_forecast(tr, TEST_WEEKS, len(tr))
    print(f"ADF on the seasonally adjusted TRAIN series -> d = {d} (p of the stationary version = {p_adf:.4f})")
    print(aic_tab.round(2).to_string(index=False))
    order = model.model.order; print("Selected order (lowest AIC):", order, " AIC =", round(model.aic, 2))
    aic_tab.round(2).to_csv(os.path.join(OUT_DIR, "f3_aic_comparison.csv"), index=False)

    # ACF / PACF of the stationary (differenced) adjusted series -> justify p and q visually
    stat = adj.diff(d).dropna() if d else adj
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(stat, lags=26, ax=ax[0], color=C["blue"], title="A: ACF (suggests q)")
    plot_pacf(stat, lags=26, ax=ax[1], color=C["green"], method="ywm", title="B: PACF (suggests p)")
    for a in ax: a.set_xlabel("Lag (weeks)")
    fig.suptitle(f"Figure F3: Model Identification on the Seasonally Adjusted Series (d = {d})", fontsize=12, fontweight="bold")
    fig.tight_layout(); save_fig(fig, "F3_acf_pacf.png")

    # --- validation against baselines ---
    naive = np.repeat(tr.iloc[-1], TEST_WEEKS)
    snaive = ts.iloc[n - TEST_WEEKS - PERIOD: n - PERIOD].values        # same weeks one year earlier
    raw = ARIMA(tr, order=(1, 1, 1)).fit().forecast(TEST_WEEKS).values  # plain non-seasonal ARIMA(1,1,1) on the raw series
    rows = {f"Seasonal-adjusted ARIMA{order}": mean, "Plain ARIMA(1,1,1) on raw series": raw,
            "Seasonal naive (same week last year)": snaive, "Naive (last observed value)": naive}
    val = pd.DataFrame({k: metrics(te.values, v) for k, v in rows.items()}).T
    val.to_csv(os.path.join(OUT_DIR, "f3_validation_metrics.csv")); print(val.to_string())

    # --- final model on the full series -> forecast beyond the data ---
    fm, flo, fhi, fmod, _, fd, _, _ = seasonal_adjusted_forecast(ts, HORIZON, n)
    fdates = pd.date_range(ts.index[-1] + pd.Timedelta(weeks=1), periods=HORIZON, freq="W-SUN")
    fut = pd.DataFrame({"Forecast": fm, "Lower_95": flo, "Upper_95": fhi}, index=fdates).round(1)
    fut.to_csv(os.path.join(OUT_DIR, "f3_future_forecast.csv"), index_label="Week"); print(fut.to_string())
    print("Final model order:", fmod.model.order)

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    a = ax[0]
    a.plot(tr.iloc[-60:], color=C["blue"], label="Training (last 60 wk shown)")
    a.plot(te, color=C["black"], marker="o", ms=3.5, lw=1.8, label="Actual hold-out")
    a.plot(te.index, mean, color=C["orange"], lw=2.2, label=f"Seasonal-adjusted ARIMA{order}")
    a.fill_between(te.index, lo, hi, color=C["orange"], alpha=.2, label="95% interval")
    a.plot(te.index, raw, color=C["red"], ls="--", lw=1.4, label="Plain ARIMA(1,1,1)")
    a.plot(te.index, naive, color=C["grey"], ls=":", lw=1.6, label="Naive")
    a.axvline(tr.index[-1], color=C["red"], ls=":", lw=1)
    a.set_title(f"A: {TEST_WEEKS}-week hold-out validation"); a.set_ylabel("INR / quintal"); a.legend(loc="lower left", fontsize=7.5); a.tick_params(axis="x", rotation=30, labelsize=8)
    b = ax[1]
    b.plot(ts.iloc[-52:], color=C["blue"], label="Last 52 weeks (simulated)")
    b.plot(fut["Forecast"], color=C["orange"], lw=2.2, marker="o", ms=3, label=f"{HORIZON}-week forecast")
    b.fill_between(fut.index, fut["Lower_95"], fut["Upper_95"], color=C["orange"], alpha=.2, label="95% interval")
    b.set_title(f"B: {HORIZON}-week forecast beyond the last observation"); b.legend(loc="upper left"); b.tick_params(axis="x", rotation=30, labelsize=8)
    fig.suptitle("Figure F4: ARIMA on the Seasonally Adjusted Series - Validation and Forecast", fontsize=12, fontweight="bold")
    fig.tight_layout(); save_fig(fig, "F4_forecast.png")
