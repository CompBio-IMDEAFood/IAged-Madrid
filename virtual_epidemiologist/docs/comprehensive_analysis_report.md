
# Comprehensive Analysis Report

## Cox Proportional Hazards Model Summary
Call:
coxph(formula = final_formula, data = data)

  n= 530229, number of events= 530229 

                                  coef exp(coef)  se(coef)       z Pr(>|z|)    
glucemia_cv_20_22            -0.035001  0.965605  0.001989 -17.598  < 2e-16 ***
HBa1C_cv_20_22                0.046767  1.047877  0.001552  30.130  < 2e-16 ***
MAGE_20_22                          NA        NA  0.000000      NA       NA    
GV_Insulin_Interaction_20_22  0.014421  1.014526  0.003549   4.064 4.83e-05 ***
sexoM                        -0.213778  0.807527  0.002855 -74.875  < 2e-16 ***
pre_dm1                       0.104886  1.110584  0.003100  33.839  < 2e-16 ***
dm2_dxTRUE                          NA        NA  0.000000      NA       NA    
hta_dxTRUE                          NA        NA  0.000000      NA       NA    
insulina_2022                -0.093223  0.910990  0.006725 -13.861  < 2e-16 ***
---
Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

                             exp(coef) exp(-coef) lower .95 upper .95
glucemia_cv_20_22               0.9656     1.0356    0.9618    0.9694
HBa1C_cv_20_22                  1.0479     0.9543    1.0447    1.0511
MAGE_20_22                          NA         NA        NA        NA
GV_Insulin_Interaction_20_22    1.0145     0.9857    1.0075    1.0216
sexoM                           0.8075     1.2383    0.8030    0.8121
pre_dm1                         1.1106     0.9004    1.1039    1.1174
dm2_dxTRUE                          NA         NA        NA        NA
hta_dxTRUE                          NA         NA        NA        NA
insulina_2022                   0.9110     1.0977    0.8991    0.9231

Concordance= 0.535  (se = 0 )
Likelihood ratio test= 8231  on 6 df,   p=<2e-16
Wald test            = 8422  on 6 df,   p=<2e-16
Score (logrank) test = 8447  on 6 df,   p=<2e-16



## Proportional Hazards Assumption Test
                              test_statistic             p    -log2(p)
GV_Insulin_Interaction_20_22      321.232296  7.806961e-72  236.214062
HBa1C_cv_20_22                     13.755688  2.081894e-04   12.229816
glucemia_cv_20_22                  16.604673  4.603744e-05   14.406833
insulina_2022                    4067.500096  0.000000e+00         inf
pre_dm_1                           77.515715  1.316706e-18   59.397772
sexo_1                            147.903361  4.980305e-34  110.629321

## Sensitivity Analysis
        covariate      coef  exp(coef)  se(coef)  coef lower 95%  coef upper 95%  exp(coef) lower 95%  exp(coef) upper 95%  cmp to          z             p   -log2(p)
glucemia_cv_20_22 -0.013516   0.986574  0.000849       -0.015180       -0.011853             0.984935             0.988217     0.0 -15.924472  4.286152e-57 187.250219
   HBa1C_cv_20_22  0.027098   1.027469  0.000888        0.025359        0.028838             1.025683             1.029258     0.0  30.531076 1.008497e-204 677.661124
    insulina_2022 -0.037867   0.962841  0.003053       -0.043851       -0.031884             0.957097             0.968619     0.0 -12.403793  2.492400e-35 114.949948
           sexo_1 -0.143533   0.866292  0.001873       -0.147204       -0.139862             0.863118             0.869478     0.0 -76.627530  0.000000e+00        inf
         pre_dm_1  0.068884   1.071312  0.001869        0.065220        0.072548             1.067393             1.075244     0.0  36.846332 3.348093e-297 984.869304

## ARIMA Model Summary
                               SARIMAX Results                                
==============================================================================
Dep. Variable:                      y   No. Observations:               530229
Model:                 ARIMA(1, 1, 1)   Log Likelihood             -751267.582
Date:                Sat, 13 Sep 2025   AIC                        1502541.164
Time:                        15:02:33   BIC                        1502574.707
Sample:                             0   HQIC                       1502550.636
                             - 530229                                         
Covariance Type:                  opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ar.L1          0.0011      0.001      0.769      0.442      -0.002       0.004
ma.L1         -0.9933      0.000  -6256.080      0.000      -0.994      -0.993
sigma2         0.9959      0.002    505.321      0.000       0.992       1.000
===================================================================================
Ljung-Box (L1) (Q):                   0.00   Jarque-Bera (JB):             52435.77
Prob(Q):                              1.00   Prob(JB):                         0.00
Heteroskedasticity (H):               0.96   Skew:                             0.77
Prob(H) (two-sided):                  0.00   Kurtosis:                         2.93
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).

## Collaboration and Clinical Insights
- Continuous collaboration with clinical experts ensured the clinical relevance of our findings.
- Feedback loops with geriatricians and pharmacologists helped interpret results in the context of elderly care.
- The integration of clinical insights was crucial for aligning analytical approaches with clinical priorities.

## Future Directions
- Further exploration of non-linear relationships and interaction terms.
- Consideration of additional temporal analysis techniques.
- Ongoing collaboration with clinical teams to refine and validate findings.
