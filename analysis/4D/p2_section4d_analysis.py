"""
Section 4D — P2 Regional Alignment: Analysis from Local Annual Scores
=====================================================================
Produces CSV outputs for the 2025 report's Section 4D
("P2 Trends – Regional Alignment").

This implementation uses only the Python standard library so it can run
in the current environment without pandas.

Canonical data source:
  - data/annual_scores (4).csv

Outputs (analysis/4D/):
  01_p2_world_avg_trend.csv
  02_p2_country_shifts_2024_2025.csv
  03_p2_big_movers.csv
  04_p2_regional_summary.csv
  04b_p2_subregional_summary.csv
  05_p2_region_outliers_2025.csv
  06_p2_region_change_contributors.csv
  07_p2_key_country_history.csv
  08_p2_country_profile_2025.csv
  09_p2_distribution_summary_2024_2025.csv
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev


DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUT_DIR = Path(__file__).parent


ISO3_TO_REGION = {
    "DZA": "Northern Africa",
    "EGY": "Northern Africa",
    "LBY": "Northern Africa",
    "MAR": "Northern Africa",
    "SDN": "Northern Africa",
    "TUN": "Northern Africa",
    "BDI": "Eastern Africa",
    "COM": "Eastern Africa",
    "DJI": "Eastern Africa",
    "ERI": "Eastern Africa",
    "ETH": "Eastern Africa",
    "KEN": "Eastern Africa",
    "MDG": "Eastern Africa",
    "MWI": "Eastern Africa",
    "MUS": "Eastern Africa",
    "MOZ": "Eastern Africa",
    "RWA": "Eastern Africa",
    "SYC": "Eastern Africa",
    "SOM": "Eastern Africa",
    "SSD": "Eastern Africa",
    "UGA": "Eastern Africa",
    "TZA": "Eastern Africa",
    "ZMB": "Eastern Africa",
    "ZWE": "Eastern Africa",
    "AGO": "Middle Africa",
    "CMR": "Middle Africa",
    "CAF": "Middle Africa",
    "TCD": "Middle Africa",
    "COG": "Middle Africa",
    "COD": "Middle Africa",
    "GNQ": "Middle Africa",
    "GAB": "Middle Africa",
    "STP": "Middle Africa",
    "BWA": "Southern Africa",
    "SWZ": "Southern Africa",
    "LSO": "Southern Africa",
    "NAM": "Southern Africa",
    "ZAF": "Southern Africa",
    "BEN": "Western Africa",
    "BFA": "Western Africa",
    "CPV": "Western Africa",
    "CIV": "Western Africa",
    "GMB": "Western Africa",
    "GHA": "Western Africa",
    "GIN": "Western Africa",
    "GNB": "Western Africa",
    "LBR": "Western Africa",
    "MLI": "Western Africa",
    "MRT": "Western Africa",
    "NER": "Western Africa",
    "NGA": "Western Africa",
    "SEN": "Western Africa",
    "SLE": "Western Africa",
    "TGO": "Western Africa",
    "ATG": "Caribbean",
    "BHS": "Caribbean",
    "BRB": "Caribbean",
    "CUB": "Caribbean",
    "DMA": "Caribbean",
    "DOM": "Caribbean",
    "GRD": "Caribbean",
    "HTI": "Caribbean",
    "JAM": "Caribbean",
    "KNA": "Caribbean",
    "LCA": "Caribbean",
    "VCT": "Caribbean",
    "TTO": "Caribbean",
    "BLZ": "Central America",
    "CRI": "Central America",
    "SLV": "Central America",
    "GTM": "Central America",
    "HND": "Central America",
    "MEX": "Central America",
    "NIC": "Central America",
    "PAN": "Central America",
    "ARG": "South America",
    "BOL": "South America",
    "BRA": "South America",
    "CHL": "South America",
    "COL": "South America",
    "ECU": "South America",
    "GUY": "South America",
    "PRY": "South America",
    "PER": "South America",
    "SUR": "South America",
    "URY": "South America",
    "VEN": "South America",
    "CAN": "Northern America",
    "USA": "Northern America",
    "KAZ": "Central Asia",
    "KGZ": "Central Asia",
    "TJK": "Central Asia",
    "TKM": "Central Asia",
    "UZB": "Central Asia",
    "CHN": "Eastern Asia",
    "PRK": "Eastern Asia",
    "JPN": "Eastern Asia",
    "MNG": "Eastern Asia",
    "KOR": "Eastern Asia",
    "BRN": "South-eastern Asia",
    "KHM": "South-eastern Asia",
    "IDN": "South-eastern Asia",
    "LAO": "South-eastern Asia",
    "MYS": "South-eastern Asia",
    "MMR": "South-eastern Asia",
    "PHL": "South-eastern Asia",
    "SGP": "South-eastern Asia",
    "THA": "South-eastern Asia",
    "TLS": "South-eastern Asia",
    "VNM": "South-eastern Asia",
    "AFG": "Southern Asia",
    "BGD": "Southern Asia",
    "BTN": "Southern Asia",
    "IND": "Southern Asia",
    "IRN": "Southern Asia",
    "MDV": "Southern Asia",
    "NPL": "Southern Asia",
    "PAK": "Southern Asia",
    "LKA": "Southern Asia",
    "ARM": "Western Asia",
    "AZE": "Western Asia",
    "BHR": "Western Asia",
    "CYP": "Western Asia",
    "GEO": "Western Asia",
    "IRQ": "Western Asia",
    "ISR": "Western Asia",
    "JOR": "Western Asia",
    "KWT": "Western Asia",
    "LBN": "Western Asia",
    "OMN": "Western Asia",
    "QAT": "Western Asia",
    "SAU": "Western Asia",
    "SYR": "Western Asia",
    "TUR": "Western Asia",
    "ARE": "Western Asia",
    "YEM": "Western Asia",
    "BLR": "Eastern Europe",
    "BGR": "Eastern Europe",
    "CZE": "Eastern Europe",
    "HUN": "Eastern Europe",
    "POL": "Eastern Europe",
    "MDA": "Eastern Europe",
    "ROU": "Eastern Europe",
    "RUS": "Eastern Europe",
    "SVK": "Eastern Europe",
    "UKR": "Eastern Europe",
    "DNK": "Northern Europe",
    "EST": "Northern Europe",
    "FIN": "Northern Europe",
    "ISL": "Northern Europe",
    "IRL": "Northern Europe",
    "LVA": "Northern Europe",
    "LTU": "Northern Europe",
    "NOR": "Northern Europe",
    "SWE": "Northern Europe",
    "GBR": "Northern Europe",
    "ALB": "Southern Europe",
    "AND": "Southern Europe",
    "BIH": "Southern Europe",
    "HRV": "Southern Europe",
    "GRC": "Southern Europe",
    "ITA": "Southern Europe",
    "MLT": "Southern Europe",
    "MNE": "Southern Europe",
    "MKD": "Southern Europe",
    "PRT": "Southern Europe",
    "SMR": "Southern Europe",
    "SRB": "Southern Europe",
    "SVN": "Southern Europe",
    "ESP": "Southern Europe",
    "AUT": "Western Europe",
    "BEL": "Western Europe",
    "FRA": "Western Europe",
    "DEU": "Western Europe",
    "LIE": "Western Europe",
    "LUX": "Western Europe",
    "MCO": "Western Europe",
    "NLD": "Western Europe",
    "CHE": "Western Europe",
    "AUS": "Australia and New Zealand",
    "NZL": "Australia and New Zealand",
    "FJI": "Melanesia",
    "PNG": "Melanesia",
    "SLB": "Melanesia",
    "VUT": "Melanesia",
    "KIR": "Micronesia",
    "MHL": "Micronesia",
    "FSM": "Micronesia",
    "NRU": "Micronesia",
    "PLW": "Micronesia",
    "WSM": "Polynesia",
    "TON": "Polynesia",
    "TUV": "Polynesia",
}

SUBREGION_TO_BROAD = {
    "Northern Africa": "Africa",
    "Eastern Africa": "Sub-Saharan Africa",
    "Middle Africa": "Sub-Saharan Africa",
    "Southern Africa": "Sub-Saharan Africa",
    "Western Africa": "Sub-Saharan Africa",
    "Caribbean": "Latin America & Caribbean",
    "Central America": "Latin America & Caribbean",
    "South America": "Latin America & Caribbean",
    "Northern America": "Northern America",
    "Central Asia": "Central Asia",
    "Eastern Asia": "Eastern Asia",
    "South-eastern Asia": "South-eastern Asia",
    "Southern Asia": "Southern Asia",
    "Western Asia": "Western Asia",
    "Eastern Europe": "Eastern Europe",
    "Northern Europe": "Northern Europe",
    "Southern Europe": "Southern Europe",
    "Western Europe": "Western Europe",
    "Australia and New Zealand": "Oceania",
    "Melanesia": "Oceania",
    "Micronesia": "Oceania",
    "Polynesia": "Oceania",
}


def round_or_blank(value: float | None, digits: int = 2):
    if value is None:
        return ""
    return round(value, digits)


def percentile(sorted_vals, p):
    if not sorted_vals:
        return None
    idx = (len(sorted_vals) - 1) * p
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def rolling_centered(values_by_year):
    years = sorted(values_by_year)
    result = {}
    for i, year in enumerate(years):
        if i == 0 or i == len(years) - 1:
            result[year] = None
            continue
        vals = [
            values_by_year[years[i - 1]],
            values_by_year[year],
            values_by_year[years[i + 1]],
        ]
        result[year] = mean(vals)
    return result


def linear_trend(years, values):
    x_bar = mean(years)
    y_bar = mean(values)
    num = sum((x - x_bar) * (y - y_bar) for x, y in zip(years, values))
    den = sum((x - x_bar) ** 2 for x in years)
    slope = num / den if den else 0.0
    intercept = y_bar - slope * x_bar
    return {year: (slope * year) + intercept for year in years}


def load_annual_scores():
    rows = []
    with open(DATA_DIR / "annual_scores (4).csv", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            iso3 = row["Country name"]
            year = int(row["Year"])
            region = ISO3_TO_REGION.get(iso3, "")
            rows.append(
                {
                    "iso3": iso3,
                    "year": year,
                    "p1": float(row["Pillar 1 Score"]) if row["Pillar 1 Score"] else None,
                    "p2": float(row["Pillar 2 Score"]) if row["Pillar 2 Score"] else None,
                    "p3": float(row["Pillar 3 Score"]) if row["Pillar 3 Score"] else None,
                    "total_index": float(row["Total Index Average"])
                    if row["Total Index Average"]
                    else None,
                    "overall_rank": int(float(row["Overall Rank"])) if row["Overall Rank"] else None,
                    "yes": int(float(row["Yes Votes"])) if row["Yes Votes"] else 0,
                    "no": int(float(row["No Votes"])) if row["No Votes"] else 0,
                    "abstain": int(float(row["Abstain Votes"])) if row["Abstain Votes"] else 0,
                    "total": int(float(row["Total Votes in Year"])) if row["Total Votes in Year"] else 0,
                    "region": region,
                    "broad_region": SUBREGION_TO_BROAD.get(region, ""),
                }
            )
    return rows


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def output_01_world_avg_trend(rows):
    yearly = defaultdict(list)
    totals = defaultdict(list)
    for row in rows:
        if row["year"] <= 2025 and row["p2"] is not None:
            yearly[row["year"]].append(row["p2"])
            totals[row["year"]].append(row["total"])

    years = sorted(yearly)
    avg_by_year = {year: mean(yearly[year]) for year in years}
    rolling = rolling_centered(avg_by_year)
    trendline = linear_trend(years, [avg_by_year[year] for year in years])

    out_rows = []
    previous = None
    for year in years:
        vals = yearly[year]
        current = avg_by_year[year]
        yoy = None if previous is None else current - previous
        out_rows.append(
            {
                "Year": year,
                "world_avg_p2": round_or_blank(current),
                "median_p2": round_or_blank(median(vals)),
                "std_p2": round_or_blank(pstdev(vals)),
                "num_countries": len(vals),
                "avg_total_votes": round_or_blank(mean(totals[year]), 1),
                "yoy_change": round_or_blank(yoy),
                "rolling_3y": round_or_blank(rolling[year]),
                "trendline_linear": round_or_blank(trendline[year]),
            }
        )
        previous = current

    write_csv(
        OUT_DIR / "01_p2_world_avg_trend.csv",
        [
            "Year",
            "world_avg_p2",
            "median_p2",
            "std_p2",
            "num_countries",
            "avg_total_votes",
            "yoy_change",
            "rolling_3y",
            "trendline_linear",
        ],
        out_rows,
    )
    return out_rows


def output_02_country_shifts(rows):
    d24 = {row["iso3"]: row for row in rows if row["year"] == 2024}
    d25 = {row["iso3"]: row for row in rows if row["year"] == 2025}
    merged = []
    all_isos = sorted(set(d24) | set(d25))
    for iso3 in all_isos:
        r24 = d24.get(iso3)
        r25 = d25.get(iso3)
        p2_24 = r24["p2"] if r24 else None
        p2_25 = r25["p2"] if r25 else None
        change = None
        if p2_24 is not None and p2_25 is not None:
            change = p2_25 - p2_24
        row = {
            "iso3": iso3,
            "p2_2024": round_or_blank(p2_24),
            "yes_2024": r24["yes"] if r24 else "",
            "no_2024": r24["no"] if r24 else "",
            "abstain_2024": r24["abstain"] if r24 else "",
            "total_2024": r24["total"] if r24 else "",
            "p2_2025": round_or_blank(p2_25),
            "yes_2025": r25["yes"] if r25 else "",
            "no_2025": r25["no"] if r25 else "",
            "abstain_2025": r25["abstain"] if r25 else "",
            "total_2025": r25["total"] if r25 else "",
            "p2_change": round_or_blank(change),
            "total_change": (r25["total"] - r24["total"]) if r24 and r25 else "",
            "yes_pct_2024": round_or_blank((r24["yes"] / r24["total"]) * 100 if r24 and r24["total"] else None, 1),
            "yes_pct_2025": round_or_blank((r25["yes"] / r25["total"]) * 100 if r25 and r25["total"] else None, 1),
            "yes_pct_change": round_or_blank(
                (((r25["yes"] / r25["total"]) * 100) - ((r24["yes"] / r24["total"]) * 100))
                if r24
                and r25
                and r24["total"]
                and r25["total"]
                else None,
                1,
            ),
            "region": (r25 or r24)["region"] if (r25 or r24) else "",
            "broad_region": (r25 or r24)["broad_region"] if (r25 or r24) else "",
        }
        merged.append(row)

    merged.sort(key=lambda r: (float("inf") if r["p2_change"] == "" else float(r["p2_change"])))
    write_csv(
        OUT_DIR / "02_p2_country_shifts_2024_2025.csv",
        list(merged[0].keys()),
        merged,
    )
    return merged


def output_03_big_movers(shifts):
    rows = []
    for row in shifts:
        if row["p2_change"] == "":
            continue
        change = float(row["p2_change"])
        if abs(change) > 10:
            out = dict(row)
            out["direction"] = "GAINER" if change > 0 else "DECLINER"
            rows.append(out)
    rows.sort(key=lambda r: float(r["p2_change"]))
    write_csv(OUT_DIR / "03_p2_big_movers.csv", list(rows[0].keys()) if rows else [], rows)
    return rows


def summarize_region(rows, region_key):
    d24 = defaultdict(list)
    d25 = defaultdict(list)
    for row in rows:
        if row["year"] == 2024 and row["p2"] is not None:
            d24[row[region_key]].append(row["p2"])
        elif row["year"] == 2025 and row["p2"] is not None:
            d25[row[region_key]].append(row["p2"])

    out = []
    for key in sorted(set(d24) | set(d25)):
        if not key:
            continue
        vals24 = d24.get(key, [])
        vals25 = d25.get(key, [])
        avg24 = mean(vals24) if vals24 else None
        avg25 = mean(vals25) if vals25 else None
        med24 = median(vals24) if vals24 else None
        med25 = median(vals25) if vals25 else None
        out.append(
            {
                region_key: key,
                "avg_p2_2024": round_or_blank(avg24),
                "median_p2_2024": round_or_blank(med24),
                "n_countries_2024": len(vals24),
                "avg_p2_2025": round_or_blank(avg25),
                "median_p2_2025": round_or_blank(med25),
                "n_countries_2025": len(vals25),
                "avg_p2_change": round_or_blank(avg25 - avg24 if avg24 is not None and avg25 is not None else None),
                "median_p2_change": round_or_blank(med25 - med24 if med24 is not None and med25 is not None else None),
            }
        )
    out.sort(key=lambda r: float(r["avg_p2_change"]))
    return out


def output_04_region_summaries(rows):
    broad = summarize_region(rows, "broad_region")
    sub = summarize_region(rows, "region")
    write_csv(OUT_DIR / "04_p2_regional_summary.csv", list(broad[0].keys()), broad)
    write_csv(OUT_DIR / "04b_p2_subregional_summary.csv", list(sub[0].keys()), sub)
    return broad, sub


def output_05_region_outliers_2025(rows):
    broad_avg = {}
    sub_avg = {}
    for broad in {row["broad_region"] for row in rows if row["year"] == 2025 and row["broad_region"]}:
        vals = [row["p2"] for row in rows if row["year"] == 2025 and row["broad_region"] == broad and row["p2"] is not None]
        broad_avg[broad] = mean(vals)
    for sub in {row["region"] for row in rows if row["year"] == 2025 and row["region"]}:
        vals = [row["p2"] for row in rows if row["year"] == 2025 and row["region"] == sub and row["p2"] is not None]
        sub_avg[sub] = mean(vals)

    out = []
    for row in rows:
        if row["year"] != 2025 or row["p2"] is None:
            continue
        out.append(
            {
                "iso3": row["iso3"],
                "p2_2025": round_or_blank(row["p2"]),
                "region": row["region"],
                "broad_region": row["broad_region"],
                "broad_region_avg_2025": round_or_blank(broad_avg[row["broad_region"]]),
                "diff_from_broad_avg": round_or_blank(row["p2"] - broad_avg[row["broad_region"]]),
                "subregion_avg_2025": round_or_blank(sub_avg[row["region"]]),
                "diff_from_subregion_avg": round_or_blank(row["p2"] - sub_avg[row["region"]]),
                "total_2025": row["total"],
            }
        )
    out.sort(key=lambda r: float(r["diff_from_broad_avg"]))
    write_csv(OUT_DIR / "05_p2_region_outliers_2025.csv", list(out[0].keys()), out)
    return out


def output_06_region_change_contributors(rows):
    d24 = {row["iso3"]: row for row in rows if row["year"] == 2024}
    d25 = {row["iso3"]: row for row in rows if row["year"] == 2025}

    region_members = defaultdict(list)
    for iso3, row in d25.items():
        if row["broad_region"]:
            region_members[row["broad_region"]].append(iso3)

    out = []
    for broad_region, members in region_members.items():
        n = len(members)
        vals24 = [d24[iso]["p2"] for iso in members if iso in d24 and d24[iso]["p2"] is not None]
        vals25 = [d25[iso]["p2"] for iso in members if iso in d25 and d25[iso]["p2"] is not None]
        avg_change = mean(vals25) - mean(vals24) if vals24 and vals25 else None
        for iso in members:
            if iso not in d24 or iso not in d25:
                continue
            p2_change = d25[iso]["p2"] - d24[iso]["p2"]
            out.append(
                {
                    "broad_region": broad_region,
                    "iso3": iso,
                    "region": d25[iso]["region"],
                    "p2_2024": round_or_blank(d24[iso]["p2"]),
                    "p2_2025": round_or_blank(d25[iso]["p2"]),
                    "p2_change": round_or_blank(p2_change),
                    "region_avg_change": round_or_blank(avg_change),
                    "contribution_to_region_avg_change": round_or_blank(p2_change / n),
                    "total_2024": d24[iso]["total"],
                    "total_2025": d25[iso]["total"],
                }
            )
    out.sort(key=lambda r: (r["broad_region"], -abs(float(r["contribution_to_region_avg_change"])), r["iso3"]))
    write_csv(OUT_DIR / "06_p2_region_change_contributors.csv", list(out[0].keys()), out)
    return out


def output_07_key_country_history(rows):
    key = [
        "USA",
        "CAN",
        "ARG",
        "BRA",
        "PRY",
        "GEO",
        "RUS",
        "BLR",
        "KOR",
        "CHN",
        "JPN",
        "AUS",
        "NZL",
        "FSM",
        "TUR",
        "SYR",
        "ISR",
    ]
    out = []
    for row in rows:
        if row["iso3"] in key and 2015 <= row["year"] <= 2025:
            out.append(
                {
                    "iso3": row["iso3"],
                    "year": row["year"],
                    "p2_score": round_or_blank(row["p2"]),
                    "yes": row["yes"],
                    "no": row["no"],
                    "abstain": row["abstain"],
                    "total": row["total"],
                }
            )
    out.sort(key=lambda r: (r["iso3"], r["year"]))
    write_csv(OUT_DIR / "07_p2_key_country_history.csv", list(out[0].keys()), out)
    return out


def output_08_country_profile_2025(rows):
    out = []
    for row in rows:
        if row["year"] != 2025:
            continue
        out.append(
            {
                "iso3": row["iso3"],
                "p2_2025": round_or_blank(row["p2"]),
                "p2_rank_2025": "",
                "p1_2025": round_or_blank(row["p1"]),
                "p3_2025": round_or_blank(row["p3"]),
                "yes_2025": row["yes"],
                "no_2025": row["no"],
                "abstain_2025": row["abstain"],
                "total_2025": row["total"],
                "yes_pct_2025": round_or_blank((row["yes"] / row["total"]) * 100 if row["total"] else None, 1),
                "region": row["region"],
                "broad_region": row["broad_region"],
            }
        )
    out.sort(key=lambda r: (-float(r["p2_2025"]), r["iso3"]))
    for idx, row in enumerate(out, start=1):
        row["p2_rank_2025"] = idx
    write_csv(OUT_DIR / "08_p2_country_profile_2025.csv", list(out[0].keys()), out)
    return out


def output_09_distribution_summary(rows):
    out = []
    for year in (2024, 2025):
        vals = sorted(row["p2"] for row in rows if row["year"] == year and row["p2"] is not None)
        out.append(
            {
                "year": year,
                "mean_p2": round_or_blank(mean(vals)),
                "median_p2": round_or_blank(median(vals)),
                "std_p2": round_or_blank(pstdev(vals)),
                "min_p2": round_or_blank(vals[0] if vals else None),
                "p10": round_or_blank(percentile(vals, 0.10)),
                "p25": round_or_blank(percentile(vals, 0.25)),
                "p75": round_or_blank(percentile(vals, 0.75)),
                "p90": round_or_blank(percentile(vals, 0.90)),
                "max_p2": round_or_blank(vals[-1] if vals else None),
                "countries_ge_95": sum(1 for value in vals if value >= 95),
                "countries_lt_80": sum(1 for value in vals if value < 80),
                "num_countries": len(vals),
            }
        )
    write_csv(OUT_DIR / "09_p2_distribution_summary_2024_2025.csv", list(out[0].keys()), out)
    return out


def main():
    rows = load_annual_scores()
    output_01_world_avg_trend(rows)
    shifts = output_02_country_shifts(rows)
    output_03_big_movers(shifts)
    output_04_region_summaries(rows)
    output_05_region_outliers_2025(rows)
    output_06_region_change_contributors(rows)
    output_07_key_country_history(rows)
    output_08_country_profile_2025(rows)
    output_09_distribution_summary(rows)
    print(f"Wrote 9 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
