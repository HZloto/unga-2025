#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from un_classification import un_classification


DEFAULT_INPUT = REPO_ROOT / "data" / "un_votes_with_sc (1).csv"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_YEAR = 2025
DEFAULT_DENOMINATOR = 192
DEFAULT_SC_FLAG = "0"


@dataclass(frozen=True)
class ParsedPath:
    topic_l1: str
    topic_l2: str | None
    topic_l3: str | None
    used_fallback: bool = False


def normalize(text: str) -> str:
    return " ".join(text.strip().split())


def tokenize_label(label: str) -> tuple[str, ...]:
    return tuple(normalize(part) for part in label.split(",") if normalize(part))


class TaxonomyParser:
    def __init__(self) -> None:
        self.l1_candidates: list[tuple[tuple[str, ...], str]] = []
        self.l2_by_l1: dict[str, list[tuple[tuple[str, ...], str]]] = {}
        self.l3_by_pair: dict[tuple[str, str], list[tuple[tuple[str, ...], str]]] = {}

        for topic_l1, l2_map in un_classification.items():
            self.l1_candidates.append((tokenize_label(topic_l1), topic_l1))

            l2_candidates: list[tuple[tuple[str, ...], str]] = []
            for topic_l2, l3_values in l2_map.items():
                l2_candidates.append((tokenize_label(topic_l2), topic_l2))
                self.l3_by_pair[(topic_l1, topic_l2)] = [
                    (tokenize_label(topic_l3), topic_l3) for topic_l3 in l3_values
                ]

            self.l2_by_l1[topic_l1] = sorted(
                l2_candidates,
                key=lambda item: (-len(item[0]), item[1]),
            )

        self.l1_candidates.sort(key=lambda item: (-len(item[0]), item[1]))

        for key, candidates in self.l3_by_pair.items():
            self.l3_by_pair[key] = sorted(
                candidates,
                key=lambda item: (-len(item[0]), item[1]),
            )

    @staticmethod
    def _matching_candidates(
        tokens: tuple[str, ...],
        start: int,
        candidates: list[tuple[tuple[str, ...], str]],
    ) -> list[tuple[tuple[str, ...], str]]:
        matches: list[tuple[tuple[str, ...], str]] = []
        for token_parts, label in candidates:
            stop = start + len(token_parts)
            if tokens[start:stop] == token_parts:
                matches.append((token_parts, label))
        return matches

    def _parse_tokens(
        self,
        tokens: tuple[str, ...],
        allow_unknown_l3: bool,
    ) -> tuple[ParsedPath, ...] | None:
        @lru_cache(maxsize=None)
        def starts_l1(position: int) -> bool:
            return bool(self._matching_candidates(tokens, position, self.l1_candidates))

        def unknown_l3_options(position: int) -> list[tuple[int, str]]:
            if position >= len(tokens):
                return []

            options: list[tuple[int, str]] = []
            for next_position in range(len(tokens), position, -1):
                if next_position < len(tokens) and not starts_l1(next_position):
                    continue
                raw_l3 = ", ".join(tokens[position:next_position])
                options.append((next_position, raw_l3))
            return options

        @lru_cache(maxsize=None)
        def parse_from(position: int) -> tuple[ParsedPath, ...] | None:
            if position == len(tokens):
                return ()

            for l1_parts, topic_l1 in self._matching_candidates(
                tokens,
                position,
                self.l1_candidates,
            ):
                after_l1 = position + len(l1_parts)
                path_options: list[tuple[int, ParsedPath]] = []

                for l2_parts, topic_l2 in self._matching_candidates(
                    tokens,
                    after_l1,
                    self.l2_by_l1[topic_l1],
                ):
                    after_l2 = after_l1 + len(l2_parts)

                    for l3_parts, topic_l3 in self._matching_candidates(
                        tokens,
                        after_l2,
                        self.l3_by_pair[(topic_l1, topic_l2)],
                    ):
                        path_options.append(
                            (
                                after_l2 + len(l3_parts),
                                ParsedPath(topic_l1, topic_l2, topic_l3),
                            )
                        )

                    path_options.append((after_l2, ParsedPath(topic_l1, topic_l2, None)))

                    if allow_unknown_l3:
                        for next_position, raw_l3 in unknown_l3_options(after_l2):
                            path_options.append(
                                (
                                    next_position,
                                    ParsedPath(topic_l1, topic_l2, raw_l3, True),
                                )
                            )

                path_options.append((after_l1, ParsedPath(topic_l1, None, None)))

                path_options.sort(
                    key=lambda item: (
                        item[1].used_fallback,
                        -item[0],
                        item[1].topic_l1,
                        item[1].topic_l2 or "",
                        item[1].topic_l3 or "",
                    )
                )
                for next_position, parsed_path in path_options:
                    remainder = parse_from(next_position)
                    if remainder is not None:
                        return (parsed_path,) + remainder

            return None

        return parse_from(0)

    def parse(self, raw_tags: str) -> tuple[ParsedPath, ...]:
        if not raw_tags or not raw_tags.strip():
            return ()

        tokens = tuple(normalize(part) for part in raw_tags.split(",") if normalize(part))

        parsed = self._parse_tokens(tokens, allow_unknown_l3=False)
        if parsed is not None:
            return parsed

        parsed = self._parse_tokens(tokens, allow_unknown_l3=True)
        if parsed is not None:
            return parsed

        raise ValueError(f"Could not parse taxonomy sequence: {raw_tags}")


