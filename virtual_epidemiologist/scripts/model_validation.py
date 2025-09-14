import os
import time
from pathlib import Path

import pandas as pd
import numpy as np

# Backend no interactivo (evita bloqueos)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

OUTDIR = Path("../output")
OUTDIR.mkdir(parents=True, exist_ok=True)

t0 = time.time()
print("== INICIO ==", flush=True)

# ---------------------------
# 1) Cargar datos y preparar tiempo/evento
# ---------------------------
data = pd.read_csv("../output/engineered_features.csv")

# Asegura tipos fecha si existen
for col in ["fecha_nacimiento", "fecha_fallecimiento",
            "diabetes_tipo_2_min_fecha", "hta_esencial_min_fecha"]:
    if col in data.columns:
        data[col] = pd.to_datetime(data[col], errors="coerce")

# EVENTO: fallecimiento (True si hay fecha)
data["event"] = data["fecha_fallecimiento"].notna()

# DURACIÓN (años):
if "age_at_event" in data.columns and np.isfinite(data["age_at_event"]).any():
    data["duration_years"] = data["age_at_event"]
else:
    study_end = pd.Timestamp("2022-12-31")
    exit_date = data["fecha_fallecimiento"].fillna(study_end)
    data["duration_years"] = (exit_date - data["fecha_nacimiento"]).dt.days / 365.25

print("A) limpieza_basica", flush=True)
# Limpieza básica
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna(subset=["duration_years"])
data = data[data["duration_years"] > 0]

# ---------------------------
# 2) Covariables (alineadas con tu modelo en R)
# ---------------------------
num_covs = [
    "glucemia_cv_20_22",
    "HBa1C_cv_20_22",
    "MAGE_20_22",
    "GV_Insulin_Interaction_20_22",
    "insulina_2022",
]

cat_covs = []
for col in ["sexo", "pre_dm", "pandemic_period"]:
    if col in data.columns:
        cat_covs.append(col)

# Indicadores a partir de fechas de diagnóstico
if "diabetes_tipo_2_min_fecha" in data.columns:
    data["dm2_dx"] = data["diabetes_tipo_2_min_fecha"].notna()
    cat_covs.append("dm2_dx")
if "hta_esencial_min_fecha" in data.columns:
    data["hta_dx"] = data["hta_esencial_min_fecha"].notna()
    cat_covs.append("hta_dx")

cols_keep = ["duration_years", "event"] + num_covs + cat_covs
cols_keep = [c for c in cols_keep if c in data.columns]
df = data[cols_keep].copy()

# Coerción
for c in num_covs:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

for c in cat_covs:
    if c in df.columns and df[c].dtype != bool:
        df[c] = df[c].astype("category")

df = df.dropna(subset=["duration_years", "event"])

print("B) one-hot_encoding", flush=True)
df_model = pd.get_dummies(df, columns=[c for c in cat_covs if c in df.columns], drop_first=True)

# Elimina columnas constantes
constant_cols = [c for c in df_model.columns
                 if c not in ["duration_years", "event"] and df_model[c].nunique(dropna=True) < 2]
if constant_cols:
    print("   - columnas constantes eliminadas:", constant_cols[:10], "..." if len(constant_cols) > 10 else "", flush=True)
    df_model = df_model.drop(columns=constant_cols)

print(f"   - shape df_model: {df_model.shape}", flush=True)
print(f"   - eventos: {int(df_model['event'].sum())} / N={len(df_model)} (ratio={df_model['event'].mean():.4f})", flush=True)

# ---------------------------
# 3) Ajuste Cox
# ---------------------------
print("C) Ajuste Cox", flush=True)
cph = CoxPHFitter(penalizer=0.5, l1_ratio=0.0)   # ridge suave
cph.fit(df_model, duration_col="duration_years", event_col="event",
        robust=False, show_progress=True)
cph.summary.to_parquet(OUTDIR / "lifelines_cox_summary.parquet", index=False)
print("cox in parquet")

cph.summary.to_csv(OUTDIR / "lifelines_cox_summary.csv", index=False)
print("   - Cox FIT OK en %.2fs" % (time.time() - t0), flush=True)

# ---------------------------
# 4) Test de Proporcionalidad (subconjunto top-k)
# ---------------------------
print("D) PH test (subconjunto)", flush=True)
try:
    top_k = 20
    summ = cph.summary.copy()
    if "z" in summ.columns:
        summ = summ.assign(abs_z=lambda d: d["z"].abs())
        top_covs = summ.sort_values("abs_z", ascending=False).head(top_k).index.tolist()
    else:
        top_covs = list(cph.params_.index)[:top_k]

    covs_for_test = ["duration_years", "event"] + [c for c in top_covs if c in df_model.columns]
    df_ph = df_model[covs_for_test].copy()

    t_ph = time.time()
    ph_test = proportional_hazard_test(cph, df_ph, time_transform="rank")
    with open(OUTDIR / "proportional_hazards_test_top20.txt", "w", encoding="utf-8") as f:
        f.write(str(ph_test.summary))
    print("   - PH test OK en %.2fs (k=%d)" % (time.time() - t_ph, len(top_covs)), flush=True)
except Exception as e:
    print("   ! PH test saltado por error:", repr(e), flush=True)

# ---------------------------
# 5) Residuales de Schoenfeld (gráficos, subset)
# ---------------------------
print("E) Schoenfeld residuals (subset)", flush=True)
try:
    schoen = cph.compute_residuals(df_model, kind="schoenfeld")
    covs_to_plot = [c for c in top_covs if c in schoen.columns][:12]  # máx 12 plots

    for cov in covs_to_plot:
        plt.figure(figsize=(7, 4))
        schoen[cov].sort_index().plot()
        plt.title(f"Schoenfeld residuals: {cov}")
        plt.xlabel("Orden temporal")
        plt.ylabel("Residual")
        plt.tight_layout()
        plt.savefig(OUTDIR / f"schoenfeld_{cov}.png")
        plt.close()
    print(f"   - {len(covs_to_plot)} gráficos guardados", flush=True)
except Exception as e:
    print("   ! Residuales saltados por error:", repr(e), flush=True)

# ---------------------------
# 6) Sensibilidad: sin la interacción
# ---------------------------
print("F) Sensibilidad (sin interacción)", flush=True)
try:
    if "GV_Insulin_Interaction_20_22" in df_model.columns:
        df_sens = df_model.drop(columns=["GV_Insulin_Interaction_20_22"])
    else:
        df_sens = df_model.copy()

    cph_sens = CoxPHFitter(penalizer=0.5, l1_ratio=0.0)
    t_sens = time.time()
    cph_sens.fit(df_sens, duration_col="duration_years", event_col="event",
                 robust=True, show_progress=True)
    cph_sens.summary.to_csv(OUTDIR / "sensitivity_analysis.csv", index=True)
    print("   - Sensibilidad OK en %.2fs" % (time.time() - t_sens), flush=True)
except Exception as e:
    print("   ! Sensibilidad saltada por error:", repr(e), flush=True)

print("== FIN en %.2fs ==" % (time.time() - t0), flush=True)
