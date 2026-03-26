"""
Section 4E - P3 Global Alignment: Analysis from Local CSVs
==========================================================
Produces CSV outputs for the 2025 report's Section 4E
("P3 Trends - Global Alignment").

Canonical score source:
  - data/annual_scores (4).csv

Descriptive proxy sources used for explanatory diagnostics:
  - data/topic_votes_yearly (4).csv
  - data/un_votes_with_sc (1).csv

Outputs (analysis/4E/):
  01_p3_world_avg_trend.csv
  02_p3_country_shifts_2024_2025.csv
  03_p3_big_movers.csv
  04_p3_regional_summary.csv
  04b_p3_subregional_summary.csv
  05_p3_majority_alignment_proxy.csv
  06_p3_topic_vote_shifts_2024_2025.csv
  07_p3_resolution_majority_summary_2025.csv
  08_p3_key_country_topic_gap_changes.csv
  09_p3_country_profile_2025.csv
  10_p3_distribution_summary_2024_2025.csv
  11_p3_key_country_history.csv
  12_p3_global_outliers_2025.csv
  13_p3_region_change_contributors.csv

Important caveat:
  P3 levels come from the published annual pillar scores in annual_scores.
  The majority-alignment and topic-level outputs below are descriptive
  diagnostics to help explain movement; they do not attempt to recompute
  the canonical Pillar 3 score.
"""

from __future__ import annotations

import csv
import json
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
        result[year] = mean(
            [
                values_by_year[years[i - 1]],
                values_by_year[year],
                values_by_year[years[i + 1]],
            ]
        )
    return result


def linear_trend(years, values):
    x_bar = mean(years)
    y_bar = mean(values)
    num = sum((x - x_bar) * (y - y_bar) for x, y in zip(years, values))
    den = sum((x - x_bar) ** 2 for x in years)
    slope = num / den if den else 0.0
    intercept = y_bar - slope * x_bar
    return {year: (slope * year) + intercept for year in years}


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


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
                    "p3_rank": int(float(row["Pillar 3 Rank"])) if row["Pillar 3 Rank"] else None,
                    "total_index": float(row["Total Index Average"])
                    if row["Total Index Average"]
                    else None,
                    "overall_rank": int(float(row["Overall Rank"])) if row["Overall Rank"] else None,
                    "yes": int(float(row["Yes Votes"])) if row["Yes Votes"] else 0,
                    "no": int(float(row["No Votes"])) if row["No Votes"] else 0,
                    "abstain": int(float(row["Abstain Votes"])) if row["Abstain Votes"] else 0,
                    "total": int(float(row["Total Votes in Year"]))
                    if row["Total Votes in Year"]
                    else 0,
                    "region": region,
                    "broad_region": SUBREGION_TO_BROAD.get(region, ""),
                }
            )
    return rows


def load_topic_votes():
    rows = []
    with open(DATA_DIR / "topic_votes_yearly (4).csv", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "year": int(row["Year"]),
                    "country": row["Country"],
                    "topic": row["TopicTag"],
                    "yes": int(row["YesVotes_Topic"]) if row["YesVotes_Topic"] else 0,
                    "no": int(row["NoVotes_Topic"]) if row["NoVotes_Topic"] else 0,
                    "abstain": int(row["AbstainVotes_Topic"])
                    if row["AbstainVotes_Topic"]
                    else 0,
                    "total": int(row["TotalVotes_Topic"]) if row["TotalVotes_Topic"] else 0,
                }
            )
    return rows


