#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.Thematic.generate_2025_theme_csvs import TaxonomyParser


DEFAULT_INPUT = REPO_ROOT / "data" / "un_votes_with_sc (1).csv"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_COUNTRIES = ("USA", "CPV")
DEFAULT_START_YEAR = 2024
DEFAULT_END_YEAR = 2025
DEFAULT_SC_FLAG = "0"
DEFAULT_LEVELS = ("topic_l1", "topic_l2", "topic_l3")
VOTE_VALUES = ("YES", "ABSTAIN", "NO")


def parse_year(date_value: str) -> int | None:
    match = re.match(r"^(\d{4})-", str(date_value).strip())
    if not match:
        return None
    return int(match.group(1))


def pct_value(count: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return (count / denominator) * 100


def format_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def make_stem(countries: tuple[str, ...], start_year: int, end_year: int) -> str:
    return f"{'_'.join(country.lower() for country in countries)}_theme_vote_proportions_{start_year}_{end_year}"


def read_country_yearly_topic_counts(
    input_path: Path,
    countries: tuple[str, ...],
    start_year: int,
    end_year: int,
    sc_flag: str,
    levels: tuple[str, ...],
) -> tuple[
    dict[str, dict[tuple[str, int, str], Counter[str]]],
    dict[str, set[str]],
    Counter[str],
]:
    country_set = {country.upper() for country in countries}
    parser = TaxonomyParser()
    counts_by_level = {level: defaultdict(Counter) for level in levels}
    topics_by_level = {level: set() for level in levels}
    diagnostics: Counter[str] = Counter()

    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            diagnostics["input_rows"] += 1

            if str(row.get("sc_flag", "")).strip() != sc_flag:
                diagnostics["skipped_sc_flag"] += 1
                continue

            year = parse_year(row.get("Date", ""))
            if year is None:
                diagnostics["skipped_bad_date"] += 1
                continue
            if year < start_year or year > end_year:
                diagnostics["skipped_year_range"] += 1
                continue

            diagnostics["included_rows"] += 1

            raw_tags = row.get("tags", "") or ""
            parsed_paths = parser.parse(raw_tags)
            unique_topics = {
                level: {
                    getattr(parsed_path, level)
                    for parsed_path in parsed_paths
                    if getattr(parsed_path, level)
                }
                for level in levels
            }
            if not any(unique_topics.values()):
                diagnostics["empty_tag_rows"] += 1

            resolution = row.get("Resolution", "")
            try:
                vote_data: Any = json.loads(row.get("vote_data", ""))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid vote_data JSON for {resolution}") from exc
            if not isinstance(vote_data, dict):
                raise ValueError(f"Expected vote_data object for {resolution}")

            for level in levels:
                for topic in unique_topics[level]:
                    topics_by_level[level].add(topic)

            for country in country_set:
                for level in levels:
                    for topic in unique_topics[level]:
                        counts = counts_by_level[level][(country, year, topic)]
                        counts["resolution_count"] += 1

                        if country not in vote_data:
                            counts["country_missing_count"] += 1
                            continue

                        vote = vote_data[country]
                        if vote in VOTE_VALUES:
                            counts[vote] += 1
                        elif vote is None:
                            counts["not_recorded_count"] += 1
                        else:
                            counts["unknown_vote_count"] += 1

    return counts_by_level, topics_by_level, diagnostics


def build_metric_bundle(counts: Counter[str]) -> dict[str, int | float | None]:
    yes_count = counts["YES"]
    abstain_count = counts["ABSTAIN"]
    no_count = counts["NO"]
    recorded_vote_count = yes_count + abstain_count + no_count
    resolution_count = counts["resolution_count"]

    return {
        "resolution_count": resolution_count,
        "recorded_vote_count": recorded_vote_count,
        "not_recorded_count": counts["not_recorded_count"],
        "country_missing_count": counts["country_missing_count"],
        "unknown_vote_count": counts["unknown_vote_count"],
        "yes_count": yes_count,
        "yes_pct": pct_value(yes_count, recorded_vote_count),
        "abstain_count": abstain_count,
        "abstain_pct": pct_value(abstain_count, recorded_vote_count),
        "no_count": no_count,
        "no_pct": pct_value(no_count, recorded_vote_count),
        "not_recorded_pct": pct_value(counts["not_recorded_count"], resolution_count),
    }


def build_long_rows_for_level(
    counts_for_level: dict[tuple[str, int, str], Counter[str]],
    countries: tuple[str, ...],
    years: tuple[int, ...],
    topics: list[str],
    topic_field: str,
) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []

    for country in countries:
        for topic in topics:
            for year in years:
                metrics = build_metric_bundle(counts_for_level[(country, year, topic)])
                rows.append(
                    {
                        "country": country,
                        topic_field: topic,
                        "year": year,
                        "resolution_count": metrics["resolution_count"],
                        "recorded_vote_count": metrics["recorded_vote_count"],
                        "yes_count": metrics["yes_count"],
                        "yes_pct": format_pct(metrics["yes_pct"]),
                        "abstain_count": metrics["abstain_count"],
                        "abstain_pct": format_pct(metrics["abstain_pct"]),
                        "no_count": metrics["no_count"],
                        "no_pct": format_pct(metrics["no_pct"]),
                        "not_recorded_count": metrics["not_recorded_count"],
                        "not_recorded_pct": format_pct(metrics["not_recorded_pct"]),
                        "country_missing_count": metrics["country_missing_count"],
                        "unknown_vote_count": metrics["unknown_vote_count"],
                    }
                )

    return rows


def build_change_rows_for_level(
    counts_for_level: dict[tuple[str, int, str], Counter[str]],
    countries: tuple[str, ...],
    start_year: int,
    end_year: int,
    topics: list[str],
    topic_field: str,
) -> tuple[list[str], list[dict[str, int | str]]]:
    start_prefix = str(start_year)
    end_prefix = str(end_year)
    fieldnames = [
        "country",
        topic_field,
        "status",
        f"{start_prefix}_resolution_count",
        f"{end_prefix}_resolution_count",
        "resolution_count_change",
        f"{start_prefix}_recorded_vote_count",
        f"{end_prefix}_recorded_vote_count",
        "recorded_vote_count_change",
        f"{start_prefix}_not_recorded_count",
        f"{end_prefix}_not_recorded_count",
        "not_recorded_count_change",
        f"{start_prefix}_country_missing_count",
        f"{end_prefix}_country_missing_count",
        "country_missing_count_change",
        f"{start_prefix}_unknown_vote_count",
        f"{end_prefix}_unknown_vote_count",
        "unknown_vote_count_change",
    ]

    for vote in ("yes", "abstain", "no"):
        fieldnames.extend(
            [
                f"{start_prefix}_{vote}_count",
                f"{end_prefix}_{vote}_count",
                f"{vote}_count_change",
                f"{start_prefix}_{vote}_pct",
                f"{end_prefix}_{vote}_pct",
                f"{vote}_pct_change_pp",
            ]
        )
    fieldnames.append("abs_yes_pct_change_pp")

    rows: list[dict[str, int | str]] = []
    for country in countries:
        for topic in topics:
            start_metrics = build_metric_bundle(counts_for_level[(country, start_year, topic)])
            end_metrics = build_metric_bundle(counts_for_level[(country, end_year, topic)])

            start_resolution_count = int(start_metrics["resolution_count"])
            end_resolution_count = int(end_metrics["resolution_count"])
            if start_resolution_count and end_resolution_count:
                status = "PRESENT_IN_BOTH"
            elif end_resolution_count:
                status = "NEW_IN_2025"
            elif start_resolution_count:
                status = "DROPPED_FROM_2024"
            else:
                status = "ABSENT_IN_BOTH"

            if status == "ABSENT_IN_BOTH":
                continue

            start_yes_pct = start_metrics["yes_pct"]
            end_yes_pct = end_metrics["yes_pct"]
            start_abstain_pct = start_metrics["abstain_pct"]
            end_abstain_pct = end_metrics["abstain_pct"]
            start_no_pct = start_metrics["no_pct"]
            end_no_pct = end_metrics["no_pct"]

            yes_pct_change = None
            if start_yes_pct is not None and end_yes_pct is not None:
                yes_pct_change = end_yes_pct - start_yes_pct

            abstain_pct_change = None
            if start_abstain_pct is not None and end_abstain_pct is not None:
                abstain_pct_change = end_abstain_pct - start_abstain_pct

            no_pct_change = None
            if start_no_pct is not None and end_no_pct is not None:
                no_pct_change = end_no_pct - start_no_pct

            row: dict[str, int | str] = {
                "country": country,
                topic_field: topic,
                "status": status,
                f"{start_prefix}_resolution_count": start_resolution_count,
                f"{end_prefix}_resolution_count": end_resolution_count,
                "resolution_count_change": end_resolution_count - start_resolution_count,
                f"{start_prefix}_recorded_vote_count": int(start_metrics["recorded_vote_count"]),
                f"{end_prefix}_recorded_vote_count": int(end_metrics["recorded_vote_count"]),
                "recorded_vote_count_change": int(end_metrics["recorded_vote_count"])
                - int(start_metrics["recorded_vote_count"]),
                f"{start_prefix}_not_recorded_count": int(start_metrics["not_recorded_count"]),
                f"{end_prefix}_not_recorded_count": int(end_metrics["not_recorded_count"]),
                "not_recorded_count_change": int(end_metrics["not_recorded_count"])
                - int(start_metrics["not_recorded_count"]),
                f"{start_prefix}_country_missing_count": int(
                    start_metrics["country_missing_count"]
                ),
                f"{end_prefix}_country_missing_count": int(
                    end_metrics["country_missing_count"]
                ),
                "country_missing_count_change": int(end_metrics["country_missing_count"])
                - int(start_metrics["country_missing_count"]),
                f"{start_prefix}_unknown_vote_count": int(start_metrics["unknown_vote_count"]),
                f"{end_prefix}_unknown_vote_count": int(end_metrics["unknown_vote_count"]),
                "unknown_vote_count_change": int(end_metrics["unknown_vote_count"])
                - int(start_metrics["unknown_vote_count"]),
                f"{start_prefix}_yes_count": int(start_metrics["yes_count"]),
                f"{end_prefix}_yes_count": int(end_metrics["yes_count"]),
                "yes_count_change": int(end_metrics["yes_count"]) - int(start_metrics["yes_count"]),
                f"{start_prefix}_yes_pct": format_pct(start_yes_pct),
                f"{end_prefix}_yes_pct": format_pct(end_yes_pct),
                "yes_pct_change_pp": format_pct(yes_pct_change),
                f"{start_prefix}_abstain_count": int(start_metrics["abstain_count"]),
                f"{end_prefix}_abstain_count": int(end_metrics["abstain_count"]),
                "abstain_count_change": int(end_metrics["abstain_count"])
                - int(start_metrics["abstain_count"]),
                f"{start_prefix}_abstain_pct": format_pct(start_abstain_pct),
                f"{end_prefix}_abstain_pct": format_pct(end_abstain_pct),
                "abstain_pct_change_pp": format_pct(abstain_pct_change),
                f"{start_prefix}_no_count": int(start_metrics["no_count"]),
                f"{end_prefix}_no_count": int(end_metrics["no_count"]),
                "no_count_change": int(end_metrics["no_count"]) - int(start_metrics["no_count"]),
                f"{start_prefix}_no_pct": format_pct(start_no_pct),
                f"{end_prefix}_no_pct": format_pct(end_no_pct),
                "no_pct_change_pp": format_pct(no_pct_change),
                "abs_yes_pct_change_pp": format_pct(
                    abs(yes_pct_change) if yes_pct_change is not None else None
                ),
            }
            rows.append(row)

    status_rank = {
        "PRESENT_IN_BOTH": 0,
        "NEW_IN_2025": 1,
        "DROPPED_FROM_2024": 2,
    }

    def sort_key(row: dict[str, int | str]) -> tuple[object, ...]:
        abs_change_raw = row["abs_yes_pct_change_pp"]
        abs_change = float(abs_change_raw) if abs_change_raw != "" else -1.0
        end_resolution_count = int(row[f"{end_prefix}_resolution_count"])
        return (
            row["country"],
            status_rank[row["status"]],
            -abs_change,
            -end_resolution_count,
            row[topic_field],
        )

    rows.sort(key=sort_key)
    return fieldnames, rows


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, int | str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate country-level UNGA vote proportions by thematic level "
            "(topic_l1/topic_l2/topic_l3)."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--countries", nargs="+", default=list(DEFAULT_COUNTRIES))
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR)
    parser.add_argument("--levels", nargs="+", default=list(DEFAULT_LEVELS))
    parser.add_argument(
        "--sc-flag",
        default=DEFAULT_SC_FLAG,
        help="Rows with this sc_flag are included; 0 is UNGA and 1 is Security Council.",
    )
    args = parser.parse_args()

    countries = tuple(country.upper() for country in args.countries)
    levels = tuple(args.levels)
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    counts_by_level, topics_by_level, diagnostics = read_country_yearly_topic_counts(
        args.input,
        countries,
        args.start_year,
        args.end_year,
        str(args.sc_flag),
        levels,
    )

    years = tuple(range(args.start_year, args.end_year + 1))
    stem = make_stem(countries, args.start_year, args.end_year)
    combined_long_rows: list[dict[str, int | str]] = []
    combined_change_rows: list[dict[str, int | str]] = []

    long_fieldnames = [
        "country",
        "topic_level",
        "topic_label",
        "year",
        "resolution_count",
        "recorded_vote_count",
        "yes_count",
        "yes_pct",
        "abstain_count",
        "abstain_pct",
        "no_count",
        "no_pct",
        "not_recorded_count",
        "not_recorded_pct",
        "country_missing_count",
        "unknown_vote_count",
    ]
    change_fieldnames = [
        "country",
        "topic_level",
        "topic_label",
        "status",
        f"{args.start_year}_resolution_count",
        f"{args.end_year}_resolution_count",
        "resolution_count_change",
        f"{args.start_year}_recorded_vote_count",
        f"{args.end_year}_recorded_vote_count",
        "recorded_vote_count_change",
        f"{args.start_year}_not_recorded_count",
        f"{args.end_year}_not_recorded_count",
        "not_recorded_count_change",
        f"{args.start_year}_country_missing_count",
        f"{args.end_year}_country_missing_count",
        "country_missing_count_change",
        f"{args.start_year}_unknown_vote_count",
        f"{args.end_year}_unknown_vote_count",
        "unknown_vote_count_change",
        f"{args.start_year}_yes_count",
        f"{args.end_year}_yes_count",
        "yes_count_change",
        f"{args.start_year}_yes_pct",
        f"{args.end_year}_yes_pct",
        "yes_pct_change_pp",
        f"{args.start_year}_abstain_count",
        f"{args.end_year}_abstain_count",
        "abstain_count_change",
        f"{args.start_year}_abstain_pct",
        f"{args.end_year}_abstain_pct",
        "abstain_pct_change_pp",
        f"{args.start_year}_no_count",
        f"{args.end_year}_no_count",
        "no_count_change",
        f"{args.start_year}_no_pct",
        f"{args.end_year}_no_pct",
        "no_pct_change_pp",
        "abs_yes_pct_change_pp",
    ]

    for level in levels:
        topic_field = level
        topics = sorted(topics_by_level[level])

        level_long_rows = build_long_rows_for_level(
            counts_by_level[level],
            countries,
            years,
            topics,
            topic_field,
        )
        level_change_fieldnames, level_change_rows = build_change_rows_for_level(
            counts_by_level[level],
            countries,
            args.start_year,
            args.end_year,
            topics,
            topic_field,
        )

        level_long_path = output_dir / f"{'_'.join(country.lower() for country in countries)}_{level}_vote_proportions_{args.start_year}_{args.end_year}.csv"
        level_change_path = output_dir / f"{'_'.join(country.lower() for country in countries)}_{level}_vote_proportions_{args.start_year}_{args.end_year}_change.csv"
        write_csv(
            level_long_path,
            [
                "country",
                topic_field,
                "year",
                "resolution_count",
                "recorded_vote_count",
                "yes_count",
                "yes_pct",
                "abstain_count",
                "abstain_pct",
                "no_count",
                "no_pct",
                "not_recorded_count",
                "not_recorded_pct",
                "country_missing_count",
                "unknown_vote_count",
            ],
            level_long_rows,
        )
        write_csv(level_change_path, level_change_fieldnames, level_change_rows)

        combined_long_rows.extend(
            {
                "country": row["country"],
                "topic_level": level,
                "topic_label": row[topic_field],
                "year": row["year"],
                "resolution_count": row["resolution_count"],
                "recorded_vote_count": row["recorded_vote_count"],
                "yes_count": row["yes_count"],
                "yes_pct": row["yes_pct"],
                "abstain_count": row["abstain_count"],
                "abstain_pct": row["abstain_pct"],
                "no_count": row["no_count"],
                "no_pct": row["no_pct"],
                "not_recorded_count": row["not_recorded_count"],
                "not_recorded_pct": row["not_recorded_pct"],
                "country_missing_count": row["country_missing_count"],
                "unknown_vote_count": row["unknown_vote_count"],
            }
            for row in level_long_rows
        )
        combined_change_rows.extend(
            {
                "country": row["country"],
                "topic_level": level,
                "topic_label": row[topic_field],
                "status": row["status"],
                f"{args.start_year}_resolution_count": row[f"{args.start_year}_resolution_count"],
                f"{args.end_year}_resolution_count": row[f"{args.end_year}_resolution_count"],
                "resolution_count_change": row["resolution_count_change"],
                f"{args.start_year}_recorded_vote_count": row[
                    f"{args.start_year}_recorded_vote_count"
                ],
                f"{args.end_year}_recorded_vote_count": row[
                    f"{args.end_year}_recorded_vote_count"
                ],
                "recorded_vote_count_change": row["recorded_vote_count_change"],
                f"{args.start_year}_not_recorded_count": row[
                    f"{args.start_year}_not_recorded_count"
                ],
                f"{args.end_year}_not_recorded_count": row[
                    f"{args.end_year}_not_recorded_count"
                ],
                "not_recorded_count_change": row["not_recorded_count_change"],
                f"{args.start_year}_country_missing_count": row[
                    f"{args.start_year}_country_missing_count"
                ],
                f"{args.end_year}_country_missing_count": row[
                    f"{args.end_year}_country_missing_count"
                ],
                "country_missing_count_change": row["country_missing_count_change"],
                f"{args.start_year}_unknown_vote_count": row[
                    f"{args.start_year}_unknown_vote_count"
                ],
                f"{args.end_year}_unknown_vote_count": row[
                    f"{args.end_year}_unknown_vote_count"
                ],
                "unknown_vote_count_change": row["unknown_vote_count_change"],
                f"{args.start_year}_yes_count": row[f"{args.start_year}_yes_count"],
                f"{args.end_year}_yes_count": row[f"{args.end_year}_yes_count"],
                "yes_count_change": row["yes_count_change"],
                f"{args.start_year}_yes_pct": row[f"{args.start_year}_yes_pct"],
                f"{args.end_year}_yes_pct": row[f"{args.end_year}_yes_pct"],
                "yes_pct_change_pp": row["yes_pct_change_pp"],
                f"{args.start_year}_abstain_count": row[
                    f"{args.start_year}_abstain_count"
                ],
                f"{args.end_year}_abstain_count": row[f"{args.end_year}_abstain_count"],
                "abstain_count_change": row["abstain_count_change"],
                f"{args.start_year}_abstain_pct": row[f"{args.start_year}_abstain_pct"],
                f"{args.end_year}_abstain_pct": row[f"{args.end_year}_abstain_pct"],
                "abstain_pct_change_pp": row["abstain_pct_change_pp"],
                f"{args.start_year}_no_count": row[f"{args.start_year}_no_count"],
                f"{args.end_year}_no_count": row[f"{args.end_year}_no_count"],
                "no_count_change": row["no_count_change"],
                f"{args.start_year}_no_pct": row[f"{args.start_year}_no_pct"],
                f"{args.end_year}_no_pct": row[f"{args.end_year}_no_pct"],
                "no_pct_change_pp": row["no_pct_change_pp"],
                "abs_yes_pct_change_pp": row["abs_yes_pct_change_pp"],
            }
            for row in level_change_rows
        )

        print(f"Wrote {level_long_path}")
        print(f"Wrote {level_change_path}")

    combined_long_rows.sort(
        key=lambda row: (
            row["country"],
            row["topic_level"],
            row["topic_label"],
            int(row["year"]),
        )
    )
    combined_change_rows.sort(
        key=lambda row: (
            row["country"],
            row["topic_level"],
            0 if row["status"] == "PRESENT_IN_BOTH" else 1 if row["status"] == "NEW_IN_2025" else 2,
            -(float(row["abs_yes_pct_change_pp"]) if row["abs_yes_pct_change_pp"] != "" else -1.0),
            -int(row[f"{args.end_year}_resolution_count"]),
            row["topic_label"],
        )
    )

    combined_long_path = output_dir / f"{stem}.csv"
    combined_change_path = output_dir / f"{stem}_change.csv"
    write_csv(combined_long_path, long_fieldnames, combined_long_rows)
    write_csv(combined_change_path, change_fieldnames, combined_change_rows)

    print(f"Wrote {combined_long_path}")
    print(f"Wrote {combined_change_path}")
    print(f"Input rows read: {diagnostics['input_rows']}")
    print(f"Rows skipped for sc_flag: {diagnostics['skipped_sc_flag']}")
    print(
        "Rows skipped for date/year filter: "
        f"{diagnostics['skipped_bad_date'] + diagnostics['skipped_year_range']}"
    )
    print(f"Rows with empty tags: {diagnostics['empty_tag_rows']}")
    for level in levels:
        print(f"{level} topics: {len(topics_by_level[level])}")


if __name__ == "__main__":
    main()
