#!/usr/bin/env python3
"""
Cross-check UNGA 2025 resolutions CSV against official UN press release data.

Sources:
  - GA/12693 (30 June 2025): https://press.un.org/en/2025/ga12693.doc.htm
  - GA/12686 (3 June 2025):  https://press.un.org/en/2025/ga12686.doc.htm
"""

import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "analysis" / "unga_2025_resolutions.csv"


def separator(title):
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}\n")


def load_csv():
    with open(CSV_PATH) as f:
        rows = list(csv.reader(f))
    header1 = rows[0]
    country_iso3 = header1[9:]
    data = {}
    for r in rows[2:]:
        data[r[0]] = r
    return data, country_iso3


def check_resolution(data, country_iso3, res_id, label, exp_y, exp_n, exp_a, named_votes):
    """Check one resolution's tallies and named country votes. Returns True if all OK."""
    ok = True
    r = data.get(res_id)
    if not r:
        print(f"  ❌ {res_id}: NOT FOUND in our CSV")
        return False

    csv_y = int(r[5])
    csv_n = int(r[6])
    csv_a = int(r[7])

    y_ok = csv_y == exp_y
    n_ok = csv_n == exp_n
    a_ok = csv_a == exp_a

    if y_ok and n_ok and a_ok:
        print(f"  ✓ {res_id} ({label})")
        print(f"    Tallies: Y={csv_y} N={csv_n} A={csv_a} — matches UN press release")
    else:
        print(f"  ❌ {res_id} ({label}) — TALLY MISMATCH")
        print(f"    CSV: Y={csv_y} N={csv_n} A={csv_a}")
        print(f"    UN:  Y={exp_y} N={exp_n} A={exp_a}")
        ok = False

    # Check named country votes
    for vote_type, countries in named_votes.items():
        for iso in countries:
            try:
                idx = 9 + country_iso3.index(iso)
            except ValueError:
                print(f"    ❌ {iso}: not found in country columns")
                ok = False
                continue
            actual = r[idx]
            if actual != vote_type:
                print(f"    ❌ {iso} should be {vote_type}, got \"{actual}\"")
                ok = False
            else:
                print(f"    ✓ {iso} = {vote_type} (confirmed)")

    return ok


def main():
    data, country_iso3 = load_csv()
    all_ok = True

    # ── Source 1: GA/12693 — 30 June 2025 ──────────────────────
    separator("Source 1: UN Press Release GA/12693 (30 June 2025)")
    print("  URL: https://press.un.org/en/2025/ga12693.doc.htm\n")

    checks_ga12693 = [
        ("A/RES/79/313", "Tackling illicit trafficking in wildlife",
         157, 1, 0,
         {"NO": ["USA"]}),

        ("A/RES/79/316", "Promoting interreligious dialogue / hate speech",
         111, 1, 44,
         {"NO": ["USA"]}),

        ("A/RES/79/315", "The Wiphala",
         139, 2, 5,
         {"NO": ["USA", "ISR"],
          "ABSTAIN": ["CAN", "GEO", "PRY", "PER", "TUR"]}),

        ("A/RES/79/314", "Our Ocean, Our Future, Our Responsibility",
         162, 1, 0,
         {"NO": ["USA"]}),

        ("A/RES/79/308", "UNIFIL financing",
         147, 3, 1,
         {"NO": ["ARG", "ISR", "USA"],
          "ABSTAIN": ["PRY"]}),
    ]

    for args in checks_ga12693:
        result = check_resolution(data, country_iso3, *args)
        if not result:
            all_ok = False
        print()

    # ── Source 2: GA/12686 — 3 June 2025 ───────────────────────
    separator("Source 2: UN Press Release GA/12686 (3 June 2025)")
    print("  URL: https://press.un.org/en/2025/ga12686.doc.htm\n")

    # From the press release:
    #  - World Horse Day (A/79/L.89): 169-1(USA)-0
    #  - Georgia IDPs (A/79/L.90): 107-9(BLR,CUB,PRK,GNQ,MLI,NIC,RUS,SDN,ZWE)-49

    checks_ga12686 = [
        ("A/RES/79/291", "World Horse Day",
         169, 1, 0,
         {"NO": ["USA"]}),

        ("A/RES/79/292", "Status of IDPs/refugees from Abkhazia, Georgia",
         107, 9, 49,
         {"NO": ["BLR", "CUB", "PRK", "GNQ", "MLI", "NIC", "RUS", "SDN", "ZWE"]}),
    ]

    for args in checks_ga12686:
        result = check_resolution(data, country_iso3, *args)
        if not result:
            all_ok = False
        print()

    # ── Summary ────────────────────────────────────────────────
    separator("ONLINE CROSS-CHECK SUMMARY")
    total_checked = len(checks_ga12693) + len(checks_ga12686)
    if all_ok:
        print(f"  ✓ ALL {total_checked} resolutions verified against official UN sources")
        print(f"  ✓ All aggregate tallies (YES/NO/ABSTAIN) match exactly")
        print(f"  ✓ All named country-level votes confirmed")
    else:
        print(f"  ⚠️  Some cross-checks failed — review above for details")
    print()


if __name__ == "__main__":
    main()
