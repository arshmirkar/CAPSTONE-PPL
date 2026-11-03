# Final Evaluation Results: Agricultural Commodity Price Forecasting
## Undergraduate Capstone Project: Time-Series & ARIMA(1, 1, 1) Modeling

**Benchmark Commodity:** Onion / Tomato Wholesale Mandi Prices  
**Historical Period:** 104 Weeks (2-Year Agricultural Cycle: May 2023 – April 2025)  
**Train / Test Split:** 88 Weeks Train (85%) / 16 Weeks Test (15%)  
**Benchmark Price Level:** Calibrated to Agmarknet Benchmark (~₹1,710/Quintal) from `cleaned_commodity_price.csv`

---

## 1. Final Model Performance Evaluation Table

The **ARIMA(1, 1, 1)** model was trained on the first 88 historical weeks and tested on the 16 unseen test weeks:

| Model | Order $(p, d, q)$ | MAE (₹/Quintal) | RMSE (₹/Quintal) | MAPE (%) | Accuracy (%) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **ARIMA** | **(1, 1, 1)** | **₹166.19** | **₹203.10** | **9.45%** | **90.55%** |

*Note: The raw numbers are saved in [`final_forecast_results.csv`](final_forecast_results.csv).*

---

## 2. Key Findings & Metric Interpretations (In Plain English)

* **MAE = ₹166.19 / Quintal:**  
  On average, our ARIMA model's weekly price forecast is off by around ₹166 on a commodity selling at ₹1,700–₹2,000 per quintal. That is an average error of only **₹1.66 per kilogram**!
* **RMSE = ₹203.10 / Quintal:**  
  Because RMSE is close to MAE, it confirms that the model does not produce wild, crazy forecast errors.
* **MAPE = 9.45%:**  
  The Mean Absolute Percentage Error is under 10%, which is considered a **solid, reliable forecast** in agricultural economics.
* **Accuracy = 90.55%:**  
  The model achieves **over 90% forecast accuracy** over a 16-week forward horizon.

---

## 3. The 3 Forecasting Graphs Generated in `graphs/`

| Figure # | Filename | What It Shows |
|:---:|---|---|
| **Figure F1** | [`forecast_01_seasonal_decomposition.png`](graphs/forecast_01_seasonal_decomposition.png) | Separates the price into Observed (actuals), Trend (inflation), and Seasonality (annual crop cycle). |
| **Figure F2** | [`forecast_02_model_identification_acf_pacf.png`](graphs/forecast_02_model_identification_acf_pacf.png) | ADF test proves the series is stationary ($p = 0.042$), and ACF/PACF plots confirm $p=1, q=1$. |
| **Figure F3** | [`forecast_03_price_forecast.png`](graphs/forecast_03_price_forecast.png) | Historical training data (blue), Actual test prices (black dots), and ARIMA(1, 1, 1) forecast line (orange) with 95% confidence band. |

---

## 4. Final Conclusion

The **ARIMA(1, 1, 1)** model provides a clean, easily explainable tool for agricultural price forecasting. With **over 90% accuracy**, it provides a solid foundation for farmer price advisories and government buffer stock planning.
