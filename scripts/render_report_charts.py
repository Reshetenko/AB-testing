from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "figures"

CONTROL = "#2f6f73"
TREATMENT = "#b45309"
TEXT = "#202124"
MUTED = "#5f6368"
GRID = "#e8ecef"
BG = "#fbfbf8"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def text_size(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    text_font: ImageFont.ImageFont,
    fill: str = TEXT,
) -> None:
    width, height = text_size(draw, value, text_font)
    draw.text((xy[0] - width / 2, xy[1] - height / 2), value, font=text_font, fill=fill)


def read_summary() -> list[dict[str, str]]:
    with (REPORTS_DIR / "summary_metrics.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_daily() -> list[dict[str, str]]:
    with (REPORTS_DIR / "daily_conversion.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def render_bar_chart() -> None:
    rows = read_summary()
    data = [
        {
            "label": "Control: old page",
            "rate": float(next(row for row in rows if row["group"] == "control")["conversion_rate"]),
            "color": CONTROL,
        },
        {
            "label": "Treatment: new page",
            "rate": float(next(row for row in rows if row["group"] == "treatment")["conversion_rate"]),
            "color": TREATMENT,
        },
    ]

    width, height = 1400, 760
    margin_left, margin_right, margin_top, margin_bottom = 130, 60, 120, 130
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    max_val = max(item["rate"] for item in data) * 1.18

    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((margin_left, 40), "Conversion Rate by Experiment Group", font=font(42, True), fill=TEXT)

    axis_y = height - margin_bottom
    draw.line((margin_left, margin_top, margin_left, axis_y), fill="#9aa0a6", width=2)
    draw.line((margin_left, axis_y, width - margin_right, axis_y), fill="#9aa0a6", width=2)

    for tick in range(5):
        tick_val = max_val * tick / 4
        y = axis_y - chart_h * tick / 4
        draw.line((margin_left, y, width - margin_right, y), fill=GRID, width=2)
        draw.text((48, y - 14), f"{tick_val * 100:.1f}%", font=font(26), fill=MUTED)

    slot = chart_w / len(data)
    bar_w = slot * 0.46
    for i, item in enumerate(data):
        x = margin_left + i * slot + (slot - bar_w) / 2
        bar_h = chart_h * item["rate"] / max_val
        y = axis_y - bar_h
        draw.rounded_rectangle((x, y, x + bar_w, axis_y), radius=10, fill=item["color"])
        draw_centered_text(draw, (x + bar_w / 2, y - 34), pct(item["rate"]), font(36, True))
        draw_centered_text(draw, (x + bar_w / 2, axis_y + 48), item["label"], font(30))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(FIGURES_DIR / "report_conversion_rate_by_group.png", quality=95)


def render_line_chart() -> None:
    rows = read_daily()
    dates = sorted({row["date"] for row in rows})
    values = [float(row["conversion_rate"]) for row in rows]
    y_min = min(values) * 0.94
    y_max = max(values) * 1.05

    width, height = 1500, 760
    margin_left, margin_right, margin_top, margin_bottom = 130, 70, 120, 120
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom

    def xy(date: str, value: float) -> tuple[float, float]:
        x = margin_left + chart_w * dates.index(date) / max(1, len(dates) - 1)
        y = margin_top + chart_h * (y_max - value) / (y_max - y_min)
        return x, y

    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((margin_left, 40), "Daily Conversion Rate During the Experiment", font=font(42, True), fill=TEXT)

    axis_y = height - margin_bottom
    draw.line((margin_left, margin_top, margin_left, axis_y), fill="#9aa0a6", width=2)
    draw.line((margin_left, axis_y, width - margin_right, axis_y), fill="#9aa0a6", width=2)

    for tick in range(5):
        tick_val = y_min + (y_max - y_min) * tick / 4
        y = margin_top + chart_h * (y_max - tick_val) / (y_max - y_min)
        draw.line((margin_left, y, width - margin_right, y), fill=GRID, width=2)
        draw.text((48, y - 14), f"{tick_val * 100:.1f}%", font=font(26), fill=MUTED)

    for i, date in enumerate(dates):
        if i % 4 == 0 or i == len(dates) - 1:
            draw_centered_text(draw, (xy(date, y_min)[0], axis_y + 46), date[5:], font(25), MUTED)

    groups = [("control", CONTROL, "Control"), ("treatment", TREATMENT, "Treatment")]
    for group, color, _ in groups:
        group_rows = [row for row in rows if row["group"] == group]
        points = [xy(row["date"], float(row["conversion_rate"])) for row in group_rows]
        draw.line(points, fill=color, width=7, joint="curve")
        for x, y in points:
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color)

    legend_x = width - 420
    for i, (_, color, label) in enumerate(groups):
        x = legend_x + i * 200
        draw.rectangle((x, 78, x + 28, 106), fill=color)
        draw.text((x + 42, 75), label, font=font(28), fill=TEXT)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(FIGURES_DIR / "report_daily_conversion_trend.png", quality=95)


def main() -> None:
    render_bar_chart()
    render_line_chart()


if __name__ == "__main__":
    main()
