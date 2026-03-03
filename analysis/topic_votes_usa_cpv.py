"""Topic Voting Breakdown for USA and Cabo Verde in 2025.
Shows per-topic Yes/No/Abstain breakdown and Yes% for each country."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent

tv = pd.read_csv(DATA / "topic_votes_yearly (2).csv")

COUNTRIES = {'USA': 'United States', 'CPV': 'Cabo Verde'}

for iso, name in COUNTRIES.items():
    print("=" * 70)
    print(f"Topic Voting Breakdown — {name} ({iso}) — 2025")
    print("=" * 70)

    ct = tv[(tv['Year'] == 2025) & (tv['Country'] == iso)].copy()
    ct['Yes%'] = (ct['YesVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)
    ct['No%'] = (ct['NoVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)
    ct['Abstain%'] = (ct['AbstainVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)
    ct = ct.sort_values('TotalVotes_Topic', ascending=False)

    print(f"\n  Topics covered: {len(ct)}")
    print(f"  Total topic-votes: {ct['TotalVotes_Topic'].sum()} (multi-tagged, exceeds annual total)")
    print()

    display = ct[['TopicTag', 'YesVotes_Topic', 'NoVotes_Topic', 'AbstainVotes_Topic',
                   'TotalVotes_Topic', 'Yes%', 'No%', 'Abstain%']].copy()
    display.columns = ['Topic', 'Yes', 'No', 'Abstain', 'Total', 'Yes%', 'No%', 'Abstain%']
    print(display.to_string(index=False))
    print()

    # Save per-country CSV
    out_file = OUT / f'topic_votes_2025_{iso}.csv'
    display.to_csv(out_file, index=False)
    print(f"  ✓ Saved: {out_file}")
    print()

# ── Side-by-side comparison on shared topics ──
print("=" * 70)
print("Side-by-Side: USA vs Cabo Verde Yes% on Shared Topics (2025)")
print("=" * 70)

usa = tv[(tv['Year'] == 2025) & (tv['Country'] == 'USA')].set_index('TopicTag')
cpv = tv[(tv['Year'] == 2025) & (tv['Country'] == 'CPV')].set_index('TopicTag')

shared = sorted(set(usa.index) & set(cpv.index))
comp_rows = []
for topic in shared:
    usa_yes_pct = usa.loc[topic, 'YesVotes_Topic'] / usa.loc[topic, 'TotalVotes_Topic'] * 100
    cpv_yes_pct = cpv.loc[topic, 'YesVotes_Topic'] / cpv.loc[topic, 'TotalVotes_Topic'] * 100
    comp_rows.append({
        'Topic': topic,
        'USA_Yes%': round(usa_yes_pct, 1),
        'CPV_Yes%': round(cpv_yes_pct, 1),
        'Gap': round(cpv_yes_pct - usa_yes_pct, 1),
    })

comp = pd.DataFrame(comp_rows).sort_values('Gap', ascending=False)
print(f"\n  Shared topics: {len(comp)}")
print(comp.to_string(index=False))

comp.to_csv(OUT / 'topic_votes_2025_USA_vs_CPV.csv', index=False)
print(f"\n  ✓ Saved: {OUT / 'topic_votes_2025_USA_vs_CPV.csv'}")
