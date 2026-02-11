"""
Coverage analysis: how many 2025 resolutions do the 3 aggregate files cover?
Compares annual_scores.csv, pairwise_similarity_yearly.csv, topic_votes_yearly.csv
against the full source (un_votes_2025_processed.csv).
"""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def separator(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

# Load all files
annual = pd.read_csv(DATA / "annual_scores.csv")
pairwise = pd.read_csv(DATA / "pairwise_similarity_yearly.csv")
topic = pd.read_csv(DATA / "topic_votes_yearly.csv")
source = pd.read_csv(DATA / "un_votes_2025_processed.csv")

# Filter to 2025
a25 = annual[annual["Year"] == 2025]
p25 = pairwise[pairwise["Year"] == 2025]
t25 = topic[topic["Year"] == 2025]
ga25 = source[source["Council"] == "General Assembly"]

country_cols = list(source.columns[16:])

# ── SOURCE FILE ──
separator("SOURCE FILE: un_votes_2025_processed.csv")
print(f"  Total rows: {len(source)} ({len(ga25)} GA + {len(source)-len(ga25)} SC)")
print(f"  GA resolutions: {ga25['Resolution'].nunique()}")
print(f"  GA date range: {ga25['Date'].min()} → {ga25['Date'].max()}")
print(f"  Country columns: {len(country_cols)}")

# ── ANNUAL SCORES ──
separator("1. annual_scores.csv (2025)")
print(f"  Countries: {len(a25)}")
total_votes = a25["Total Votes in Year"]
print(f"  Total Votes in Year: min={total_votes.min():.0f}, max={total_votes.max():.0f}, median={total_votes.median():.0f}")
max_country = a25.loc[total_votes.idxmax(), "Country name"]
max_votes = int(total_votes.max())
print(f"  Max-participating country: {max_country} with {max_votes} votes")
print(f"  → Covers approx {max_votes} resolutions")

# Vote arithmetic
a25c = a25.copy()
a25c["computed"] = a25c["Yes Votes"] + a25c["No Votes"] + a25c["Abstain Votes"]
mismatches = a25c[a25c["computed"] != a25c["Total Votes in Year"]]
print(f"  Vote arithmetic (Y+N+A=Total): {'✓ all pass' if len(mismatches)==0 else f'{len(mismatches)} mismatches'}")

# Country overlap
annual_countries = set(a25["Country name"])
source_countries = set(country_cols)
extra_annual = sorted(annual_countries - source_countries)
missing_annual = sorted(source_countries - annual_countries)
print(f"  Countries in annual but not source: {extra_annual if extra_annual else 'none'}")
print(f"  Countries in source but not annual: {missing_annual if missing_annual else 'none'}")

# ── PAIRWISE SIMILARITY ──
separator("2. pairwise_similarity_yearly.csv (2025)")
print(f"  Rows: {len(p25):,}")
p25_countries = set(p25["Country1_ISO3"]) | set(p25["Country2_ISO3"])
print(f"  Unique countries: {len(p25_countries)}")
print(f"  Similarity range: [{p25['CosineSimilarity'].min():.4f}, {p25['CosineSimilarity'].max():.4f}]")
zero_sim = (p25["CosineSimilarity"] == 0).sum()
print(f"  Zero-similarity rows: {zero_sim} ({zero_sim/len(p25)*100:.1f}%)")
extra_pw = sorted(p25_countries - source_countries)
print(f"  Countries in pairwise but not source: {extra_pw if extra_pw else 'none'}")

# ── TOPIC VOTES ──
separator("3. topic_votes_yearly.csv (2025)")
print(f"  Rows: {len(t25):,}")
t25_countries = set(t25["Country"])
t25_topics = sorted(t25["TopicTag"].unique())
print(f"  Unique countries: {len(t25_countries)}")
print(f"  Unique topics: {len(t25_topics)}")
extra_tv = sorted(t25_countries - source_countries)
print(f"  Countries in topic but not source: {extra_tv if extra_tv else 'none'}")

# ── COVERAGE COMPARISON ──
separator("RESOLUTION COVERAGE COMPARISON")
print(f"  Source file (GA):     192 resolutions (Feb 24 – Dec 18)")
print(f"  annual_scores max:    {max_votes} votes ({max_country})")
print(f"  → Missing:            {192 - max_votes} resolutions")
print(f"  Coverage ratio:       {max_votes}/192 = {max_votes/192*100:.1f}%")

# ── COUNTRY COMPARISON: annual vs topic vs source ──
separator("COUNTRY COMPARISON: annual vs topic vs full source")
for iso in ["AUS", "GBR", "FRA"]:
    tc = t25[t25["Country"] == iso]
    t_yes = int(tc["YesVotes_Topic"].sum())
    t_no = int(tc["NoVotes_Topic"].sum())
    t_abs = int(tc["AbstainVotes_Topic"].sum())

    ac = a25[a25["Country name"] == iso].iloc[0]
    a_yes = int(ac["Yes Votes"])
    a_no = int(ac["No Votes"])
    a_abs = int(ac["Abstain Votes"])
    a_total = int(ac["Total Votes in Year"])

    ga_col = ga25[iso]
    csv_yes = (ga_col == "YES").sum()
    csv_no = (ga_col == "NO").sum()
    csv_abs = (ga_col == "ABSTAIN").sum()
    csv_total = csv_yes + csv_no + csv_abs

    print(f"  {iso}:")
    print(f"    annual_scores:   Y={a_yes:>3d}  N={a_no:>3d}  A={a_abs:>3d}  T={a_total:>3d}")
    print(f"    topic_votes sum: Y={t_yes:>3d}  N={t_no:>3d}  A={t_abs:>3d}  (inflated by multi-tag)")
    print(f"    full source:     Y={csv_yes:>3d}  N={csv_no:>3d}  A={csv_abs:>3d}  T={csv_total:>3d}")
    print()

# ── CONSISTENCY CHECK ──
separator("CONSISTENCY: Do the 3 files agree on the same scrape window?")
consistent = 0
inconsistent_list = []
for iso in sorted(source_countries & annual_countries & t25_countries):
    ac = a25[a25["Country name"] == iso]
    if len(ac) == 0:
        continue
    ac = ac.iloc[0]
    tc = t25[t25["Country"] == iso]
    a_yes = int(ac["Yes Votes"])
    t_yes = int(tc["YesVotes_Topic"].sum())
    a_no = int(ac["No Votes"])
    t_no = int(tc["NoVotes_Topic"].sum())
    if t_yes >= a_yes and t_no >= a_no:
        consistent += 1
    else:
        inconsistent_list.append((iso, a_yes, a_no, t_yes, t_no))

if not inconsistent_list:
    print(f"  ✓ All {consistent} countries: topic_votes >= annual_scores (consistent scrape)")
else:
    for iso, ay, an, ty, tn in inconsistent_list[:5]:
        print(f"  ❌ {iso}: annual Y={ay} N={an} but topic Y={ty} N={tn}")
    print(f"  {consistent} consistent, {len(inconsistent_list)} inconsistent")

# ── ESTIMATE DATE CUTOFF ──
separator("ESTIMATED DATE CUTOFF OF THE 3 FILES")
ga_sorted = ga25.sort_values("Date").reset_index(drop=True)
cumulative = 0
cutoff_idx = None
for i, row in ga_sorted.iterrows():
    vote = row[max_country]
    if vote in ("YES", "NO", "ABSTAIN"):
        cumulative += 1
    if cumulative == max_votes:
        cutoff_idx = i
        print(f"  Cutoff at resolution #{i+1}: {row['Resolution']}")
        print(f"  Date: {row['Date']}")
        title = row["Title"]
        if len(title) > 80:
            title = title[:80] + "..."
        print(f"  Title: {title}")
        break

if cutoff_idx is not None:
    remaining = ga_sorted.iloc[cutoff_idx + 1 :]
    print(f"\n  Resolutions AFTER cutoff ({len(remaining)} missing from the 3 files):")
    print(f"  {'Resolution':<22s} {'Date':<12s} Title")
    print(f"  {'-'*22} {'-'*12} {'-'*50}")
    for _, row in remaining.iterrows():
        title = row["Title"]
        if len(title) > 65:
            title = title[:65] + "..."
        print(f"  {row['Resolution']:<22s} {row['Date']:<12s} {title}")
else:
    print("  ⚠️ Could not determine cutoff")

# ── TOPIC LIST ──
separator("TOPICS IN topic_votes_yearly.csv (2025)")
for i, t in enumerate(t25_topics, 1):
    count = len(t25[t25["TopicTag"] == t])
    print(f"  {i:>2d}. {t} ({count} country-rows)")

print("\n  Done.")