def load_raw_resolutions():
    rows = []
    with open(DATA_DIR / "un_votes_with_sc (1).csv", newline="") as handle:
        reader = csv.DictReader(handle)
        seen = set()
        for row in reader:
            date = (row.get("Date") or "").strip()
            if len(date) < 4 or not date[:4].isdigit():
                continue
            year = int(date[:4])
            if year not in (2024, 2025):
                continue

            resolution = row.get("Resolution") or ""
            if row.get("sc_flag") != "0" and "ES-" not in resolution:
                continue

            key = (row.get("id"), resolution)
            if key in seen:
                continue
            seen.add(key)

            try:
                votes = json.loads(row.get("vote_data") or "{}")
            except json.JSONDecodeError:
                continue

            yes = sum(1 for vote in votes.values() if vote == "YES")
            no = sum(1 for vote in votes.values() if vote == "NO")
            abstain = sum(1 for vote in votes.values() if vote == "ABSTAIN")
            total = yes + no + abstain
            if total == 0:
                continue

            counts = {"YES": yes, "NO": no, "ABSTAIN": abstain}
            top = max(counts.values())
            winners = [label for label, count in counts.items() if count == top]
            second = sorted(counts.values(), reverse=True)[1]
            rows.append(
                {
                    "year": year,
                    "date": date[:10],
                    "resolution": resolution,
                    "title": row.get("Title") or "",
                    "tags": row.get("tags") or "",
                    "votes": votes,
                    "yes": yes,
                    "no": no,
                    "abstain": abstain,
                    "total": total,
                    "majority_vote": winners[0] if len(winners) == 1 else None,
                    "majority_share": (top / total) * 100,
                    "majority_margin": ((top - second) / total) * 100,
                    "non_yes_pct": ((no + abstain) / total) * 100,
                }
            )
    return rows


