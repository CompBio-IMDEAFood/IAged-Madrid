
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load the selected variables data
selected_data = pd.read_csv('../output/selected_variables.csv')

# Feature Engineering: Calculate additional glycemic variability metrics
def calculate_mage(df, glucose_column):
    # Placeholder function for MAGE calculation
    # In practice, this would involve more complex logic to calculate MAGE
    return df[glucose_column].std()  # Simplified example

# Calculate MAGE for each period
selected_data['MAGE_15_19'] = calculate_mage(selected_data, 'glucemia_media_15_19')
selected_data['MAGE_20_22'] = calculate_mage(selected_data, 'glucemia_media_20_22')

# Interaction terms: Example interaction between GV and insulin use
selected_data['GV_Insulin_Interaction_15_19'] = selected_data['glucemia_cv_15_19'] * selected_data['insulina_2020']
selected_data['GV_Insulin_Interaction_20_22'] = selected_data['glucemia_cv_20_22'] * selected_data['insulina_2022']

# Standardize features for modeling
scaler = StandardScaler()
gv_features = ['glucemia_cv_15_19', 'HBa1C_cv_15_19', 'glucemia_cv_20_22', 'HBa1C_cv_20_22', 'MAGE_15_19', 'MAGE_20_22']
selected_data[gv_features] = scaler.fit_transform(selected_data[gv_features])

# Save the engineered features
selected_data.to_csv('../output/engineered_features.csv', index=False)
