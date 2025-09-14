# --- Paquetes ---
library(survival)
library(dplyr)
library(readr)
library(forcats)
library(stringr)
library(rlang)

# --- Carga ---
data <- read_csv("../output/engineered_features.csv", show_col_types = FALSE)

# --- Fechas base ---
data <- data %>%
  mutate(
    fecha_nacimiento   = as.Date(fecha_nacimiento),
    fecha_fallecimiento= as.Date(fecha_fallecimiento)
  )

# 1) Construir fecha de censura/último contacto
#    Tomamos la última fecha disponible por fila entre TODAS las columnas Date (excepto nacimiento y fallecimiento).
date_cols <- names(data)[sapply(data, inherits, what = "Date")]
date_cols_to_scan <- setdiff(date_cols, c("fecha_nacimiento", "fecha_fallecimiento"))

# si no hubiera otras fechas, usa una fecha fin de estudio (ajusta si sabes la real)
study_end <- as.Date("2022-12-31")

if (length(date_cols_to_scan) == 0) {
  data$last_obs <- study_end
} else {
  data <- data %>%
    rowwise() %>%
    mutate(
      last_obs = suppressWarnings(
        max(c_across(all_of(date_cols_to_scan)), na.rm = TRUE)
      )
    ) %>%
    ungroup() %>%
    mutate(last_obs = ifelse(is.infinite(last_obs), NA, last_obs) %>% as.Date(origin = "1970-01-01"))
  
  # si alguna fila no tiene ninguna otra fecha, censúrala en study_end
  data$last_obs[is.na(data$last_obs)] <- study_end
}

# 2) Tiempo de seguimiento y evento
data <- data %>%
  mutate(
    exit_date = if_else(!is.na(fecha_fallecimiento), fecha_fallecimiento, last_obs),
    event     = !is.na(fecha_fallecimiento),
    time_years = as.numeric(difftime(exit_date, fecha_nacimiento, units = "days"))/365.25
  ) %>%
  filter(!is.na(time_years), time_years > 0)

# 3) Variables de la fórmula: convertir fechas de diagnóstico a indicadores
data <- data %>%
  mutate(
    dm2_dx  = !is.na(diabetes_tipo_2_min_fecha),
    hta_dx  = !is.na(hta_esencial_min_fecha)
  )

# 4) Factores limpios
data <- data %>%
  mutate(
    # ajusta según tus codificaciones reales
    sexo = case_when(
      is.numeric(sexo) ~ if_else(sexo == 1, "M", "F"),
      TRUE ~ as.character(sexo)
    ) %>% factor() %>% fct_drop(),
    pandemic_period = as.factor(pandemic_period) %>% fct_drop(),
    pre_dm = if (is.numeric(pre_dm)) factor(pre_dm) else as.factor(pre_dm)
  )

# 5) Construir fórmula sin columnas fecha crudas
base_formula <- as.formula(
  "Surv(time_years, event) ~ glucemia_cv_20_22 + HBa1C_cv_20_22 + MAGE_20_22 +
   GV_Insulin_Interaction_20_22 + sexo + pre_dm + dm2_dx + hta_dx +
   insulina_2022 + pandemic_period"
)

# 6) Quitar de la fórmula cualquier factor con <2 niveles (evita contrasts error)
mf <- model.frame(base_formula, data = data, na.action = na.pass)
is_fac <- sapply(mf, is.factor)
bad_fac <- names(which(sapply(mf[ , is_fac, drop=FALSE], nlevels) < 2))

final_terms <- attr(terms(base_formula), "term.labels")
final_terms <- setdiff(final_terms, bad_fac)  # sacar factores problemáticos

final_formula <- reformulate(final_terms, response = "Surv(time_years, event)")

# 7) Ajuste Cox
cox_model <- coxph(final_formula, data = data)
cox_summary <- summary(cox_model)

# 8) Guardados
dir.create("../output", showWarnings = FALSE, recursive = TRUE)
sink("../output/cox_model_summary.txt"); print(cox_summary); sink()
saveRDS(cox_model, "../output/cox_model.rds")

# 9) Mensaje útil
message("Factores removidos por tener <2 niveles: ",
        paste(bad_fac, collapse = ", "))
message("Fórmula final: ", deparse(final_formula))

broom::tidy(cox_model) %>% write_csv("../output/cox_model_tidy.csv")
