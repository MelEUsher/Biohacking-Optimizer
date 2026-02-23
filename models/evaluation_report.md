# Model Evaluation Report

## Metrics Table

| model | mse | mae | rmse | r2 |
| --- | --- | --- | --- | --- |
| Linear Regression | 1.5341 | 1.0108 | 1.2386 | 0.1819 |
| Gradient Boosting | 1.6527 | 1.0652 | 1.2856 | 0.1187 |
| Random Forest | 1.6928 | 1.0631 | 1.3011 | 0.0973 |

## Best Model Selection

Best Model: **Linear Regression**

Justification: Linear Regression has the highest R² (0.1819) with RMSE 1.2386 and MAE 1.0108. It leads the next-best model by 0.0632 R².

## Residual Analysis Summary

- Mean residual: -0.0317
- Standard deviation of residuals: 1.2382
- Normality test: Shapiro-Wilk
- p-value: 0.7700
- Distribution notes: Residuals are approximately normal at alpha=0.05 (test statistic=0.9925).

## Error Distribution Observations

Residual mean suggests minimal bias; residual variability shows wider spread. No large residual outliers detected.