def output_01_world_avg_trend(rows):
    yearly = defaultdict(list)
    totals = defaultdict(list)
    for row in rows:
        if row["year"] <= 2025 and row["p3"] is not None:
            yearly[row["year"]].append(row["p3"])
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
                "world_avg_p3": round_or_blank(current),
                "median_p3": round_or_blank(median(vals)),
                "std_p3": round_or_blank(pstdev(vals)),
                "num_countries": len(vals),
                "avg_total_votes": round_or_blank(mean(totals[year]), 1),
                "yoy_change": round_or_blank(yoy),
                "rolling_3y": round_or_blank(rolling[year]),
                "trendline_linear": round_or_blank(trendline[year]),
            }
        )
        previous = current

    write_csv(
        OUT_DIR / "01_p3_world_avg_trend.csv",
        [
            "Year",
            "world_avg_p3",
            "median_p3",
            "std_p3",
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
        p3_24 = r24["p3"] if r24 else None
        p3_25 = r25["p3"] if r25 else None
        change = None
        if p3_24 is not None and p3_25 is not None:
            change = p3_25 - p3_24

        merged.append(
            {
                "iso3": iso3,
                "p3_2024": round_or_blank(p3_24),
                "p3_rank_2024": r24["p3_rank"] if r24 and r24["p3_rank"] is not None else "",
                "yes_2024": r24["yes"] if r24 else "",
                "no_2024": r24["no"] if r24 else "",
                "abstain_2024": r24["abstain"] if r24 else "",
                "total_2024": r24["total"] if r24 else "",
                "p3_2025": round_or_blank(p3_25),
                "p3_rank_2025": r25["p3_rank"] if r25 and r25["p3_rank"] is not None else "",
                "yes_2025": r25["yes"] if r25 else "",
                "no_2025": r25["no"] if r25 else "",
                "abstain_2025": r25["abstain"] if r25 else "",
                "total_2025": r25["total"] if r25 else "",
                "p3_change": round_or_blank(change),
                "total_change": (r25["total"] - r24["total"]) if r24 and r25 else "",
                "yes_pct_2024": round_or_blank(
                    (r24["yes"] / r24["total"]) * 100 if r24 and r24["total"] else None,
                    1,
                ),
                "yes_pct_2025": round_or_blank(
                    (r25["yes"] / r25["total"]) * 100 if r25 and r25["total"] else None,
                    1,
                ),
                "no_pct_2024": round_or_blank(
                    (r24["no"] / r24["total"]) * 100 if r24 and r24["total"] else None,
                    1,
                ),
                "no_pct_2025": round_or_blank(
                    (r25["no"] / r25["total"]) * 100 if r25 and r25["total"] else None,
                    1,
                ),
                "abstain_pct_2024": round_or_blank(
                    (r24["abstain"] / r24["total"]) * 100
                    if r24 and r24["total"]
                    else None,
                    1,
                ),
                "abstain_pct_2025": round_or_blank(
                    (r25["abstain"] / r25["total"]) * 100
                    if r25 and r25["total"]
                    else None,
                    1,
                ),
                "region": (r25 or r24)["region"] if (r25 or r24) else "",
                "broad_region": (r25 or r24)["broad_region"] if (r25 or r24) else "",
            }
        )

    merged.sort(key=lambda row: float("inf") if row["p3_change"] == "" else float(row["p3_change"]))
    write_csv(OUT_DIR / "02_p3_country_shifts_2024_2025.csv", list(merged[0].keys()), merged)
    return merged


def output_03_big_movers(shifts):
    rows = []
    for row in shifts:
        if row["p3_change"] == "":
            continue
        change = float(row["p3_change"])
        if abs(change) > 10:
            out = dict(row)
            out["direction"] = "GAINER" if change > 0 else "DECLINER"
            rows.append(out)

    rows.sort(key=lambda row: float(row["p3_change"]))
    write_csv(
        OUT_DIR / "03_p3_big_movers.csv",
        list(rows[0].keys()) if rows else list(shifts[0].keys()) + ["direction"],
        rows,
    )
    return rows


def summarize_region(rows, region_key):
    d24 = defaultdict(list)
    d25 = defaultdict(list)
    for row in rows:
        if row["year"] == 2024 and row["p3"] is not None and row[region_key]:
            d24[row[region_key]].append(row["p3"])
        elif row["year"] == 2025 and row["p3"] is not None and row[region_key]:
            d25[row[region_key]].append(row["p3"])

    out = []
    for key in sorted(set(d24) | set(d25)):
        vals24 = d24.get(key, [])
        vals25 = d25.get(key, [])
        avg24 = mean(vals24) if vals24 else None
        avg25 = mean(vals25) if vals25 else None
        med24 = median(vals24) if vals24 else None
        med25 = median(vals25) if vals25 else None
        out.append(
            {
                region_key: key,
                "avg_p3_2024": round_or_blank(avg24),
                "median_p3_2024": round_or_blank(med24),
                "n_countries_2024": len(vals24),
                "avg_p3_2025": round_or_blank(avg25),
                "median_p3_2025": round_or_blank(med25),
                "n_countries_2025": len(vals25),
                "avg_p3_change": round_or_blank(
                    avg25 - avg24 if avg24 is not None and avg25 is not None else None
                ),
                "median_p3_change": round_or_blank(
                    med25 - med24 if med24 is not None and med25 is not None else None
                ),
            }
        )

    out.sort(key=lambda row: float(row["avg_p3_change"]))
    return out


def output_04_region_summaries(rows):
    broad = summarize_region(rows, "broad_region")
    sub = summarize_region(rows, "region")
    write_csv(OUT_DIR / "04_p3_regional_summary.csv", list(broad[0].keys()), broad)
    write_csv(OUT_DIR / "04b_p3_subregional_summary.csv", list(sub[0].keys()), sub)
    return broad, sub


def output_05_majority_alignment_proxy(raw_resolutions, annual_rows):
    country_year = defaultdict(
        lambda: {"participated": 0, "with_majority": 0, "yes": 0, "no": 0, "abstain": 0}
    )
    world_mix = defaultdict(lambda: {"yes": 0, "no": 0, "abstain": 0, "total": 0})

    for row in raw_resolutions:
        year = row["year"]
        world_mix[year]["yes"] += row["yes"]
        world_mix[year]["no"] += row["no"]
        world_mix[year]["abstain"] += row["abstain"]
        world_mix[year]["total"] += row["total"]

        for iso3, vote in row["votes"].items():
            if vote not in ("YES", "NO", "ABSTAIN"):
                continue
            item = country_year[(iso3, year)]
            item["participated"] += 1
            if vote == "YES":
                item["yes"] += 1
            elif vote == "NO":
                item["no"] += 1
            else:
                item["abstain"] += 1
            if row["majority_vote"] and vote == row["majority_vote"]:
                item["with_majority"] += 1

    annual_map = {(row["iso3"], row["year"]): row for row in annual_rows if row["year"] in (2024, 2025)}
    out = []
    countries = sorted({iso3 for iso3, year in country_year if year in (2024, 2025)})

    for iso3 in countries:
        if (iso3, 2024) not in country_year or (iso3, 2025) not in country_year:
            continue
        if (iso3, 2024) not in annual_map or (iso3, 2025) not in annual_map:
            continue

        prepared = {}
        for year in (2024, 2025):
            country = country_year[(iso3, year)]
            world = world_mix[year]
            if not country["participated"] or not world["total"]:
                prepared[year] = None
                continue

            rate = (country["with_majority"] / country["participated"]) * 100
            yes_pct = (country["yes"] / country["participated"]) * 100
            no_pct = (country["no"] / country["participated"]) * 100
            abstain_pct = (country["abstain"] / country["participated"]) * 100
            world_yes = (world["yes"] / world["total"]) * 100
            world_no = (world["no"] / world["total"]) * 100
            world_abstain = (world["abstain"] / world["total"]) * 100
            mix_distance = (
                abs(yes_pct - world_yes)
                + abs(no_pct - world_no)
                + abs(abstain_pct - world_abstain)
            )
            prepared[year] = {
                "participated": country["participated"],
                "with_majority": country["with_majority"],
                "majority_rate": rate,
                "yes_pct": yes_pct,
                "no_pct": no_pct,
                "abstain_pct": abstain_pct,
                "world_yes_pct": world_yes,
                "world_no_pct": world_no,
                "world_abstain_pct": world_abstain,
                "mix_distance": mix_distance,
            }

        p3_24 = annual_map[(iso3, 2024)]["p3"]
        p3_25 = annual_map[(iso3, 2025)]["p3"]
        out.append(
            {
                "iso3": iso3,
                "p3_2024": round_or_blank(p3_24),
                "p3_2025": round_or_blank(p3_25),
                "p3_change": round_or_blank(p3_25 - p3_24 if p3_24 is not None and p3_25 is not None else None),
                "majority_alignment_rate_2024": round_or_blank(prepared[2024]["majority_rate"]),
                "majority_alignment_rate_2025": round_or_blank(prepared[2025]["majority_rate"]),
                "majority_alignment_change": round_or_blank(
                    prepared[2025]["majority_rate"] - prepared[2024]["majority_rate"]
                ),
                "participated_resolutions_2024": prepared[2024]["participated"],
                "participated_resolutions_2025": prepared[2025]["participated"],
                "with_majority_count_2024": prepared[2024]["with_majority"],
                "with_majority_count_2025": prepared[2025]["with_majority"],
                "yes_pct_proxy_2024": round_or_blank(prepared[2024]["yes_pct"], 1),
                "yes_pct_proxy_2025": round_or_blank(prepared[2025]["yes_pct"], 1),
                "no_pct_proxy_2024": round_or_blank(prepared[2024]["no_pct"], 1),
                "no_pct_proxy_2025": round_or_blank(prepared[2025]["no_pct"], 1),
                "abstain_pct_proxy_2024": round_or_blank(prepared[2024]["abstain_pct"], 1),
                "abstain_pct_proxy_2025": round_or_blank(prepared[2025]["abstain_pct"], 1),
                "world_yes_pct_2024": round_or_blank(prepared[2024]["world_yes_pct"], 1),
                "world_yes_pct_2025": round_or_blank(prepared[2025]["world_yes_pct"], 1),
                "world_no_pct_2024": round_or_blank(prepared[2024]["world_no_pct"], 1),
                "world_no_pct_2025": round_or_blank(prepared[2025]["world_no_pct"], 1),
                "world_abstain_pct_2024": round_or_blank(prepared[2024]["world_abstain_pct"], 1),
                "world_abstain_pct_2025": round_or_blank(prepared[2025]["world_abstain_pct"], 1),
                "vote_mix_distance_l1_2024": round_or_blank(prepared[2024]["mix_distance"]),
                "vote_mix_distance_l1_2025": round_or_blank(prepared[2025]["mix_distance"]),
                "vote_mix_distance_change": round_or_blank(
                    prepared[2025]["mix_distance"] - prepared[2024]["mix_distance"]
                ),
                "region": annual_map[(iso3, 2025)]["region"],
                "broad_region": annual_map[(iso3, 2025)]["broad_region"],
            }
        )

    out.sort(key=lambda row: float(row["majority_alignment_change"]))
    write_csv(OUT_DIR / "05_p3_majority_alignment_proxy.csv", list(out[0].keys()), out)
    return out


def output_06_topic_vote_shifts(topic_rows):
    world = defaultdict(
        lambda: defaultdict(lambda: {"yes": 0, "no": 0, "abstain": 0, "total": 0, "countries": set()})
    )
    for row in topic_rows:
        if row["year"] not in (2024, 2025):
            continue
        bucket = world[row["year"]][row["topic"]]
        bucket["yes"] += row["yes"]
        bucket["no"] += row["no"]
        bucket["abstain"] += row["abstain"]
        bucket["total"] += row["total"]
        bucket["countries"].add(row["country"])

    out = []
    topics = sorted(set(world[2024]) | set(world[2025]))
    for topic in topics:
        d24 = world[2024].get(topic, {"yes": 0, "no": 0, "abstain": 0, "total": 0, "countries": set()})
        d25 = world[2025].get(topic, {"yes": 0, "no": 0, "abstain": 0, "total": 0, "countries": set()})

        yes24 = (d24["yes"] / d24["total"] * 100) if d24["total"] else None
        no24 = (d24["no"] / d24["total"] * 100) if d24["total"] else None
        abstain24 = (d24["abstain"] / d24["total"] * 100) if d24["total"] else None
        yes25 = (d25["yes"] / d25["total"] * 100) if d25["total"] else None
        no25 = (d25["no"] / d25["total"] * 100) if d25["total"] else None
        abstain25 = (d25["abstain"] / d25["total"] * 100) if d25["total"] else None

        if d24["total"] and d25["total"]:
            status = "PRESENT_IN_BOTH"
        elif d25["total"]:
            status = "NEW_IN_2025"
        else:
            status = "DROPPED_FROM_2024"

        out.append(
            {
                "topic": topic,
                "status": status,
                "total_votes_2024": d24["total"],
                "countries_2024": len(d24["countries"]),
                "yes_pct_2024": round_or_blank(yes24, 1),
                "no_pct_2024": round_or_blank(no24, 1),
                "abstain_pct_2024": round_or_blank(abstain24, 1),
                "total_votes_2025": d25["total"],
                "countries_2025": len(d25["countries"]),
                "yes_pct_2025": round_or_blank(yes25, 1),
                "no_pct_2025": round_or_blank(no25, 1),
                "abstain_pct_2025": round_or_blank(abstain25, 1),
                "yes_pct_change": round_or_blank(
                    yes25 - yes24 if yes24 is not None and yes25 is not None else None,
                    2,
                ),
                "no_pct_change": round_or_blank(
                    no25 - no24 if no24 is not None and no25 is not None else None,
                    2,
                ),
                "abstain_pct_change": round_or_blank(
                    abstain25 - abstain24
                    if abstain24 is not None and abstain25 is not None
                    else None,
                    2,
                ),
            }
        )

    out.sort(
        key=lambda row: (
            float("inf") if row["yes_pct_change"] == "" else float(row["yes_pct_change"]),
            -int(row["total_votes_2025"] or 0),
            row["topic"],
        )
    )
    write_csv(OUT_DIR / "06_p3_topic_vote_shifts_2024_2025.csv", list(out[0].keys()), out)
    return out


def output_07_resolution_majority_summary_2025(raw_resolutions):
    rows = []
    for row in raw_resolutions:
        if row["year"] != 2025:
            continue
        rows.append(
            {
                "date": row["date"],
                "resolution": row["resolution"],
                "title": row["title"],
                "yes": row["yes"],
                "no": row["no"],
                "abstain": row["abstain"],
                "total": row["total"],
                "majority_vote": row["majority_vote"] or "",
                "majority_share": round_or_blank(row["majority_share"], 2),
                "majority_margin": round_or_blank(row["majority_margin"], 2),
                "non_yes_pct": round_or_blank(row["non_yes_pct"], 2),
                "no_pct": round_or_blank((row["no"] / row["total"]) * 100, 2),
                "abstain_pct": round_or_blank((row["abstain"] / row["total"]) * 100, 2),
                "tags": row["tags"],
            }
        )

    rows.sort(key=lambda row: (float(row["majority_share"]), float(row["majority_margin"]), row["resolution"]))
    write_csv(OUT_DIR / "07_p3_resolution_majority_summary_2025.csv", list(rows[0].keys()), rows)
    return rows


def output_08_key_country_topic_gap_changes(topic_rows, big_movers):
    world = defaultdict(
        lambda: defaultdict(lambda: {"yes": 0, "no": 0, "abstain": 0, "total": 0})
    )
    country = defaultdict(lambda: defaultdict(dict))
    for row in topic_rows:
        if row["year"] not in (2024, 2025):
            continue
        world_bucket = world[row["year"]][row["topic"]]
        world_bucket["yes"] += row["yes"]
        world_bucket["no"] += row["no"]
        world_bucket["abstain"] += row["abstain"]
        world_bucket["total"] += row["total"]
        country[(row["country"], row["year"])][row["topic"]] = row

    key_countries = {
        "USA",
        "CAN",
        "GBR",
        "FRA",
        "DEU",
        "RUS",
        "CHN",
        "ARG",
        "ISR",
        "UKR",
        "GEO",
        "FSM",
        "PRY",
    }
    for row in big_movers:
        key_countries.add(row["iso3"])

    out = []
    for iso3 in sorted(key_countries):
        topics = set(country[(iso3, 2024)]) | set(country[(iso3, 2025)])
        for topic in topics:
            c24 = country[(iso3, 2024)].get(topic)
            c25 = country[(iso3, 2025)].get(topic)
            w24 = world[2024].get(topic)
            w25 = world[2025].get(topic)
            if not c24 or not c25 or not w24 or not w25:
                continue
            if not c24["total"] or not c25["total"] or not w24["total"] or not w25["total"]:
                continue
            if w25["total"] < 500:
                continue

            country_yes_24 = (c24["yes"] / c24["total"]) * 100
            country_yes_25 = (c25["yes"] / c25["total"]) * 100
            world_yes_24 = (w24["yes"] / w24["total"]) * 100
            world_yes_25 = (w25["yes"] / w25["total"]) * 100
            gap_24 = country_yes_24 - world_yes_24
            gap_25 = country_yes_25 - world_yes_25

            out.append(
                {
                    "iso3": iso3,
                    "topic": topic,
                    "country_total_votes_2024": c24["total"],
                    "country_total_votes_2025": c25["total"],
                    "world_total_votes_2025": w25["total"],
                    "country_yes_pct_2024": round_or_blank(country_yes_24, 1),
                    "country_yes_pct_2025": round_or_blank(country_yes_25, 1),
                    "country_yes_pct_change": round_or_blank(country_yes_25 - country_yes_24, 1),
                    "world_yes_pct_2024": round_or_blank(world_yes_24, 1),
                    "world_yes_pct_2025": round_or_blank(world_yes_25, 1),
                    "world_yes_pct_change": round_or_blank(world_yes_25 - world_yes_24, 1),
                    "gap_vs_world_yes_2024": round_or_blank(gap_24, 1),
                    "gap_vs_world_yes_2025": round_or_blank(gap_25, 1),
                    "abs_gap_change": round_or_blank(abs(gap_25) - abs(gap_24), 1),
                }
            )

    out.sort(key=lambda row: (row["iso3"], float(row["abs_gap_change"]), -int(row["world_total_votes_2025"]), row["topic"]))
    write_csv(OUT_DIR / "08_p3_key_country_topic_gap_changes.csv", list(out[0].keys()), out)
    return out


def output_09_country_profile_2025(rows, proxy_rows):
    proxy_map = {row["iso3"]: row for row in proxy_rows}
    vals_2025 = [row["p3"] for row in rows if row["year"] == 2025 and row["p3"] is not None]
    world_avg_2025 = mean(vals_2025)

    out = []
    for row in rows:
        if row["year"] != 2025:
            continue
        proxy = proxy_map.get(row["iso3"], {})
        out.append(
            {
                "iso3": row["iso3"],
                "p3_2025": round_or_blank(row["p3"]),
                "p3_rank_2025": row["p3_rank"] if row["p3_rank"] is not None else "",
                "p1_2025": round_or_blank(row["p1"]),
                "p2_2025": round_or_blank(row["p2"]),
                "yes_2025": row["yes"],
                "no_2025": row["no"],
                "abstain_2025": row["abstain"],
                "total_2025": row["total"],
                "yes_pct_2025": round_or_blank((row["yes"] / row["total"]) * 100 if row["total"] else None, 1),
                "no_pct_2025": round_or_blank((row["no"] / row["total"]) * 100 if row["total"] else None, 1),
                "abstain_pct_2025": round_or_blank((row["abstain"] / row["total"]) * 100 if row["total"] else None, 1),
                "majority_alignment_rate_2025": proxy.get("majority_alignment_rate_2025", ""),
                "vote_mix_distance_l1_2025": proxy.get("vote_mix_distance_l1_2025", ""),
                "diff_from_world_avg_2025": round_or_blank(
                    row["p3"] - world_avg_2025 if row["p3"] is not None else None
                ),
                "region": row["region"],
                "broad_region": row["broad_region"],
            }
        )

    out.sort(key=lambda row: (-float(row["p3_2025"]), row["iso3"]))
    write_csv(OUT_DIR / "09_p3_country_profile_2025.csv", list(out[0].keys()), out)
    return out


def output_10_distribution_summary(rows):
    out = []
    for year in (2024, 2025):
        vals = sorted(row["p3"] for row in rows if row["year"] == year and row["p3"] is not None)
        out.append(
            {
                "year": year,
                "mean_p3": round_or_blank(mean(vals)),
                "median_p3": round_or_blank(median(vals)),
                "std_p3": round_or_blank(pstdev(vals)),
                "min_p3": round_or_blank(vals[0] if vals else None),
                "p10": round_or_blank(percentile(vals, 0.10)),
                "p25": round_or_blank(percentile(vals, 0.25)),
                "p75": round_or_blank(percentile(vals, 0.75)),
                "p90": round_or_blank(percentile(vals, 0.90)),
                "max_p3": round_or_blank(vals[-1] if vals else None),
                "countries_ge_95": sum(1 for value in vals if value >= 95),
                "countries_ge_90": sum(1 for value in vals if value >= 90),
                "countries_ge_80": sum(1 for value in vals if value >= 80),
                "countries_lt_50": sum(1 for value in vals if value < 50),
                "countries_lt_40": sum(1 for value in vals if value < 40),
                "countries_lt_20": sum(1 for value in vals if value < 20),
                "num_countries": len(vals),
            }
        )

    write_csv(OUT_DIR / "10_p3_distribution_summary_2024_2025.csv", list(out[0].keys()), out)
    return out


def output_11_key_country_history(rows):
    key = [
        "USA",
        "CAN",
        "GBR",
        "FRA",
        "DEU",
        "RUS",
        "CHN",
        "ARG",
        "ISR",
        "UKR",
        "GEO",
        "FSM",
        "PRY",
    ]
    out = []
    for row in rows:
        if row["iso3"] in key and 2015 <= row["year"] <= 2025:
            out.append(
                {
                    "iso3": row["iso3"],
                    "year": row["year"],
                    "p3_score": round_or_blank(row["p3"]),
                    "p3_rank": row["p3_rank"] if row["p3_rank"] is not None else "",
                    "yes": row["yes"],
                    "no": row["no"],
                    "abstain": row["abstain"],
                    "total": row["total"],
                }
            )

    out.sort(key=lambda row: (row["iso3"], row["year"]))
    write_csv(OUT_DIR / "11_p3_key_country_history.csv", list(out[0].keys()), out)
    return out


def output_12_global_outliers_2025(rows, proxy_rows):
    proxy_map = {row["iso3"]: row for row in proxy_rows}
    world_avg = mean(row["p3"] for row in rows if row["year"] == 2025 and row["p3"] is not None)

    broad_avg = {}
    for broad_region in {row["broad_region"] for row in rows if row["year"] == 2025 and row["broad_region"]}:
        vals = [
            row["p3"]
            for row in rows
            if row["year"] == 2025 and row["broad_region"] == broad_region and row["p3"] is not None
        ]
        broad_avg[broad_region] = mean(vals)

    out = []
    for row in rows:
        if row["year"] != 2025 or row["p3"] is None:
            continue
        proxy = proxy_map.get(row["iso3"], {})
        out.append(
            {
                "iso3": row["iso3"],
                "p3_2025": round_or_blank(row["p3"]),
                "world_avg_2025": round_or_blank(world_avg),
                "diff_from_world_avg": round_or_blank(row["p3"] - world_avg),
                "broad_region": row["broad_region"],
                "broad_region_avg_2025": round_or_blank(broad_avg[row["broad_region"]]),
                "diff_from_broad_region_avg": round_or_blank(
                    row["p3"] - broad_avg[row["broad_region"]]
                ),
                "region": row["region"],
                "majority_alignment_rate_2025": proxy.get("majority_alignment_rate_2025", ""),
                "vote_mix_distance_l1_2025": proxy.get("vote_mix_distance_l1_2025", ""),
                "total_2025": row["total"],
            }
        )

    out.sort(key=lambda row: float(row["diff_from_world_avg"]))
    write_csv(OUT_DIR / "12_p3_global_outliers_2025.csv", list(out[0].keys()), out)
    return out


def output_13_region_change_contributors(rows):
    d24 = {row["iso3"]: row for row in rows if row["year"] == 2024}
    d25 = {row["iso3"]: row for row in rows if row["year"] == 2025}

    region_members = defaultdict(list)
    for iso3, row in d25.items():
        if row["broad_region"]:
            region_members[row["broad_region"]].append(iso3)

    out = []
    for broad_region, members in region_members.items():
        n = len(members)
        vals24 = [d24[iso]["p3"] for iso in members if iso in d24 and d24[iso]["p3"] is not None]
        vals25 = [d25[iso]["p3"] for iso in members if iso in d25 and d25[iso]["p3"] is not None]
        avg_change = mean(vals25) - mean(vals24) if vals24 and vals25 else None
        for iso3 in members:
            if iso3 not in d24 or iso3 not in d25:
                continue
            p3_change = d25[iso3]["p3"] - d24[iso3]["p3"]
            out.append(
                {
                    "broad_region": broad_region,
                    "iso3": iso3,
                    "region": d25[iso3]["region"],
                    "p3_2024": round_or_blank(d24[iso3]["p3"]),
                    "p3_2025": round_or_blank(d25[iso3]["p3"]),
                    "p3_change": round_or_blank(p3_change),
                    "region_avg_change": round_or_blank(avg_change),
                    "contribution_to_region_avg_change": round_or_blank(p3_change / n),
                    "total_2024": d24[iso3]["total"],
                    "total_2025": d25[iso3]["total"],
                }
            )

    out.sort(
        key=lambda row: (
            row["broad_region"],
            -abs(float(row["contribution_to_region_avg_change"])),
            row["iso3"],
        )
    )
    write_csv(OUT_DIR / "13_p3_region_change_contributors.csv", list(out[0].keys()), out)
    return out


def main():
    annual_rows = load_annual_scores()
    topic_rows = load_topic_votes()
    raw_resolutions = load_raw_resolutions()

    output_01_world_avg_trend(annual_rows)
    shifts = output_02_country_shifts(annual_rows)
    big_movers = output_03_big_movers(shifts)
    output_04_region_summaries(annual_rows)
    proxy_rows = output_05_majority_alignment_proxy(raw_resolutions, annual_rows)
    output_06_topic_vote_shifts(topic_rows)
    output_07_resolution_majority_summary_2025(raw_resolutions)
    output_08_key_country_topic_gap_changes(topic_rows, big_movers)
    output_09_country_profile_2025(annual_rows, proxy_rows)
    output_10_distribution_summary(annual_rows)
    output_11_key_country_history(annual_rows)
    output_12_global_outliers_2025(annual_rows, proxy_rows)
    output_13_region_change_contributors(annual_rows)
    print(f"Wrote 13 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
