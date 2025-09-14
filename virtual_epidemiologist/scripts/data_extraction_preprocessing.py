
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Create necessary directories if they don't exist
os.makedirs('../output', exist_ok=True)
os.makedirs('../docs', exist_ok=True)
os.makedirs('../logs', exist_ok=True)

# Load CSV files into DataFrames
bioquimicas_df = pd.read_csv('../raw_data/bioquimicas.csv')
pacientes_df = pd.read_csv('../raw_data/pacientes.csv')
farmacos_df = pd.read_csv('../raw_data/farmacos.csv')
enfermedades_df = pd.read_csv('../raw_data/enfermedades.csv')

# Merge DataFrames on 'id'
merged_df = bioquimicas_df.merge(pacientes_df, on='id', how='left')
merged_df = merged_df.merge(farmacos_df, on='id', how='left')
merged_df = merged_df.merge(enfermedades_df, on='id', how='left')

# Handle missing values
# Impute missing values with median for numerical columns
for column in merged_df.select_dtypes(include=[np.number]).columns:
    merged_df[column].fillna(merged_df[column].median(), inplace=True)

# Impute missing values with mode for categorical columns
for column in merged_df.select_dtypes(include=[object]).columns:
    merged_df[column].fillna(merged_df[column].mode()[0], inplace=True)

# Handle outliers using IQR method
def handle_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
    df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])

# Apply outlier handling to relevant columns
for column in ['glucemia_media_15_19', 'HBa1C_media_15_19', 'glucemia_media_20_22', 'HBa1C_media_20_22']:
    handle_outliers(merged_df, column)

# Structure temporal data
# Convert date columns to datetime
date_columns = [col for col in merged_df.columns if 'fecha' in col]
for col in date_columns:
    merged_df[col] = pd.to_datetime(merged_df[col], errors='coerce')

# Align data points to a common timeline
# Example: Create a column for pandemic period
merged_df['pandemic_period'] = np.where(merged_df['glucemia_ult_deter_20_22'].notnull(), 'pandemic', 'pre-pandemic')

# Save the preprocessed data
merged_df.to_csv('../output/preprocessed_data.csv', index=False)
