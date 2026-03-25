#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_2024 = BASE_DIR / "ga_2024_geo_l3_summary.csv"
DEFAULT_2025 = BASE_DIR / "ga_2025_geo_l3_summary.csv"
DEFAULT_OUTPUT_HTML = BASE_DIR / "ga_2025_vs_2024_geo_l3_change.html"
DEFAULT_OUTPUT_SVG = BASE_DIR / "ga_2025_vs_2024_geo_l3_change.svg"


def load_summary(path: Path, tag_column: str) -> dict[str, dict[str, float | int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        pct_column = next(name for name in reader.fieldnames or [] if name.startswith("pct_of_"))
        data: dict[str, dict[str, float | int]] = {}
        for row in reader:
            data[row[tag_column]] = {
                "count": int(row["resolution_count"]),
                "pct": float(row[pct_column]),
            }
    return data


def wrap_label(text: str, max_chars: int = 28) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines or [text]


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_delta(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} pp"


def build_svg(
    summary_2024: dict[str, dict[str, float | int]],
    summary_2025: dict[str, dict[str, float | int]],
    top_n: int,
) -> str:
    tags = sorted(
        set(summary_2024) | set(summary_2025),
        key=lambda tag: (
            -float(summary_2025.get(tag, {"pct": 0.0})["pct"]),
            -int(summary_2025.get(tag, {"count": 0})["count"]),
            tag,
        ),
    )[:top_n]

    rows = []
    for tag in tags:
        current = summary_2025.get(tag, {"count": 0, "pct": 0.0})
        previous = summary_2024.get(tag, {"count": 0, "pct": 0.0})
        rows.append(
            {
                "tag": tag,
                "count_2025": int(current["count"]),
                "pct_2025": float(current["pct"]),
                "count_2024": int(previous["count"]),
                "pct_2024": float(previous["pct"]),
                "delta": float(current["pct"]) - float(previous["pct"]),
            }
        )

    width = 1460
    header_h = 150
    row_h = 52
    footer_h = 90
    height = header_h + footer_h + (row_h * len(rows))

    bg = "#f5efe4"
    ink = "#102a43"
    muted = "#52667a"
    grid = "#d9cfbe"
    line_neutral = "#c9bea9"
    year_2024 = "#5c7c99"
    year_2025 = "#d95d39"
    up = "#1f8f73"
    down = "#c44536"
    card = "#fffaf1"

    label_x = 54
    plot_x0 = 410
    plot_x1 = 1040
    plot_w = plot_x1 - plot_x0
    right_x = 1095

    max_pct = max(
        [row["pct_2024"] for row in rows] + [row["pct_2025"] for row in rows] + [12.0]
    )
    axis_max = max(6.0, math.ceil((max_pct * 1.12) / 1.0) * 1.0)
    ticks = 6

    def pct_to_x(value: float) -> float:
        return plot_x0 + (value / axis_max) * plot_w

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Top geographic L3 tags in 2025 and change since 2024</title>',
        f'<desc id="desc">Ranked dumbbell chart comparing 2024 and 2025 percentages of all GA resolutions for the top geographic L3 tags by 2025 share.</desc>',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<circle cx="{width - 90}" cy="72" r="180" fill="#e8dcc7" opacity="0.45"/>',
        f'<circle cx="{width - 30}" cy="10" r="90" fill="#efe5d6" opacity="0.8"/>',
        f'<rect x="28" y="24" width="{width - 56}" height="{height - 48}" rx="26" fill="{card}" stroke="#eadfce"/>',
        f'<text x="54" y="70" fill="{ink}" font-size="33" font-family="Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif" font-weight="700">Top Geographic L3 Tags, 2025</text>',
        f'<text x="54" y="102" fill="{muted}" font-size="16" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">Ranked by 2025 share of all General Assembly resolutions. Hollow blue marks 2024, filled orange marks 2025, and the connector shows the direction of change.</text>',
        f'<text x="54" y="126" fill="{muted}" font-size="14" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">Percentages are normalized to each year’s full GA denominator, so the 2024 vs 2025 comparison is comparable despite different resolution counts.</text>',
        f'<rect x="{right_x}" y="52" width="132" height="34" rx="17" fill="#eef3f8"/>',
        f'<circle cx="{right_x + 18}" cy="69" r="5" fill="none" stroke="{year_2024}" stroke-width="2.5"/>',
        f'<text x="{right_x + 32}" y="74" fill="{ink}" font-size="13" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">2024</text>',
        f'<rect x="{right_x + 142}" y="52" width="132" height="34" rx="17" fill="#fff0ea"/>',
        f'<circle cx="{right_x + 160}" cy="69" r="5" fill="{year_2025}"/>',
        f'<text x="{right_x + 174}" y="74" fill="{ink}" font-size="13" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">2025</text>',
    ]

    axis_y = header_h - 6
    for idx in range(ticks + 1):
        pct = axis_max * idx / ticks
        x = pct_to_x(pct)
        svg.append(
            f'<line x1="{x:.1f}" y1="{header_h}" x2="{x:.1f}" y2="{height - footer_h}" stroke="{grid}" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{x:.1f}" y="{axis_y}" text-anchor="middle" fill="{muted}" font-size="12" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">{pct:.0f}%</text>'
        )

    for idx, row in enumerate(rows):
        y = header_h + idx * row_h + 32
        y_line = y - 6
        x_2024 = pct_to_x(row["pct_2024"])
        x_2025 = pct_to_x(row["pct_2025"])
        delta_color = up if row["delta"] >= 0 else down
        label_lines = wrap_label(row["tag"])
        text_y = y - ((len(label_lines) - 1) * 8)

        svg.append(
            f'<line x1="{plot_x0}" y1="{y_line}" x2="{plot_x1}" y2="{y_line}" stroke="{line_neutral}" stroke-width="1" opacity="0.35"/>'
        )
        svg.append(
            f'<line x1="{x_2024:.1f}" y1="{y_line}" x2="{x_2025:.1f}" y2="{y_line}" stroke="{delta_color}" stroke-width="3" stroke-linecap="round" opacity="0.95"/>'
        )
        svg.append(
            f'<circle cx="{x_2024:.1f}" cy="{y_line}" r="6.5" fill="{card}" stroke="{year_2024}" stroke-width="3"/>'
        )
        svg.append(
            f'<circle cx="{x_2025:.1f}" cy="{y_line}" r="7.5" fill="{year_2025}"/>'
        )

        svg.append(
            f'<text x="{label_x}" y="{text_y}" fill="{ink}" font-size="15" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif" font-weight="600">'
        )
        for line_index, line in enumerate(label_lines):
            dy = 0 if line_index == 0 else 16
            svg.append(f'<tspan x="{label_x}" dy="{dy}">{xml_escape(line)}</tspan>')
        svg.append("</text>")

        svg.append(
            f'<text x="{right_x}" y="{y_line + 5}" fill="{ink}" font-size="14" font-family="Menlo, Consolas, Monaco, monospace">{row["count_2025"]:>2} res  ·  {row["pct_2025"]:.2f}%</text>'
        )

        badge_w = 78
        badge_x = width - 54 - badge_w
        badge_fill = "#e8f4ef" if row["delta"] >= 0 else "#fdeceb"
        svg.append(
            f'<rect x="{badge_x}" y="{y_line - 13}" width="{badge_w}" height="26" rx="13" fill="{badge_fill}"/>'
        )
        svg.append(
            f'<text x="{badge_x + badge_w / 2}" y="{y_line + 5}" text-anchor="middle" fill="{delta_color}" font-size="13" font-family="Menlo, Consolas, Monaco, monospace" font-weight="700">{fmt_delta(row["delta"])}</text>'
        )

    footer_y = height - 42
    svg.append(
        f'<text x="54" y="{footer_y}" fill="{muted}" font-size="13" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">Top {len(rows)} tags shown. Source: current manual geographic mapping in ga_2024_geographic_mapping.csv and ga_2025_geographic_mapping.csv.</text>'
    )
    svg.append(
        f'<text x="{width - 54}" y="{footer_y}" text-anchor="end" fill="{muted}" font-size="13" font-family="Avenir Next, Trebuchet MS, Helvetica Neue, sans-serif">2024 denominator: 95 resolutions  |  2025 denominator: 192 resolutions</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


def build_html(svg_markup: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GA Geographic L3 Change</title>
  <style>
    :root {{
      --bg: #efe5d6;
      --ink: #102a43;
      --muted: #52667a;
      --card: #fffaf1;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top right, #e5d4bb 0, transparent 28%),
        linear-gradient(180deg, #efe5d6 0%, #f6efe4 100%);
      color: var(--ink);
      font-family: "Avenir Next", "Trebuchet MS", "Helvetica Neue", sans-serif;
      display: grid;
      place-items: center;
      padding: 24px;
    }}
    .frame {{
      width: min(100%, 1480px);
      background: rgba(255, 250, 241, 0.72);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(221, 207, 189, 0.95);
      border-radius: 28px;
      padding: 14px;
      box-shadow: 0 24px 80px rgba(16, 42, 67, 0.08);
    }}
    svg {{
      display: block;
      width: 100%;
      height: auto;
      border-radius: 22px;
    }}
  </style>
</head>
<body>
  <div class="frame">
    {svg_markup}
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a sleek 2025 vs 2024 geographic L3 change visualization.",
    )
    parser.add_argument("--summary-2024", type=Path, default=DEFAULT_2024)
    parser.add_argument("--summary-2025", type=Path, default=DEFAULT_2025)
    parser.add_argument("--top-n", type=int, default=15)
    parser.add_argument("--output-html", type=Path, default=DEFAULT_OUTPUT_HTML)
    parser.add_argument("--output-svg", type=Path, default=DEFAULT_OUTPUT_SVG)
    args = parser.parse_args()

    summary_2024 = load_summary(args.summary_2024, "geo_l3")
    summary_2025 = load_summary(args.summary_2025, "geo_l3")
    svg_markup = build_svg(summary_2024, summary_2025, args.top_n)
    html_markup = build_html(svg_markup)

    args.output_svg.write_text(svg_markup, encoding="utf-8")
    args.output_html.write_text(html_markup, encoding="utf-8")

    print(f"Wrote {args.output_svg}")
    print(f"Wrote {args.output_html}")


if __name__ == "__main__":
    main()
