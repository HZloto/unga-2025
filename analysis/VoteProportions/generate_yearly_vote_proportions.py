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
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "unga_yearly_vote_proportions.csv"
DEFAULT_START_YEAR = 1946
DEFAULT_END_YEAR = 2025
DEFAULT_SC_FLAG = "0"
VOTE_VALUES = ("YES", "ABSTAIN", "NO")


def parse_year(date_value: str) -> int | None:
    match = re.match(r"^(\d{4})-", str(date_value).strip())
    if not match:
        return None
    return int(match.group(1))


def percentage(count: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{(count / denominator) * 100:.2f}"


def read_yearly_counts(
    input_path: Path,
    start_year: int,
    end_year: int,
    sc_flag: str,
) -> tuple[dict[int, Counter[str]], Counter[str]]:
    yearly_counts: dict[int, Counter[str]] = defaultdict(Counter)
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

            year_counts = yearly_counts[year]
            year_counts["resolution_count"] += 1
            year_counts["vote_slot_count"] += len(vote_data)

            for vote in vote_data.values():
                if vote in VOTE_VALUES:
                    year_counts[vote] += 1
                elif vote is None:
                    year_counts["not_recorded_count"] += 1
                else:
                    year_counts["unknown_vote_count"] += 1

    return yearly_counts, diagnostics


def build_output_rows(yearly_counts: dict[int, Counter[str]]) -> list[dict[str, int | str]]:
    output_rows: list[dict[str, int | str]] = []
    for year in sorted(yearly_counts):
        counts = yearly_counts[year]
        yes_count = counts["YES"]
        abstain_count = counts["ABSTAIN"]
        no_count = counts["NO"]
        recorded_vote_count = yes_count + abstain_count + no_count

        output_rows.append(
            {
                "year": year,
                "resolution_count": counts["resolution_count"],
                "vote_slot_count": counts["vote_slot_count"],
                "recorded_vote_count": recorded_vote_count,
                "yes_count": yes_count,
                "yes_pct": percentage(yes_count, recorded_vote_count),
                "abstain_count": abstain_count,
                "abstain_pct": percentage(abstain_count, recorded_vote_count),
                "no_count": no_count,
                "no_pct": percentage(no_count, recorded_vote_count),
                "not_recorded_count": counts["not_recorded_count"],
                "unknown_vote_count": counts["unknown_vote_count"],
            }
        )
    return output_rows


def write_csv(path: Path, rows: list[dict[str, int | str]]) -> None:
    fieldnames = [
        "year",
        "resolution_count",
        "vote_slot_count",
        "recorded_vote_count",
        "yes_count",
        "yes_pct",
        "abstain_count",
        "abstain_pct",
        "no_count",
        "no_pct",
        "not_recorded_count",
        "unknown_vote_count",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate yearly UNGA YES/ABSTAIN/NO vote proportions from "
            "the raw vote JSON CSV."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument(
        "--end-year",
        type=int,
        default=DEFAULT_END_YEAR,
        help="Inclusive end year. Defaults to 2025 to exclude partial 2026 data.",
    )
    parser.add_argument(
        "--sc-flag",
        default=DEFAULT_SC_FLAG,
        help="Rows with this sc_flag are included; 0 is UNGA and 1 is Security Council.",
    )
    args = parser.parse_args()

    yearly_counts, diagnostics = read_yearly_counts(
        args.input,
        args.start_year,
        args.end_year,
        str(args.sc_flag),
    )
    rows = build_output_rows(yearly_counts)
    write_csv(args.output, rows)

    print(f"Wrote {args.output}")
    print(f"Year rows: {len(rows)}")
    if rows:
        print(f"Year range in output: {rows[0]['year']}-{rows[-1]['year']}")
    print(f"Input rows read: {diagnostics['input_rows']}")
    print(f"Rows skipped for sc_flag: {diagnostics['skipped_sc_flag']}")
    print(f"Rows skipped for date/year filter: {diagnostics['skipped_bad_date'] + diagnostics['skipped_year_range']}")
    print(f"Rows skipped for bad date: {diagnostics['skipped_bad_date']}")


if __name__ == "__main__":
    main()
