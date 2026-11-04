"""
Shared helpers for the forecasting package (Lab 11 SciPy + Lab 12 Statsmodels concepts).

IMPORTANT - about the data:
    commodity_price.csv is a ONE-DAY snapshot (19 May 2025), so it contains no
    price history. The real cross-sectional data is used for the statistical
    tests (f4) and the implications (f5). For the time-series work (f1-f3) a
    clearly-labelled SIMULATED weekly benchmark series is built, anchored to the
    real mean Onion price in the dataset. Results from the simulated series show
    how the method behaves; they must be re-run on real weekly Agmarknet prices
    before they are used for any decision.
"""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "forecasting", "figures")
OUT_DIR = os.path.join(ROOT, "forecasting", "outputs")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

N_WEEKS = 156        # 3 full years: seasonal_decompose needs >= 2 full 52-week cycles in the TRAIN part too
TEST_WEEKS = 24      # ~15 % hold-out; covers the autumn peak -> spring trough swing
PERIOD = 52          # weekly data with an annual harvest cycle
SEED = 42

plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.edgecolor": "#cccccc", "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": "#e6e6e6", "grid.linestyle": "--", "grid.alpha": 0.8,
    "axes.titleweight": "bold", "axes.titlesize": 10.5, "axes.labelsize": 9.5,
    "legend.fontsize": 8.5, "figure.dpi": 100,
})
C = {"blue": "#2b5c8f", "orange": "#e67e22", "green": "#2e8b57", "red": "#c0392b",
     "grey": "#7f8c8d", "black": "#111111", "maroon": "#9b0000"}


def load_cleaned():
    """Real cleaned mandi data + the engineered spread metrics used in the report."""
    df = pd.read_csv(os.path.join(ROOT, "cleaned_commodity_price.csv"))
    df["Price_Spread"] = df["Max_Price"] - df["Min_Price"]
    df["Spread_Pct"] = np.where(df["Modal_Price"] > 0, df["Price_Spread"] / df["Modal_Price"] * 100, 0)
    return df


def build_weekly_series():
    """
    104+ weeks of simulated weekly Onion benchmark price (INR/quintal).
    Multiplicative structure: Price = Trend x Seasonal x Noise
    (multiplicative because the seasonal swing of a price scales with its level,
    exactly like the airline-passenger series in Lab 12).
    Anchored to the REAL mean Onion modal price of the cleaned dataset.
    """
    df = load_cleaned()
    base = df.loc[df["Commodity"] == "Onion", "Modal_Price"].mean()   # ~ INR 1,711 / quintal
    rng = np.random.default_rng(SEED)
    t = np.arange(N_WEEKS)
    dates = pd.date_range(end="2025-04-27", periods=N_WEEKS, freq="W-SUN")
    trend = base * (0.88 + 0.24 * t / (N_WEEKS - 1))                       # +~27 % drift over 3 years (inflation)
    # Onion prices peak in the post-monsoon lean season (Oct-Nov) and bottom out at rabi arrivals (Mar-Apr)
    peak_week = int((pd.Timestamp("2022-10-16") - dates[0]).days // 7) % PERIOD
    seasonal = 1 + 0.22 * np.cos(2 * np.pi * (t - peak_week) / PERIOD) + 0.05 * np.cos(4 * np.pi * (t - peak_week) / PERIOD)
    noise = np.exp(rng.normal(0, 0.03, N_WEEKS))                           # ~3 % market-arrival noise
    return pd.Series(trend * seasonal * noise, index=dates, name="Modal_Price").round(2)


def metrics(actual, pred):
    """MAE, RMSE, MAPE and 100-MAPE (the report's 'accuracy')."""
    a, p = np.asarray(actual, float), np.asarray(pred, float)
    mae = np.mean(np.abs(a - p))
    rmse = np.sqrt(np.mean((a - p) ** 2))
    mape = np.mean(np.abs((a - p) / a)) * 100
    return {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "MAPE_%": round(mape, 2), "100-MAPE_%": round(100 - mape, 2)}


def save_fig(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", os.path.relpath(path, ROOT))
