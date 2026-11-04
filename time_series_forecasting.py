"""
Agricultural Commodity Price Forecasting: Simple ARIMA(1, 1, 1) Model
======================================================================
Updated according to SciPy, Matplotlib, and Statsmodels modules.

Pipeline:
1. Historical Series Generation (Pandas DatetimeIndex)
2. Trend Smoothing (SMA and EWMA)
3. Seasonal Decomposition (Observed, Trend, Seasonal, Residual)
4. Stationarity Testing (ADF Test & Differencing)
5. Model Fitting & Forecasting: ARIMA(1, 1, 1)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

# Set clean styling for presentation graphs
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

GRAPHS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphs')
os.makedirs(GRAPHS_DIR, exist_ok=True)

# ==============================================================================
# STEP 1: LOAD BENCHMARK AND PREPARE HISTORICAL TIME-SERIES
# ==============================================================================
def create_commodity_time_series():
    """
    Creates a 104-week (2-year) weekly time series reflecting wholesale price
    movements of Indian staple crops.
    """
    np.random.seed(42)
    dates = pd.date_range(start='2023-05-01', periods=104, freq='W')
    
    # 1. Base price + mild macro inflation trend
    base_price = 1710.0
    trend = base_price + np.linspace(0, 280, 104)
    
    # 2. Agricultural seasonal wave
    t = np.arange(104)
    seasonal = 360 * np.sin(2 * np.pi * t / 52) + 120 * np.cos(4 * np.pi * t / 52)
    
    # 3. Random noise
    noise = np.random.normal(0, 55, 104)
    
    price_series = pd.Series(trend + seasonal + noise, index=dates, name='Modal_Price')
    return price_series

# ==============================================================================
# STEP 2: TREND SMOOTHING (SMA & EWMA)
# ==============================================================================
def run_smoothing(ts):
    """
    Adjusts trend using Simple Moving Average (SMA) and 
    Exponentially Weighted Moving Average (EWMA).
    """
    print("\n--- STEP 2: Trend Smoothing ---")
    sma = ts.rolling(window=12).mean()
    ewma = ts.ewm(span=12, adjust=False).mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(ts, label="Original", alpha=0.5, color='#1f77b4')
    plt.plot(sma, label="SMA (12)", color='#ff7f0e', linewidth=2)
    plt.plot(ewma, label="EWMA (span=12)", color='#2ca02c', linewidth=2)
    
    plt.legend()
    plt.title("Trend Smoothing: SMA vs EWMA")
    plt.grid(True)
    plt.tight_layout()
    
    output_path = os.path.join(GRAPHS_DIR, 'forecast_01_smoothing.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

# ==============================================================================
# STEP 3: SEASONAL DECOMPOSITION
# ==============================================================================
def run_seasonal_decomposition(ts):
    """
    Decomposes the series into Observed, Trend, Seasonal, and Residual.
    """
    print("\n--- STEP 3: Running Seasonal Decomposition ---")
    decomp = seasonal_decompose(ts, model='additive', period=52)
    
    fig = decomp.plot()
    fig.set_size_inches(12, 8)
    plt.suptitle("Seasonal Time-Series Decomposition", fontsize=13, fontweight='bold', y=1.02)
    
    output_path = os.path.join(GRAPHS_DIR, 'forecast_02_seasonal_decomposition.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

# ==============================================================================
# STEP 4: TIME-SERIES STATIONARITY (ADF TEST)
# ==============================================================================
def run_stationarity_check(ts):
    """
    Checks stationarity using Augmented Dickey-Fuller (ADF) test.
    Applies differencing if non-stationary.
    """
    print("\n--- STEP 4: Stationarity Analysis ---")
    
    # 1. ADF Test on raw series
    result_raw = adfuller(ts)
    print(f"Raw Series ADF Statistic: {result_raw[0]:.4f}, p-value: {result_raw[1]:.4f}")
    print("Status:", "Stationary" if result_raw[1] < 0.05 else "Non-stationary")
    
    # 2. First Difference to achieve stationarity
    ts_diff = ts.diff().dropna()
    result_diff = adfuller(ts_diff)
    print(f"Differenced Series ADF Statistic: {result_diff[0]:.4f}, p-value: {result_diff[1]:.4e}")
    print("Status:", "Stationary" if result_diff[1] < 0.05 else "Non-stationary")

# ==============================================================================
# STEP 5: ARIMA(1, 1, 1) TRAINING & FORECASTING
# ==============================================================================
def train_and_forecast_arima(ts):
    """
    Fits ARIMA(1, 1, 1) model and generates forecasts.
    """
    print("\n--- STEP 5: Training ARIMA(1, 1, 1) Model ---")
    
    # Train/Test Split
    train_size = 88
    train = ts.iloc[:train_size]
    test = ts.iloc[train_size:]
    test_len = len(test)
    
    # Fit ARIMA model
    model = ARIMA(train, order=(1, 1, 1))
    fitted_model = model.fit()
    
    # Print statsmodels built-in evaluation summary
    print("\n=== ARIMA MODEL SUMMARY ===")
    print(fitted_model.summary())
    
    # Generate forecast
    forecast = fitted_model.forecast(steps=test_len)
    
    # --------------------------------------------------------------------------
    # FORECAST PLOT
    # --------------------------------------------------------------------------
    print("\nGenerating Forecast Plot...")
    plt.figure(figsize=(14, 6))
    
    plt.plot(train.index, train.values, label='Historical Training Data', color='#2b5c8f')
    plt.plot(test.index, test.values, label='Actual Test Data', color='#111111', marker='o', markersize=4)
    plt.plot(forecast.index, forecast.values, label='ARIMA Forecast', color='red', linewidth=2)
    
    plt.axvline(train.index[-1], color='#e74c3c', linestyle=':', label='Forecast Start')
    
    plt.title("ARIMA(1, 1, 1) Commodity Price Forecast")
    plt.xlabel('Date')
    plt.ylabel('Price (INR/Quintal)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    forecast_plot_path = os.path.join(GRAPHS_DIR, 'forecast_03_arima_forecast.png')
    plt.savefig(forecast_plot_path, dpi=300)
    plt.close()
    print(f"Saved: {forecast_plot_path}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    print("=" * 70)
    print("TIME-SERIES FORECASTING PIPELINE (STATSMODELS)")
    print("=" * 70)
    
    ts = create_commodity_time_series()
    ts = pd.read_csv("cleaned_commodity_prices.csv")  # Load actual data if available
    print(f"Generated benchmark weekly price series: {len(ts)} observations.")
    
    run_smoothing(ts)
    run_seasonal_decomposition(ts)
    run_stationarity_check(ts)
    train_and_forecast_arima(ts)
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"All graphs saved in: {GRAPHS_DIR}")
    print("=" * 70)

if __name__ == '__main__':
    main()