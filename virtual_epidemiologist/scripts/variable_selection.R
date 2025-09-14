
# Load necessary libraries
library(dplyr)
library(readr)

# Load the preprocessed data
data <- read_csv("../output/preprocessed_data.csv")

# Select relevant variables for analysis
selected_data <- data %>%
  select(
    id,
    # Glycemic variability metrics
    glucemia_media_15_19, glucemia_sd_15_19, glucemia_cv_15_19,
    HBa1C_media_15_19, HBa1C_sd_15_19, HBa1C_cv_15_19,
    glucemia_media_20_22, glucemia_sd_20_22, glucemia_cv_20_22,
    HBa1C_media_20_22, HBa1C_sd_20_22, HBa1C_cv_20_22,
    # Demographic variables
    sexo, fecha_nacimiento,
    # Mortality and COVID-19 status
    fecha_fallecimiento, fallecimiento_covid, fallecimiento_no_covid,
    # Comorbidities
    pre_dm, diabetes_tipo_1_min_fecha, diabetes_tipo_2_min_fecha,
    hta_esencial_min_fecha, hta_complicada_min_fecha,
    # Medication use
    insulina_2020, insulina_2021, insulina_2022,
    metformina_2020, metformina_2021, metformina_2022,
    # Pandemic period indicator
    pandemic_period
  )

# Save the selected variables for further analysis
write_csv(selected_data, "../output/selected_variables.csv")