def load_filtered_rows(
    input_path: Path,
    year: int,
    sc_flag: str,
) -> list[dict[str, str]]:
    filtered_rows: list[dict[str, str]] = []
    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date_value = str(row.get("Date", ""))
            if not date_value.startswith(f"{year}-"):
                continue
            if str(row.get("sc_flag", "")) != sc_flag:
                continue
            filtered_rows.append(row)
    return filtered_rows


def build_summary_rows(
    resolutions_to_paths: dict[str, tuple[ParsedPath, ...]],
    denominator: int,
    level_name: str,
    pct_column_name: str,
) -> list[dict[str, str | int]]:
    tag_to_resolutions: dict[str, set[str]] = defaultdict(set)

    for resolution, paths in resolutions_to_paths.items():
        unique_tags = {
            getattr(parsed_path, level_name)
            for parsed_path in paths
            if getattr(parsed_path, level_name)
        }
        for tag in unique_tags:
            tag_to_resolutions[tag].add(resolution)

    summary_rows: list[dict[str, str | int]] = []
    for tag, resolutions in sorted(
        tag_to_resolutions.items(),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        resolution_count = len(resolutions)
        summary_rows.append(
            {
                level_name: tag,
                "resolution_count": resolution_count,
                pct_column_name: f"{(resolution_count / denominator) * 100:.2f}",
            }
        )

    return summary_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 2025 GA thematic summaries from comma-compressed taxonomy tags.",
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--denominator", type=int, default=DEFAULT_DENOMINATOR)
    parser.add_argument("--sc-flag", default=DEFAULT_SC_FLAG)
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    filtered_rows = load_filtered_rows(args.input, args.year, args.sc_flag)
    if len(filtered_rows) != args.denominator:
        raise ValueError(
            f"Expected {args.denominator} rows for {args.year} with sc_flag={args.sc_flag}, "
            f"found {len(filtered_rows)}"
        )

    taxonomy_parser = TaxonomyParser()
    resolutions_to_paths: dict[str, tuple[ParsedPath, ...]] = {}
    parsed_path_rows: list[dict[str, object]] = []
    fallback_rows: list[tuple[str, str]] = []
    empty_tag_count = 0

    for row in filtered_rows:
        resolution = row["Resolution"]
        raw_tags = row.get("tags", "") or ""
        parsed_paths = taxonomy_parser.parse(raw_tags)
        resolutions_to_paths[resolution] = parsed_paths

        if not parsed_paths:
            empty_tag_count += 1
            parsed_path_rows.append(
                {
                    "resolution": resolution,
                    "date": row.get("Date", ""),
                    "title": row.get("Title", ""),
                    "path_index": 0,
                    "topic_l1": "",
                    "topic_l2": "",
                    "topic_l3": "",
                    "used_fallback": "False",
                    "raw_tags": raw_tags,
                }
            )
            continue

        for path_index, parsed_path in enumerate(parsed_paths, start=1):
            if parsed_path.used_fallback:
                fallback_rows.append((resolution, parsed_path.topic_l3 or ""))

            parsed_path_rows.append(
                {
                    "resolution": resolution,
                    "date": row.get("Date", ""),
                    "title": row.get("Title", ""),
                    "path_index": path_index,
                    "topic_l1": parsed_path.topic_l1,
                    "topic_l2": parsed_path.topic_l2 or "",
                    "topic_l3": parsed_path.topic_l3 or "",
                    "used_fallback": str(parsed_path.used_fallback),
                    "raw_tags": raw_tags,
                }
            )

    parsed_output = output_dir / f"ga_{args.year}_topic_paths.csv"
    l1_output = output_dir / f"ga_{args.year}_topic_l1_summary.csv"
    l2_output = output_dir / f"ga_{args.year}_topic_l2_summary.csv"
    l3_output = output_dir / f"ga_{args.year}_topic_l3_summary.csv"
    pct_column_name = f"pct_of_{args.denominator}"

    write_csv(
        parsed_output,
        [
            "resolution",
            "date",
            "title",
            "path_index",
            "topic_l1",
            "topic_l2",
            "topic_l3",
            "used_fallback",
            "raw_tags",
        ],
        parsed_path_rows,
    )
    write_csv(
        l1_output,
        ["topic_l1", "resolution_count", pct_column_name],
        build_summary_rows(
            resolutions_to_paths,
            args.denominator,
            "topic_l1",
            pct_column_name,
        ),
    )
    write_csv(
        l2_output,
        ["topic_l2", "resolution_count", pct_column_name],
        build_summary_rows(
            resolutions_to_paths,
            args.denominator,
            "topic_l2",
            pct_column_name,
        ),
    )
    write_csv(
        l3_output,
        ["topic_l3", "resolution_count", pct_column_name],
        build_summary_rows(
            resolutions_to_paths,
            args.denominator,
            "topic_l3",
            pct_column_name,
        ),
    )

    print(f"Filtered rows: {len(filtered_rows)}")
    print(f"Empty tag rows: {empty_tag_count}")
    print(f"Fallback L3 matches: {len(fallback_rows)}")
    if fallback_rows:
        print("Fallback details:")
        for resolution, topic_l3 in fallback_rows:
            print(f"  {resolution}: {topic_l3}")
    print(f"Wrote {parsed_output}")
    print(f"Wrote {l1_output}")
    print(f"Wrote {l2_output}")
    print(f"Wrote {l3_output}")


if __name__ == "__main__":
    main()
