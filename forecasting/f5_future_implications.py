"""
F5 - Quantifying the three future implications (farmer alerts, mandi cold storage, government early warning)
Uses the REAL cross-sectional data (storage ranking, Kerala/UP gap) and the SIMULATED weekly series (alert back-test, seasonal calendar).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from common import build_weekly_series, load_cleaned, save_fig, OUT_DIR, PERIOD, TEST_WEEKS, C
from f3_arima_forecast import seasonal_pattern

LEAD = 4            # weeks of advance warning tested (about one month)
HOLD_THR = 1.05     # advise 'wait' if the 4-week-ahead forecast is >= 5 % above today (assumed alert rule)

if __name__ == "__main__":
    out = {}
    # ---------- 1. FARMER: rolling-origin back-test of a 4-week-ahead price alert ----------
    ts = build_weekly_series(); n = len(ts); start = n - TEST_WEEKS
    sp = seasonal_pattern(ts.iloc[:start])                              # seasonal factors learned from training weeks only (no look-ahead)
    recs = []
    for o in range(start, n - LEAD):                                    # origin = last known week index o-1
        hist = ts.iloc[:o]; adj = hist / np.resize(sp, o)
        f = ARIMA(adj, order=(1, 1, 2)).fit().forecast(LEAD).values[-1] * np.resize(sp, o + LEAD)[-1]
        now, actual = hist.iloc[-1], ts.iloc[o + LEAD - 1]
        recs.append({"Week": hist.index[-1], "Price_now": now, "Forecast_4w": f, "Actual_4w": actual})
    bt = pd.DataFrame(recs).set_index("Week")
    bt["Alert"] = np.where(bt.Forecast_4w >= bt.Price_now * HOLD_THR, "WAIT", np.where(bt.Forecast_4w <= bt.Price_now / HOLD_THR, "SELL NOW", "NO ACTION"))
    bt["Dir_correct"] = np.sign(bt.Forecast_4w - bt.Price_now) == np.sign(bt.Actual_4w - bt.Price_now)
    bt["Gain_if_follow"] = np.where(bt.Alert == "WAIT", bt.Actual_4w - bt.Price_now, np.where(bt.Alert == "SELL NOW", bt.Price_now - bt.Actual_4w, np.nan))
    bt.round(1).to_csv(os.path.join(OUT_DIR, "f5_alert_backtest.csv"))
    act = bt.dropna(subset=["Gain_if_follow"])
    out.update(backtest_origins=len(bt), direction_hit_rate_pct=bt.Dir_correct.mean() * 100,
               mape_4w_pct=(abs(bt.Forecast_4w - bt.Actual_4w) / bt.Actual_4w).mean() * 100,
               alerts_issued=len(act), alert_success_pct=(act.Gain_if_follow > 0).mean() * 100 if len(act) else np.nan,
               avg_gain_per_alert_inr_q=act.Gain_if_follow.mean() if len(act) else np.nan)
    print(bt.round(0).to_string()); print({k: round(v, 2) for k, v in out.items()})

    # ---------- 2. MANDI: cold-storage priority from REAL spreads ----------
    df = load_cleaned()
    g = df.groupby("Commodity", observed=True).agg(Records=("Spread_Pct", "size"), Mean_Spread_Pct=("Spread_Pct", "mean"),
                                                   Mean_Spread_INR=("Price_Spread", "mean"), Pct_Records_Over_20=("Spread_Pct", lambda s: (s > 20).mean() * 100))
    g = g[g.Records >= 15].sort_values("Mean_Spread_Pct", ascending=False).head(10).round(1)
    g.to_csv(os.path.join(OUT_DIR, "f5_storage_priority.csv"))
    print(g.to_string())

    # ---------- 3. GOVERNMENT: Kerala vs UP price gap + seasonal release / procurement calendar ----------
    rows = []
    for c in ["Tomato", "Onion", "Potato", "Brinjal", "Green Chilli"]:
        k = df[(df.Commodity == c) & (df.State == "Kerala")].Modal_Price; u = df[(df.Commodity == c) & (df.State == "Uttar Pradesh")].Modal_Price
        _, p = stats.mannwhitneyu(k, u)
        rows.append({"Commodity": c, "Kerala_mean": k.mean(), "UP_mean": u.mean(), "Ratio": k.mean() / u.mean(), "Gap_INR_q": k.mean() - u.mean(), "n_Kerala": len(k), "n_UP": len(u), "MannWhitney_p": p})
    gap = pd.DataFrame(rows).round(3); gap.to_csv(os.path.join(OUT_DIR, "f5_interstate_gap.csv"), index=False); print(gap.to_string(index=False))
    seas = pd.read_csv(os.path.join(OUT_DIR, "f2_seasonal_by_month.csv"), index_col=0)["Seasonal_index"]
    seas.to_frame().assign(Action=np.where(seas >= 1.15, "Release buffer stock", np.where(seas <= 0.88, "Procure / store", "Monitor"))).to_csv(os.path.join(OUT_DIR, "f5_seasonal_calendar.csv"))
    pd.Series(out).to_csv(os.path.join(OUT_DIR, "f5_summary.csv"), header=["value"])

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
    a = ax[0]; a.plot(bt.index, bt.Price_now, color=C["blue"], label="Price at alert date"); a.plot(bt.index, bt.Actual_4w, color=C["black"], marker="o", ms=3, label="Actual price 4 weeks later")
    a.plot(bt.index, bt.Forecast_4w, color=C["orange"], lw=2, label="4-week-ahead forecast")
    w = bt[bt.Alert == "WAIT"]; s = bt[bt.Alert == "SELL NOW"]
    a.scatter(w.index, w.Price_now, marker="^", color=C["green"], s=60, zorder=5, label="WAIT alert"); a.scatter(s.index, s.Price_now, marker="v", color=C["red"], s=60, zorder=5, label="SELL NOW alert")
    a.set_title(f"A: Farmer alert back-test (direction hit rate {out['direction_hit_rate_pct']:.0f} %)"); a.legend(fontsize=7.5); a.tick_params(axis="x", rotation=30, labelsize=8)
    b = ax[1]; gg = g.sort_values("Mean_Spread_Pct"); b.barh(gg.index, gg.Mean_Spread_Pct, color=C["maroon"], alpha=.85); b.axvline(20, color=C["grey"], ls="--")
    b.set_title("B: Cold-storage priority - mean intra-market spread %"); b.set_xlabel("Spread %"); b.tick_params(axis="y", labelsize=8)
    c_ = ax[2]; m = seas.values; cols = [C["red"] if v >= 1.15 else C["green"] if v <= 0.88 else C["grey"] for v in m]
    c_.bar([x[:3] for x in seas.index], (m - 1) * 100, color=cols); c_.axhline(0, color="k", lw=.8)
    c_.set_title("C: Seasonal price effect - red: release stock, green: procure"); c_.set_ylabel("% vs trend")
    fig.suptitle("Figure F6: Evidence Behind the Three Future Implications", fontsize=12, fontweight="bold"); fig.tight_layout(); save_fig(fig, "F6_future_implications.png")
