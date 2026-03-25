#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DEFAULT_DENOMINATOR = 192
DEFAULT_INPUT = Path(__file__).resolve().parent / "ga_2025_geographic_mapping.csv"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent


def default_output_prefix(input_path: Path) -> str:
    stem = input_path.stem
    if stem.endswith("_geographic_mapping"):
        return stem.replace("_geographic_mapping", "_geo")
    return stem


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_single_value_summary(
    rows: list[dict[str, str]],
    column_name: str,
    denominator: int,
) -> list[dict[str, str | int]]:
    tag_to_resolutions: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        tag = (row.get(column_name) or "").strip()
        resolution = (row.get("resolution_number") or "").strip()
        if not tag or not resolution:
            continue
        tag_to_resolutions[tag].add(resolution)

    pct_column = f"pct_of_{denominator}"
    summary_rows: list[dict[str, str | int]] = []
    for tag, resolutions in sorted(
        tag_to_resolutions.items(),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        resolution_count = len(resolutions)
        summary_rows.append(
            {
                column_name: tag,
                "resolution_count": resolution_count,
                pct_column: f"{(resolution_count / denominator) * 100:.2f}",
            }
        )

    return summary_rows


def build_exploded_summary(
    rows: list[dict[str, str]],
    source_column: str,
    output_column: str,
    denominator: int,
) -> list[dict[str, str | int]]:
    tag_to_resolutions: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        resolution = (row.get("resolution_number") or "").strip()
        raw_values = row.get(source_column) or ""
        if not resolution or not raw_values.strip():
            continue

        values = {value.strip() for value in raw_values.split(";") if value.strip()}
        for value in values:
            tag_to_resolutions[value].add(resolution)

    pct_column = f"pct_of_{denominator}"
    summary_rows: list[dict[str, str | int]] = []
    for tag, resolutions in sorted(
        tag_to_resolutions.items(),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        resolution_count = len(resolutions)
        summary_rows.append(
            {
                output_column: tag,
                "resolution_count": resolution_count,
                pct_column: f"{(resolution_count / denominator) * 100:.2f}",
            }
        )

    return summary_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str | int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 2025 geographic hierarchy summaries from the manual mapping CSV.",
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--denominator", type=int, default=DEFAULT_DENOMINATOR)
    parser.add_argument("--output-prefix")
    args = parser.parse_args()

    rows = read_rows(args.input)
    if len(rows) != args.denominator:
        raise ValueError(
            f"Expected {args.denominator} rows in {args.input}, found {len(rows)}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    pct_column = f"pct_of_{args.denominator}"
    output_prefix = args.output_prefix or default_output_prefix(args.input)

    l1_rows = build_single_value_summary(rows, "geo_l1", args.denominator)
    l2_rows = build_single_value_summary(rows, "geo_l2", args.denominator)
    l3_rows = build_exploded_summary(
        rows,
        "geo_l3_candidates",
        "geo_l3",
        args.denominator,
    )

    l1_output = args.output_dir / f"{output_prefix}_l1_summary.csv"
    l2_output = args.output_dir / f"{output_prefix}_l2_summary.csv"
    l3_output = args.output_dir / f"{output_prefix}_l3_summary.csv"

    write_csv(l1_output, ["geo_l1", "resolution_count", pct_column], l1_rows)
    write_csv(l2_output, ["geo_l2", "resolution_count", pct_column], l2_rows)
    write_csv(l3_output, ["geo_l3", "resolution_count", pct_column], l3_rows)

    print(f"Input rows: {len(rows)}")
    print(f"Wrote {l1_output}")
    print(f"Wrote {l2_output}")
    print(f"Wrote {l3_output}")


if __name__ == "__main__":
    main()
