#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data" / "un_votes_with_sc (1).csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "usa_cpv_vote_proportions_2024_2025.csv"
DEFAULT_CHANGE_OUTPUT = (
    Path(__file__).resolve().parent / "usa_cpv_vote_proportions_2024_2025_change.csv"
)
DEFAULT_COUNTRIES = ("USA", "CPV")
DEFAULT_START_YEAR = 2024
DEFAULT_END_YEAR = 2025
DEFAULT_SC_FLAG = "0"
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


def read_country_yearly_counts(
    input_path: Path,
    countries: tuple[str, ...],
    start_year: int,
    end_year: int,
    sc_flag: str,
) -> tuple[dict[tuple[str, int], Counter[str]], Counter[str]]:
    country_set = {country.upper() for country in countries}
    yearly_counts: dict[tuple[str, int], Counter[str]] = defaultdict(Counter)
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

            resolution = row.get("Resolution", "")
            try:
                vote_data: Any = json.loads(row.get("vote_data", ""))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid vote_data JSON for {resolution}") from exc
            if not isinstance(vote_data, dict):
                raise ValueError(f"Expected vote_data object for {resolution}")

            for country in country_set:
                counts = yearly_counts[(country, year)]
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

    return yearly_counts, diagnostics


def build_long_rows(
    yearly_counts: dict[tuple[str, int], Counter[str]],
    countries: tuple[str, ...],
    start_year: int,
    end_year: int,
) -> list[dict[str, int | str]]:
    output_rows: list[dict[str, int | str]] = []

    for country in countries:
        for year in range(start_year, end_year + 1):
            counts = yearly_counts[(country, year)]
            yes_count = counts["YES"]
            abstain_count = counts["ABSTAIN"]
            no_count = counts["NO"]
            recorded_vote_count = yes_count + abstain_count + no_count
            resolution_count = counts["resolution_count"]

            output_rows.append(
                {
                    "country": country,
                    "year": year,
                    "resolution_count": resolution_count,
                    "recorded_vote_count": recorded_vote_count,
                    "yes_count": yes_count,
                    "yes_pct": format_pct(pct_value(yes_count, recorded_vote_count)),
                    "abstain_count": abstain_count,
                    "abstain_pct": format_pct(
                        pct_value(abstain_count, recorded_vote_count)
                    ),
                    "no_count": no_count,
                    "no_pct": format_pct(pct_value(no_count, recorded_vote_count)),
                    "not_recorded_count": counts["not_recorded_count"],
                    "not_recorded_pct": format_pct(
                        pct_value(counts["not_recorded_count"], resolution_count)
                    ),
                    "country_missing_count": counts["country_missing_count"],
                    "unknown_vote_count": counts["unknown_vote_count"],
                }
            )

    return output_rows


def build_change_rows(
    yearly_counts: dict[tuple[str, int], Counter[str]],
    countries: tuple[str, ...],
    start_year: int,
    end_year: int,
) -> tuple[list[str], list[dict[str, int | str]]]:
    start_prefix = str(start_year)
    end_prefix = str(end_year)
    fieldnames = [
        "country",
        f"{start_prefix}_resolution_count",
        f"{end_prefix}_resolution_count",
        f"{start_prefix}_recorded_vote_count",
        f"{end_prefix}_recorded_vote_count",
        "recorded_vote_count_change",
        f"{start_prefix}_not_recorded_count",
        f"{end_prefix}_not_recorded_count",
        "not_recorded_count_change",
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

    rows: list[dict[str, int | str]] = []
    for country in countries:
        start_counts = yearly_counts[(country, start_year)]
        end_counts = yearly_counts[(country, end_year)]

        start_recorded = (
            start_counts["YES"] + start_counts["ABSTAIN"] + start_counts["NO"]
        )
        end_recorded = end_counts["YES"] + end_counts["ABSTAIN"] + end_counts["NO"]

        row: dict[str, int | str] = {
            "country": country,
            f"{start_prefix}_resolution_count": start_counts["resolution_count"],
            f"{end_prefix}_resolution_count": end_counts["resolution_count"],
            f"{start_prefix}_recorded_vote_count": start_recorded,
            f"{end_prefix}_recorded_vote_count": end_recorded,
            "recorded_vote_count_change": end_recorded - start_recorded,
            f"{start_prefix}_not_recorded_count": start_counts["not_recorded_count"],
            f"{end_prefix}_not_recorded_count": end_counts["not_recorded_count"],
            "not_recorded_count_change": end_counts["not_recorded_count"]
            - start_counts["not_recorded_count"],
        }

        for vote_label, vote_key in (
            ("yes", "YES"),
            ("abstain", "ABSTAIN"),
            ("no", "NO"),
        ):
            start_count = start_counts[vote_key]
            end_count = end_counts[vote_key]
            start_pct = pct_value(start_count, start_recorded)
            end_pct = pct_value(end_count, end_recorded)
            pct_change = None
            if start_pct is not None and end_pct is not None:
                pct_change = end_pct - start_pct

            row.update(
                {
                    f"{start_prefix}_{vote_label}_count": start_count,
                    f"{end_prefix}_{vote_label}_count": end_count,
                    f"{vote_label}_count_change": end_count - start_count,
                    f"{start_prefix}_{vote_label}_pct": format_pct(start_pct),
                    f"{end_prefix}_{vote_label}_pct": format_pct(end_pct),
                    f"{vote_label}_pct_change_pp": format_pct(pct_change),
                }
            )

        rows.append(row)

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
        description="Generate country-level UNGA YES/ABSTAIN/NO vote proportions."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--change-output", type=Path, default=DEFAULT_CHANGE_OUTPUT)
    parser.add_argument("--countries", nargs="+", default=list(DEFAULT_COUNTRIES))
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR)
    parser.add_argument(
        "--sc-flag",
        default=DEFAULT_SC_FLAG,
        help="Rows with this sc_flag are included; 0 is UNGA and 1 is Security Council.",
    )
    args = parser.parse_args()

    countries = tuple(country.upper() for country in args.countries)
    yearly_counts, diagnostics = read_country_yearly_counts(
        args.input,
        countries,
        args.start_year,
        args.end_year,
        str(args.sc_flag),
    )

    long_rows = build_long_rows(
        yearly_counts,
        countries,
        args.start_year,
        args.end_year,
    )
    long_fieldnames = [
        "country",
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
    write_csv(args.output, long_fieldnames, long_rows)

    change_fieldnames, change_rows = build_change_rows(
        yearly_counts,
        countries,
        args.start_year,
        args.end_year,
    )
    write_csv(args.change_output, change_fieldnames, change_rows)

    print(f"Wrote {args.output}")
    print(f"Wrote {args.change_output}")
    print(f"Country-year rows: {len(long_rows)}")
    print(f"Input rows read: {diagnostics['input_rows']}")
    print(f"Rows skipped for sc_flag: {diagnostics['skipped_sc_flag']}")
    print(
        "Rows skipped for date/year filter: "
        f"{diagnostics['skipped_bad_date'] + diagnostics['skipped_year_range']}"
    )
    print(f"Rows skipped for bad date: {diagnostics['skipped_bad_date']}")


if __name__ == "__main__":
    main()
