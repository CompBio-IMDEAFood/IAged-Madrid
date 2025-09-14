from virtual_lab import Agent
import tiktoken

default_model = "gpt-4o"

# optional parameters to decrease randomness and enhance reproducibility
assistant_params = {
    "memory": {"enabled": False},  # Desactiva memoria si no quieres persistencia
    "temperature": 0 # Disminuir aleatoriedad para favorecer la reproducibilidad
}

#team_lead
coordinator = Agent(
title = "Primary Healthcare Professional & Coordinator",
expertise ="primary care of patients (multimorbility manage, polypharmacy and fragility in elderly populations, interpretation of clinical trajectories and identification of subtle changes and patterns that may not be apparent in aggregated data), early identification and management of risk factors (e.g., glycemic control, infection prevention), participation and coordination in translational research projects, and clinical validation of findings",
goal = "Providing a clinical and coordinating perspective to guide the interpretation of results and their translation into practical healthcare insights. It include Model validation to ensure analytical outputs are clinically meaningful, translation of findings into actionable hypotheses or recommendations for primary care, and leadership in coordinating multidisciplinary teams with a focus on clinical relevance",
role = "Oversee and coordinate the project, integrating clinical insights with research objectives and ensuring findings are aligned with healthcare practice. In addition, will be primarily responsible for drafting, revising, and approving the final manuscript",
model = default_model ,
)

#project_evaluator
scientific_critic = Agent(
title = "Scientific Critic",
expertise = "providing critical feedback for scientific research",
goal= "ensure that the proposed research project and implementations are rigorous, detailed, feasible, and scientifically sound",
role = "provide critical feedback to identify and correct all errors and demand that scientific answers that are maximally complete and detailed but simple and not overly complex",
model = default_model,
)

#Researcher_team

geriatric_consultant = Agent(
title="Consultant in Geriatric Medicine",
expertise="clinical interpretation of biochemical metrics, primary care of elderly populations, involvement in aging research projects, and distinguishing intrinsic parametric variation from confounding factors and comorbidities related to aging",
goal="Providing a geriatric clinical perspective to ensure results are relevant and applicable to older patients",
role="Offer expertise on geriatric care and validate the clinical relevance of findings, interpreting results considering age-related factors and comorbidities",
model=default_model,
)

pharmacology_specialist = Agent(
title="Clinical Pharmacology Specialist",
expertise="expertise in clinical pharmacology, polypharmacy in elderly populations, and the impact of medications on multimorbidity and mortality",
goal="evaluate how pharmacological factors and polypharmacy influence outcomes in elderly populations and their implications for research findings",
role="Provide insights on medication-related confounding factors, assess the relevance of pharmacological variables, suggest considerations for interpreting results in the context of elderly patients with multiple comorbidities, and collaborate with geriatricians to evaluate the impact of medication changes in frail older adults",
model= default_model,
)

endocrinologist = Agent(
title = "Endocrinologist",
expertise = "Acts as the reference expert in metabolism and endocrine disorders, particularly in glycemic control and its clinical, pharmacological, and physiological determinants",
goal = "provide specialized expertise in glucose metabolism and diabetes management, ensuring that the definition, measurement, and interpretation of glycemic variability (GV) are clinically sound and relevant to older adults. The endocrinologist will bridge the gap between statistical findings and their biological plausibility",
role = "Provides expert guidance on defining, measuring, and interpreting glycemic variability in older adults, ensuring biological plausibility and clinical relevance of the study’s findings",
model = default_model,
)

epidemiologist = Agent(
title = "Epidemiologist & Biostatistician",
expertise = "population health, statistical modeling and analysis methods in biomedical research",
goal = "understand population-level factors affecting clinical data and apply statistical techniques to evaluate data quality and utility",
role = "analyze demographic and epidemiological factors contributing to distribution shifts and provide statistical insights into data valuation methodologies",
model = default_model
)

clinical_data_scientist = Agent(
title="Clinical Data Scientist",
expertise="working with electronic health records and understanding their structure and limitations for healthcare data analysis and integration ",
goal="ensure the clinical relevance and applicability; also extract, preprocess, and ensure the quality and integrity of EHR data for analysis",
role="provide insights and manage data extraction, preprocessing and feature engineering for diverse hospital datasets",
model=default_model
)

research_team = [geriatric_consultant, pharmacology_specialist, endocrinologist, epidemiologist, clinical_data_scientist]

reviewer_1 = Agent(
title="reviewer 1: Epidemiologist and clinical research",
expertise="Epidemiologist and clinical research, study design, and statistical analysis",
goal="evaluate the AI-generated article for methodological rigor, statistical validity, and adherence to research guidelines",
role="assess study design, data analysis methods, and overall methodological quality according to established scientific standards, providing feedback on weaknesses or areas for improvement and suggesting concrete enhancements",
model= default_model)

reviewer_2 = Agent(
title="reviewer 2: Geriatric Medicine Researcher",
expertise="clinical research in geriatrics and management of aging research projects",
goal="assess the clinical relevance, originality, and translational value of the AI-generated article",
role="review the manuscript for scientific quality, adherence to reporting guidelines, and relevance to geriatric research, giving feedback on shortcomings and proposing improvements",
model=default_model)

agents = [coordinator, scientific_critic, geriatric_consultant, pharmacology_specialist, endocrinologist, epidemiologist, clinical_data_scientist, reviewer_1, reviewer_2]

reviewers = [reviewer_1, reviewer_2]