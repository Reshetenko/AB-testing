from __future__ import annotations

import html
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ab_data.csv"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "figures"


def normal_two_sided_p_value(z_score: float) -> float:
    return math.erfc(abs(z_score) / math.sqrt(2))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def bar_chart_svg(data: list[tuple[str, float]], title: str, y_label: str) -> str:
    width, height = 760, 430
    margin_left, margin_right, margin_top, margin_bottom = 82, 38, 58, 72
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    max_val = max(v for _, v in data) * 1.18
    bar_w = chart_w / len(data) * 0.54
    gap = chart_w / len(data)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="{margin_left}" y="32" font-family="Arial" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>',
        f'<text x="18" y="{height / 2}" transform="rotate(-90 18 {height / 2})" font-family="Arial" font-size="13" fill="#5f6368">{html.escape(y_label)}</text>',
        f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#9aa0a6" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#9aa0a6" stroke-width="1"/>',
    ]
    colors = ["#2f6f73", "#b45309"]
    for i, (label, value) in enumerate(data):
        x = margin_left + i * gap + (gap - bar_w) / 2
        bar_h = chart_h * value / max_val
        y = height - margin_bottom - bar_h
        parts.extend(
            [
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="{colors[i % len(colors)]}"/>',
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#202124">{value:.2%}</text>',
                f'<text x="{x + bar_w / 2:.1f}" y="{height - margin_bottom + 30}" text-anchor="middle" font-family="Arial" font-size="15" fill="#202124">{html.escape(label)}</text>',
            ]
        )
    for tick in range(5):
        tick_val = max_val * tick / 4
        y = height - margin_bottom - chart_h * tick / 4
        parts.extend(
            [
                f'<line x1="{margin_left - 5}" y1="{y:.1f}" x2="{margin_left}" y2="{y:.1f}" stroke="#9aa0a6" stroke-width="1"/>',
                f'<text x="{margin_left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#5f6368">{tick_val:.1%}</text>',
                f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#eceff1" stroke-width="1"/>',
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts)


def line_chart_svg(daily: pd.DataFrame, title: str) -> str:
    width, height = 860, 430
    margin_left, margin_right, margin_top, margin_bottom = 76, 36, 58, 78
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    dates = sorted(daily["date"].unique())
    y_min = daily["conversion_rate"].min() * 0.88
    y_max = daily["conversion_rate"].max() * 1.08

    def xy(date, value):
        idx = dates.index(date)
        x = margin_left + chart_w * idx / max(1, len(dates) - 1)
        y = margin_top + chart_h * (y_max - value) / (y_max - y_min)
        return x, y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="{margin_left}" y="32" font-family="Arial" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>',
        f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#9aa0a6" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#9aa0a6" stroke-width="1"/>',
    ]
    for tick in range(5):
        tick_val = y_min + (y_max - y_min) * tick / 4
        y = margin_top + chart_h * (y_max - tick_val) / (y_max - y_min)
        parts.extend(
            [
                f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#eceff1" stroke-width="1"/>',
                f'<text x="{margin_left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#5f6368">{tick_val:.1%}</text>',
            ]
        )
    color_by_group = {"control": "#2f6f73", "treatment": "#b45309"}
    for group, group_df in daily.groupby("group"):
        points = [xy(row["date"], row["conversion_rate"]) for _, row in group_df.sort_values("date").iterrows()]
        path = " ".join([("M" if i == 0 else "L") + f" {x:.1f} {y:.1f}" for i, (x, y) in enumerate(points)])
        parts.append(f'<path d="{path}" fill="none" stroke="{color_by_group[group]}" stroke-width="3"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color_by_group[group]}"/>')
    for i, date in enumerate(dates):
        if i % 3 == 0 or i == len(dates) - 1:
            x, _ = xy(date, y_min)
            parts.append(f'<text x="{x:.1f}" y="{height - margin_bottom + 28}" text-anchor="middle" font-family="Arial" font-size="11" fill="#5f6368">{date[5:]}</text>')
    parts.extend(
        [
            '<rect x="630" y="54" width="14" height="14" fill="#2f6f73"/>',
            '<text x="652" y="66" font-family="Arial" font-size="13" fill="#202124">Control</text>',
            '<rect x="720" y="54" width="14" height="14" fill="#b45309"/>',
            '<text x="742" y="66" font-family="Arial" font-size="13" fill="#202124">Treatment</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    valid_assignment = (
        ((df["group"] == "control") & (df["landing_page"] == "old_page"))
        | ((df["group"] == "treatment") & (df["landing_page"] == "new_page"))
    )
    clean = df.loc[valid_assignment].drop_duplicates("user_id", keep="first").copy()
    clean["date"] = clean["timestamp"].dt.strftime("%Y-%m-%d")

    summary = clean.groupby("group")["converted"].agg(users="count", conversions="sum", conversion_rate="mean")
    n_control = int(summary.loc["control", "users"])
    n_treatment = int(summary.loc["treatment", "users"])
    x_control = int(summary.loc["control", "conversions"])
    x_treatment = int(summary.loc["treatment", "conversions"])
    p_control = x_control / n_control
    p_treatment = x_treatment / n_treatment
    lift_abs = p_treatment - p_control
    lift_rel = lift_abs / p_control

    pooled = (x_control + x_treatment) / (n_control + n_treatment)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n_control + 1 / n_treatment))
    z_score = lift_abs / se_pooled
    p_value = normal_two_sided_p_value(z_score)
    se_unpooled = math.sqrt(
        p_control * (1 - p_control) / n_control + p_treatment * (1 - p_treatment) / n_treatment
    )
    ci_low = lift_abs - 1.96 * se_unpooled
    ci_high = lift_abs + 1.96 * se_unpooled

    daily = (
        clean.groupby(["date", "group"])["converted"]
        .agg(users="count", conversions="sum", conversion_rate="mean")
        .reset_index()
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(REPORTS_DIR / "summary_metrics.csv")
    daily.to_csv(REPORTS_DIR / "daily_conversion.csv", index=False)

    write_text(
        FIGURES_DIR / "conversion_rate_by_group.svg",
        bar_chart_svg(
            [("Control: old page", p_control), ("Treatment: new page", p_treatment)],
            "Conversion Rate by Experiment Group",
            "Conversion rate",
        ),
    )
    write_text(
        FIGURES_DIR / "daily_conversion_trend.svg",
        line_chart_svg(daily, "Daily Conversion Rate During the Experiment"),
    )

    metrics = {
        "raw_rows": len(df),
        "clean_rows": len(clean),
        "removed_invalid_or_duplicate_rows": len(df) - len(clean),
        "start_date": clean["timestamp"].min().strftime("%Y-%m-%d"),
        "end_date": clean["timestamp"].max().strftime("%Y-%m-%d"),
        "control_users": n_control,
        "treatment_users": n_treatment,
        "control_conversion_rate": p_control,
        "treatment_conversion_rate": p_treatment,
        "absolute_lift": lift_abs,
        "relative_lift": lift_rel,
        "z_score": z_score,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }
    pd.Series(metrics).to_csv(REPORTS_DIR / "experiment_results.csv", header=["value"])

    print("Analysis complete")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
