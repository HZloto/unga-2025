"""Topic votes grouped into custom thematic clusters — a middle ground
between the 9 broad UNBIS main categories and the 26+ subcategories.

Produces 2 CSVs (USA, CPV) + 1 side-by-side comparison."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent

tv = pd.read_csv(DATA / "topic_votes_yearly (2).csv")

# ── Custom thematic groupings ──
# Each tag from the 64 in the dataset is mapped to exactly one thematic group.
# Groups are designed to have meaningful volume while being specific enough
# to tell a story (target: 10-40 votes per group).

THEMATIC = {
    # ── Peace & Security ──
    'MAINTENANCE OF PEACE AND SECURITY':    'Peace & Security',
    'POLITICAL EVENTS AND ISSUES':          'Peace & Security',

    # ── Disarmament & Arms Control ──
    'DISARMAMENT AND MILITARY QUESTIONS':   'Disarmament & Arms Control',
    'NUCLEAR SCIENCE':                      'Disarmament & Arms Control',
    'SPACE SCIENCES':                       'Disarmament & Arms Control',

    # ── Human Rights & Equality ──
    'HUMAN RIGHTS':                         'Human Rights & Equality',
    'DISCRIMINATION':                       'Human Rights & Equality',
    'WOMEN\'S ADVANCEMENT':                 'Human Rights & Equality',
    'PERSONS WITH DISABILITIES':            'Human Rights & Equality',
    'SPECIAL GROUPS':                       'Human Rights & Equality',

    # ── Refugees & Humanitarian Aid ──
    'PROTECTION OF AND ASSISTANCE TO REFUGEES AND DISPLACED PERSONS':
                                            'Refugees & Humanitarian Aid',
    'HUMANITARIAN AID AND RELIEF':          'Refugees & Humanitarian Aid',

    # ── International Law & Governance ──
    'INTERNATIONAL LAW':                    'International Law & Governance',
    'LAW OF THE SEA':                       'International Law & Governance',
    'GENERAL AND NATIONAL LAW':             'International Law & Governance',
    'RECOMMENDATIONS':                      'International Law & Governance',
    'PUBLIC ADMINISTRATION':                'International Law & Governance',

    # ── Environment & Climate ──
    'ENVIRONMENT':                          'Environment & Climate',
    'POLLUTION':                            'Environment & Climate',
    'WILDLIFE':                             'Environment & Climate',
    'NATURAL RESOURCES AND THE ENVIRONMENT':'Environment & Climate',
    'ENVIRONMENTAL HEALTH':                 'Environment & Climate',
    'LAND FORMS AND ECOSYSTEMS':            'Environment & Climate',
    'MARINE RESOURCES':                     'Environment & Climate',
    'WATER':                                'Environment & Climate',

    # ── Economic Development & Finance ──
    'DEVELOPMENT':                          'Economic Development & Finance',
    'DEVELOPMENT FINANCE':                  'Economic Development & Finance',
    'ECONOMIC CONDITIONS':                  'Economic Development & Finance',
    'PUBLIC FINANCE':                       'Economic Development & Finance',
    'MONETARY ISSUES':                      'Economic Development & Finance',
    'BANKING AND INVESTMENT':               'Economic Development & Finance',
    'RESOURCES (GENERAL)':                  'Economic Development & Finance',
    'TRADE RELATED FINANCE':                'Economic Development & Finance',
    'TAXATION':                             'Economic Development & Finance',

    # ── Trade & Commodities ──
    'GENERAL INTERNATIONAL TRADE AND TRADE POLICY': 'Trade & Commodities',
    'TRADE IN COMMODITIES':                 'Trade & Commodities',
    'INTERNATIONAL TRADE':                  'Trade & Commodities',
    'COMMODITIES':                          'Trade & Commodities',

    # ── Social Welfare & Labor ──
    'SOCIAL DEVELOPMENT':                   'Social Welfare & Labor',
    'WELFARE AND SOCIAL SERVICES':          'Social Welfare & Labor',
    'SPECIAL CATEGORIES OF WORKERS':        'Social Welfare & Labor',
    'SKILLS DEVELOPMENT':                   'Social Welfare & Labor',

    # ── Health & Nutrition ──
    'DISEASE PREVENTION AND CONTROL':       'Health & Nutrition',
    'COMPREHENSIVE HEALTH SERVICES':        'Health & Nutrition',
    'DISEASES AND CARRIERS OF DISEASES':    'Health & Nutrition',
    'FOOD AND NUTRITION':                   'Health & Nutrition',

    # ── Education, Culture & Communication ──
    'EDUCATIONAL POLICY AND PLANNING':      'Education, Culture & Communication',
    'CULTURAL DEVELOPMENT':                 'Education, Culture & Communication',
    'CULTURE':                              'Education, Culture & Communication',
    'EDUCATIONAL SYSTEMS':                  'Education, Culture & Communication',
    'NON-FORMAL EDUCATION':                 'Education, Culture & Communication',
    'LANGUAGE':                             'Education, Culture & Communication',
    'PHILOSOPHY AND RELIGION':              'Education, Culture & Communication',
    'COMMUNICATION AND MASS MEDIA':         'Education, Culture & Communication',

    # ── Science, Technology & Energy ──
    'DEVELOPMENT AND TRANSFER OF TECHNOLOGY AND PROMOTION OF SCIENCE':
                                            'Science, Technology & Energy',
    'COMPUTER SCIENCE AND TECHNOLOGY':      'Science, Technology & Energy',
    'TELECOMMUNICATIONS':                   'Science, Technology & Energy',
    'SCIENCE AND TECHNOLOGY':               'Science, Technology & Energy',
    'ENERGY RESOURCES':                     'Science, Technology & Energy',
    'TRANSPORT POLICY AND PLANNING':        'Science, Technology & Energy',
    'STATISTICS':                           'Science, Technology & Energy',

    # ── Broad Political & Legal (catch-all main categories) ──
    'POLITICAL AND LEGAL QUESTIONS':        'Political & Legal (General)',
    'INTERNATIONAL RELATIONS':              'Political & Legal (General)',

    # ── No Tag ──
    'No Tag':                               'Untagged',
}

# ── Group order for display ──
GROUP_ORDER = [
    'Peace & Security',
    'Disarmament & Arms Control',
    'Human Rights & Equality',
    'Refugees & Humanitarian Aid',
    'International Law & Governance',
    'Environment & Climate',
    'Economic Development & Finance',
    'Trade & Commodities',
    'Social Welfare & Labor',
    'Health & Nutrition',
    'Education, Culture & Communication',
    'Science, Technology & Energy',
    'Political & Legal (General)',
    'Untagged',
]


def build_thematic(df, country, year=2025):
    """Aggregate topic votes into thematic groups for one country-year."""
    c = df[(df['Year'] == year) & (df['Country'] == country)].copy()
    c['ThematicGroup'] = c['TopicTag'].map(THEMATIC)

    unmapped = c[c['ThematicGroup'].isna()]['TopicTag'].unique()
    if len(unmapped):
        print(f"  ⚠️  Unmapped tags for {country}: {list(unmapped)}")

    agg = (c.groupby('ThematicGroup')
            .agg(YesVotes=('YesVotes_Topic', 'sum'),
                 NoVotes=('NoVotes_Topic', 'sum'),
                 AbstainVotes=('AbstainVotes_Topic', 'sum'),
                 TotalVotes=('TotalVotes_Topic', 'sum'),
                 Tags=('TopicTag', 'count'))
            .reset_index())

    agg['Yes_Pct'] = (agg['YesVotes'] / agg['TotalVotes'] * 100).round(1)
    agg['No_Pct'] = (agg['NoVotes'] / agg['TotalVotes'] * 100).round(1)
    agg['Abstain_Pct'] = (agg['AbstainVotes'] / agg['TotalVotes'] * 100).round(1)

    # Order by defined group order
    agg['ThematicGroup'] = pd.Categorical(agg['ThematicGroup'],
                                           categories=GROUP_ORDER,
                                           ordered=True)
    agg = agg.sort_values('ThematicGroup').reset_index(drop=True)
    return agg


# ── Build for USA and CPV ──
print("=" * 70)
print("THEMATIC TOPIC GROUPS — USA & CPV — 2025")
print("=" * 70)

for iso in ['USA', 'CPV']:
    agg = build_thematic(tv, iso)
    fname = f'topic_votes_2025_{iso}_thematic.csv'
    agg.to_csv(OUT / fname, index=False)
    print(f"\n{'─' * 60}")
    print(f"  {iso}  ({len(agg)} thematic groups, {agg['Tags'].sum()} underlying tags)")
    print(f"{'─' * 60}")
    for _, r in agg.iterrows():
        print(f"  {r['ThematicGroup']:<40s}  "
              f"Yes {r['Yes_Pct']:5.1f}%  No {r['No_Pct']:5.1f}%  "
              f"Abs {r['Abstain_Pct']:5.1f}%  "
              f"({r['TotalVotes']:3d} votes, {r['Tags']} tags)")

# ── Side-by-side comparison ──
usa = build_thematic(tv, 'USA').rename(columns=lambda c: f'USA_{c}' if c != 'ThematicGroup' else c)
cpv = build_thematic(tv, 'CPV').rename(columns=lambda c: f'CPV_{c}' if c != 'ThematicGroup' else c)
comp = usa.merge(cpv, on='ThematicGroup', how='outer')
comp['Yes_Pct_Gap'] = (comp['USA_Yes_Pct'] - comp['CPV_Yes_Pct']).round(1)
comp.to_csv(OUT / 'topic_votes_2025_USA_vs_CPV_thematic.csv', index=False)

print(f"\n{'─' * 60}")
print("  USA vs CPV — Yes% Gap (USA minus CPV)")
print(f"{'─' * 60}")
for _, r in comp.iterrows():
    print(f"  {r['ThematicGroup']:<40s}  "
          f"USA {r['USA_Yes_Pct']:5.1f}%  CPV {r['CPV_Yes_Pct']:5.1f}%  "
          f"Gap {r['Yes_Pct_Gap']:+6.1f}pp")

print(f"\nSaved: topic_votes_2025_USA_thematic.csv")
print(f"       topic_votes_2025_CPV_thematic.csv")
print(f"       topic_votes_2025_USA_vs_CPV_thematic.csv")
