"""Run the whole forecasting package in order:  python forecasting/run_all.py"""
import runpy, os
here = os.path.dirname(os.path.abspath(__file__))
for f in ["f1_stationarity", "f2_smoothing_decomposition", "f3_arima_forecast", "f4_statistical_tests", "f5_future_implications"]:
    print("\n" + "=" * 20, f, "=" * 20)
    runpy.run_path(os.path.join(here, f + ".py"), run_name="__main__")
