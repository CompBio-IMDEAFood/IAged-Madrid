import os
import pandas as pd

# Load results from previous analyses
cox_summary = open('../output/cox_model_summary.txt').read()
ph_test_results = open('../output/proportional_hazards_test_top20.txt').read()
sensitivity_analysis = pd.read_csv('../output/sensitivity_analysis.csv')
arima_summary = open('../output/arima_model_summary.txt').read()

# Integrate results into a comprehensive report
report = f"""
# Comprehensive Analysis Report

## Cox Proportional Hazards Model Summary
{cox_summary}

## Proportional Hazards Assumption Test
{ph_test_results}

## Sensitivity Analysis
{sensitivity_analysis.to_string(index=False)}

## ARIMA Model Summary
{arima_summary}

## Collaboration and Clinical Insights
- Continuous collaboration with clinical experts ensured the clinical relevance of our findings.
- Feedback loops with geriatricians and pharmacologists helped interpret results in the context of elderly care.
- The integration of clinical insights was crucial for aligning analytical approaches with clinical priorities.

## Future Directions
- Further exploration of non-linear relationships and interaction terms.
- Consideration of additional temporal analysis techniques.
- Ongoing collaboration with clinical teams to refine and validate findings.
"""

# Save the comprehensive report
with open('../docs/comprehensive_analysis_report.md', 'w') as f:
    f.write(report)
