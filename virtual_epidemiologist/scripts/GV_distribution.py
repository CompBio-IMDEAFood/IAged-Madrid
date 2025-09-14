# -*- coding: utf-8 -*-
"""
Analysis of between-individual variability (not time series)
- Requires: ../output/engineered_features.csv
- Assumes columns: glucemia_media_15_19, glucemia_media_20_22
- Optionally uses 'patient_id' if present, otherwise creates one from the index.
- Generates: CSVs with stats, plots, and a text report.
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ------------------------- Config -------------------------
INPUT_CSV = '../output/engineered_features.csv'
OUT_DIR   = '../output'
COL_P1    = 'glucemia_media_15_19'
COL_P2    = 'glucemia_media_20_22'
PATIENT_ID_COL = 'patient_id'  # if not present, it will be created

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------- Label mapping ----------------------
pretty_labels = {
    COL_P1: "Average glucose (15–19)",
    COL_P2: "Average glucose (20–22)",
    "delta_20_22_vs_15_19": "Delta glucose (20–22 vs 15–19)",
    "mean_glucose": "Overall average glucose"
}

def label(colname):
    return pretty_labels.get(colname, colname.replace("_", " "))

# ----------------------- Load data ----------------------
df = pd.read_csv(INPUT_CSV)

if PATIENT_ID_COL not in df.columns:
    df[PATIENT_ID_COL] = np.arange(len(df))

df_use = df[[PATIENT_ID_COL, COL_P1, COL_P2]].copy()
df_use = df_use.replace([np.inf, -np.inf], np.nan).dropna(subset=[COL_P1, COL_P2])

df_use["delta_20_22_vs_15_19"] = df_use[COL_P2] - df_use[COL_P1]
df_use["mean_glucose"] = df_use[[COL_P1, COL_P2]].mean(axis=1)

# --------------------- Distribution plots -------------------
plt.figure(figsize=(10,6))
plt.hist(df_use[COL_P1].dropna(), bins=40, alpha=0.6, label=label(COL_P1), density=True)
plt.hist(df_use[COL_P2].dropna(), bins=40, alpha=0.6, label=label(COL_P2), density=True)
plt.title("Distribution of average glucose by period")
plt.xlabel("Average glucose")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "dist_periods_hist.png"))
plt.close()

plt.figure(figsize=(8,6))
plt.boxplot([df_use[COL_P1].dropna(), df_use[COL_P2].dropna()],
            labels=[label(COL_P1), label(COL_P2)], showmeans=True)
plt.title("Boxplots by period")
plt.ylabel("Average glucose")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "boxplots_periods.png"))
plt.close()

plt.figure(figsize=(8,6))
plt.violinplot([df_use[COL_P1].dropna(), df_use[COL_P2].dropna()], showmeans=True, showextrema=True)
plt.xticks([1,2],[label(COL_P1), label(COL_P2)])
plt.title("Violin plots by period")
plt.ylabel("Average glucose")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "violin_periods.png"))
plt.close()

plt.figure(figsize=(8,6))
plt.hist(df_use["delta_20_22_vs_15_19"].dropna(), bins=40, density=True)
plt.title(label("delta_20_22_vs_15_19"))
plt.xlabel("Delta of average glucose")
plt.ylabel("Density")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "dist_delta_hist.png"))
plt.close()
