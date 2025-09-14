
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler

# Load the engineered features data
data = pd.read_csv('../output/engineered_features.csv')

# Create a time series for glycemic variability metrics
# Example: Use the mean glucose levels over time
time_series_data = data[['glucemia_media_15_19', 'glucemia_media_20_22']].mean(axis=1)

# Standardize the time series data
scaler = StandardScaler()
time_series_scaled = scaler.fit_transform(time_series_data.values.reshape(-1, 1)).flatten()

# Fit an ARIMA model
arima_model = ARIMA(time_series_scaled, order=(1, 1, 1))
arima_result = arima_model.fit()

# Plot the time series and ARIMA model fit
plt.figure(figsize=(10, 6))
plt.plot(time_series_scaled, label='Standardized Glucose Levels', color='blue')
plt.plot(arima_result.fittedvalues, label='ARIMA Fit', color='red')
plt.title('Time Series Analysis of Glycemic Variability')
plt.xlabel('Time')
plt.ylabel('Standardized Glucose Levels')
plt.legend()
plt.savefig('../output/time_series_analysis.png')
plt.close()

# Save ARIMA model summary
with open('../output/arima_model_summary.txt', 'w') as f:
    f.write(str(arima_result.summary()))
