from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

DAILY_USERS = 100_000
ANALYSIS_DAYS = 30
REVENUE_PER_CONVERSION = 75.0
GROSS_MARGIN = 0.40
ALPHA = 0.05
POWER = 0.80
Z_ALPHA_TWO_SIDED = 1.959963984540054
Z_POWER_80 = 0.8416212335729143


def read_experiment_results() -> dict[str, str]:
    with (REPORTS_DIR / "experiment_results.csv").open(encoding="utf-8", newline="") as f:
        return {row[0]: row[1] for row in csv.reader(f) if row and row[0]}


def monthly_impact(lift: float) -> tuple[float, float]:
    conversion_delta = lift * DAILY_USERS * ANALYSIS_DAYS
    gross_profit_delta = conversion_delta * REVENUE_PER_CONVERSION * GROSS_MARGIN
    return conversion_delta, gross_profit_delta


def sample_size_per_group(baseline_rate: float, mde: float) -> int:
    variance = 2 * baseline_rate * (1 - baseline_rate)
    n = variance * (Z_ALPHA_TWO_SIDED + Z_POWER_80) ** 2 / mde**2
    return math.ceil(n)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    metrics = read_experiment_results()
    baseline_rate = float(metrics["control_conversion_rate"])
    observed_lift = float(metrics["absolute_lift"])
    ci_low = float(metrics["ci_low"])
    ci_high = float(metrics["ci_high"])

    observed_conversions, observed_profit = monthly_impact(observed_lift)
    low_conversions, low_profit = monthly_impact(ci_low)
    high_conversions, high_profit = monthly_impact(ci_high)

    assumptions = [
        {"assumption": "daily_users_after_rollout", "value": DAILY_USERS},
        {"assumption": "analysis_horizon_days", "value": ANALYSIS_DAYS},
        {"assumption": "revenue_per_conversion_usd", "value": REVENUE_PER_CONVERSION},
        {"assumption": "gross_margin", "value": GROSS_MARGIN},
        {"assumption": "alpha", "value": ALPHA},
        {"assumption": "power", "value": POWER},
    ]
    write_csv(REPORTS_DIR / "risk_assumptions.csv", assumptions)

    impact_rows = [
        {
            "scenario": "Observed effect",
            "lift_pp": observed_lift * 100,
            "monthly_conversion_delta": round(observed_conversions),
            "monthly_gross_profit_delta_usd": round(observed_profit),
            "decision_read": "Expected impact if observed effect persists",
        },
        {
            "scenario": "95% CI lower bound",
            "lift_pp": ci_low * 100,
            "monthly_conversion_delta": round(low_conversions),
            "monthly_gross_profit_delta_usd": round(low_profit),
            "decision_read": "Downside risk if the new page is worse",
        },
        {
            "scenario": "95% CI upper bound",
            "lift_pp": ci_high * 100,
            "monthly_conversion_delta": round(high_conversions),
            "monthly_gross_profit_delta_usd": round(high_profit),
            "decision_read": "Upside if the new page is modestly better",
        },
    ]
    write_csv(REPORTS_DIR / "business_impact_scenarios.csv", impact_rows)

    mdes = [0.0025, 0.005, 0.01]
    sample_size_rows = []
    for mde in mdes:
        per_group = sample_size_per_group(baseline_rate, mde)
        sample_size_rows.append(
            {
                "mde_pp": mde * 100,
                "users_per_group": per_group,
                "total_users": per_group * 2,
                "alpha": ALPHA,
                "power": POWER,
                "baseline_conversion_rate": baseline_rate,
            }
        )
    write_csv(REPORTS_DIR / "sample_size_plan.csv", sample_size_rows)

    print("Risk analysis complete")
    print(f"Observed monthly gross profit impact: ${observed_profit:,.0f}")
    print(f"95% downside risk: ${low_profit:,.0f}")
    print(f"95% upside case: ${high_profit:,.0f}")


if __name__ == "__main__":
    main()
