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
    report.pdf
    report.tex
    summary_metrics.csv
  scripts/
    analyze_ab_test.py
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
