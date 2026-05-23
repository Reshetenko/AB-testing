# A/B Testing Portfolio Case

This project analyzes whether a new e-commerce landing page improves conversion compared with the existing page.

## Project Structure

```text
ab_testing_case/
  data/
    ab_data.csv
  dashboard/
    index.html
  figures/
    conversion_rate_by_group.svg
    daily_conversion_trend.svg
    report_conversion_rate_by_group.png
    report_daily_conversion_trend.png
  reports/
    ab_testing_case_study.md
    daily_conversion.csv
    experiment_results.csv
    business_impact_scenarios.csv
    report.pdf
    report.tex
    risk_assumptions.csv
    sample_size_plan.csv
    summary_metrics.csv
  scripts/
    analyze_ab_test.py
    analyze_decision_risk.py
    render_report_charts.py
```

## Business Question

Should the company roll out the new landing page to all users?

## Result

The new landing page did not produce a statistically significant improvement in conversion.

| Metric | Result |
|---|---:|
| Control conversion rate | 12.04% |
| Treatment conversion rate | 11.88% |
| Absolute lift | -0.158 percentage points |
| p-value | 0.190 |
| 95% confidence interval | [-0.394 pp, +0.078 pp] |

Recommendation: keep the old page and do not launch the new page as-is.

## Decision Risk

The project also includes a business risk layer that translates the statistical result into rollout impact and next-test planning.

Using explicit assumptions of 100,000 daily users, a 30-day horizon, $75 revenue per conversion, and 40% gross margin:

| Scenario | Monthly gross profit impact |
|---|---:|
| Observed effect persists | -$142,041 |
| 95% downside case | -$354,411 |
| 95% upside case | +$70,328 |

The risk analysis supports the same recommendation: do not roll out the new page as-is. The upside is limited and statistically uncertain, while the downside risk is materially larger.

## Dashboard

Open the dashboard directly in a browser:

```text
dashboard/index.html
```

The dashboard is self-contained and does not require a local web server.

## PDF Report

The final English PDF report is available at:

```text
reports/report.pdf
```

## Reproduce the Analysis

Run:

```bash
/Users/mult/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/analyze_ab_test.py
```

from inside the `ab_testing_case` folder, or run:

```bash
/Users/mult/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ab_testing_case/scripts/analyze_ab_test.py
```

from the workspace root.

To regenerate the PNG charts used in the PDF report, run:

```bash
/Users/mult/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/render_report_charts.py
```

from inside the `ab_testing_case` folder.

To regenerate the decision risk outputs, run:

```bash
/Users/mult/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/analyze_decision_risk.py
```

from inside the `ab_testing_case` folder.
