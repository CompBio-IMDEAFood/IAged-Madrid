# survival_analysis_quartiles.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, statistics

# =========================
# Load data
# =========================
data = pd.read_csv("../output/engineered_features.csv")

# Convert dates to datetime
data['fecha_fallecimiento'] = pd.to_datetime(data['fecha_fallecimiento'], errors='coerce')
data['fecha_nacimiento'] = pd.to_datetime(data['fecha_nacimiento'], errors='coerce')

# Study cutoff date
fecha_corte = pd.to_datetime("2022-12-31")

# Calculate follow-up time in years
data['follow_up_time'] = np.where(
    data['fecha_fallecimiento'].notnull(),
    (data['fecha_fallecimiento'] - data['fecha_nacimiento']).dt.days / 365.25,
    (fecha_corte - data['fecha_nacimiento']).dt.days / 365.25
)

# Event: 1 if died, 0 if censored
data['event'] = np.where(data['fecha_fallecimiento'].notnull(), 1, 0)

# =========================
# Quartiles of glycemic variability
# =========================
var_metric = "glucemia_cv_20_22"   # change here if you want another metric
data['quartile'] = pd.qcut(
    data[var_metric], 4,
    labels=["Q1 (low GV)", "Q2", "Q3", "Q4 (high GV)"]
)

# =========================
# Kaplan–Meier
# =========================
kmf = KaplanMeierFitter()
plt.figure(figsize=(8, 6))

# Silence pandas FutureWarning by setting observed=True
for quartile, group in data.groupby("quartile", observed=True):
    kmf.fit(durations=group["follow_up_time"],
            event_observed=group["event"],
            label=str(quartile))
    kmf.plot_survival_function(ci_show=False)  # no CI for clarity

plt.title("Kaplan–Meier Survival Curves by Quartiles of GV", fontsize=14)
plt.xlabel("Time (years)", fontsize=12)
plt.ylabel("Survival Probability", fontsize=12)
plt.legend(title="GV Quartiles", fontsize=10)
plt.grid(alpha=0.3)

# =========================
# Statistical test (log-rank test)
# =========================
q1 = data[data['quartile'] == "Q1 (low GV)"]
q4 = data[data['quartile'] == "Q4 (high GV)"]

results = statistics.logrank_test(
    q1["follow_up_time"], q4["follow_up_time"],
    event_observed_A=q1["event"], event_observed_B=q4["event"]
)

print("Comparison Q1 vs Q4:")
print(results.summary)

# =========================
# Add results table inside the plot
# =========================
table_data = [
    ["Comparison", "Test statistic", "p-value"],
    ["Q1 vs Q4", f"{results.test_statistic:.2f}", f"{results.p_value:.2e}"]
]

plt.table(cellText=table_data,
          cellLoc='center',
          loc='lower left',
          colWidths=[0.25, 0.25, 0.25])

plt.tight_layout()
plt.savefig("../output/kaplan_meier_curves_with_table.png", dpi=300)
plt.show()
