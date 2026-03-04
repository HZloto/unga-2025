"""Split topic votes for USA and CPV by UNBIS Thesaurus hierarchy level.
Produces 3 CSVs: main category, subcategory, and specific item."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent

tv = pd.read_csv(DATA / "topic_votes_yearly (2).csv")

# ── UNBIS Thesaurus hierarchy classification ──
# Level 1: Main Categories (broadest top-level UNBIS headings)
# Level 2: Subcategories (mid-level groupings)
# Level 3: Specific Items (most granular terms)

HIERARCHY = {
    # ── MAIN CATEGORIES (Level 1) ──
    'POLITICAL AND LEGAL QUESTIONS': 1,
    'DISARMAMENT AND MILITARY QUESTIONS': 1,
    'HUMAN RIGHTS': 1,
    'SOCIAL DEVELOPMENT': 1,
    'ENVIRONMENT': 1,
    'INTERNATIONAL LAW': 1,
    'ECONOMIC CONDITIONS': 1,
    'DEVELOPMENT': 1,
    'INTERNATIONAL RELATIONS': 1,

    # ── SUBCATEGORIES (Level 2) ──
    'MAINTENANCE OF PEACE AND SECURITY': 2,
    'POLITICAL EVENTS AND ISSUES': 2,
    'DISCRIMINATION': 2,
    'DEVELOPMENT FINANCE': 2,
    'WELFARE AND SOCIAL SERVICES': 2,
    'PROTECTION OF AND ASSISTANCE TO REFUGEES AND DISPLACED PERSONS': 2,
    'MARINE RESOURCES': 2,
    'NATURAL RESOURCES AND THE ENVIRONMENT': 2,
    'WOMEN\'S ADVANCEMENT': 2,
    'HUMANITARIAN AID AND RELIEF': 2,
    'FOOD AND NUTRITION': 2,
    'CULTURAL DEVELOPMENT': 2,
    'EDUCATIONAL POLICY AND PLANNING': 2,
    'PUBLIC FINANCE': 2,
    'GENERAL INTERNATIONAL TRADE AND TRADE POLICY': 2,
    'ENERGY RESOURCES': 2,
    'NUCLEAR SCIENCE': 2,
    'SPACE SCIENCES': 2,
    'SCIENCE AND TECHNOLOGY': 2,
    'DISEASE PREVENTION AND CONTROL': 2,
    'COMPREHENSIVE HEALTH SERVICES': 2,
    'DEVELOPMENT AND TRANSFER OF TECHNOLOGY AND PROMOTION OF SCIENCE': 2,
    'GENERAL AND NATIONAL LAW': 2,
    'COMPUTER SCIENCE AND TECHNOLOGY': 2,
    'COMMUNICATION AND MASS MEDIA': 2,
    'RESOURCES (GENERAL)': 2,

    # ── SPECIFIC ITEMS (Level 3) ──
    'WILDLIFE': 3,
    'POLLUTION': 3,
    'BANKING AND INVESTMENT': 3,
    'TELECOMMUNICATIONS': 3,
    'TRADE IN COMMODITIES': 3,
    'COMMODITIES': 3,
    'SKILLS DEVELOPMENT': 3,
    'TAXATION': 3,
    'STATISTICS': 3,
    'TRANSPORT POLICY AND PLANNING': 3,
    'WATER': 3,
    'SPECIAL GROUPS': 3,
    'SPECIAL CATEGORIES OF WORKERS': 3,
    'LAW OF THE SEA': 3,
    'LAND FORMS AND ECOSYSTEMS': 3,
    'PUBLIC ADMINISTRATION': 3,
    'EDUCATIONAL SYSTEMS': 3,
    'PERSONS WITH DISABILITIES': 3,
    'NON-FORMAL EDUCATION': 3,
    'MONETARY ISSUES': 3,
    'DISEASES AND CARRIERS OF DISEASES': 3,
    'LANGUAGE': 3,
    'CULTURE': 3,
    'PHILOSOPHY AND RELIGION': 3,
    'TRADE RELATED FINANCE': 3,
    'ENVIRONMENTAL HEALTH': 3,
    'RECOMMENDATIONS': 3,
    'INTERNATIONAL TRADE': 3,
    'No Tag': 3,
}

LEVEL_NAMES = {1: 'main_category', 2: 'subcategory', 3: 'specific_item'}

# Check for unclassified tags
all_tags_2025 = tv[tv['Year'] == 2025]['TopicTag'].unique()
unclassified = [t for t in all_tags_2025 if t not in HIERARCHY]
if unclassified:
    print(f"⚠️ Unclassified tags: {unclassified}")

for iso, name in [('USA', 'United States'), ('CPV', 'Cabo Verde')]:
    ct = tv[(tv['Year'] == 2025) & (tv['Country'] == iso)].copy()
    ct['Level'] = ct['TopicTag'].map(HIERARCHY)
    ct['Yes%'] = (ct['YesVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)
    ct['No%'] = (ct['NoVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)
    ct['Abstain%'] = (ct['AbstainVotes_Topic'] / ct['TotalVotes_Topic'] * 100).round(1)

    for level, level_name in LEVEL_NAMES.items():
        subset = ct[ct['Level'] == level].sort_values('TotalVotes_Topic', ascending=False)
        out_df = subset[['TopicTag', 'YesVotes_Topic', 'NoVotes_Topic',
                         'AbstainVotes_Topic', 'TotalVotes_Topic',
                         'Yes%', 'No%', 'Abstain%']].copy()
        out_df.columns = ['Topic', 'Yes', 'No', 'Abstain', 'Total', 'Yes%', 'No%', 'Abstain%']

        fname = f'topic_votes_2025_{iso}_{level_name}.csv'
        out_df.to_csv(OUT / fname, index=False)
        print(f"✓ {fname}: {len(out_df)} topics")

    print()

# ── Summary table ──
print("=" * 70)
print("Summary: Topic counts by level")
print("=" * 70)
for level, level_name in LEVEL_NAMES.items():
    tags_at_level = [t for t, lv in HIERARCHY.items() if lv == level]
    print(f"  Level {level} ({level_name}): {len(tags_at_level)} tags")

print()
print("=" * 70)
print("USA — Main Categories (Level 1)")
print("=" * 70)
usa = tv[(tv['Year'] == 2025) & (tv['Country'] == 'USA')].copy()
usa['Level'] = usa['TopicTag'].map(HIERARCHY)
usa['Yes%'] = (usa['YesVotes_Topic'] / usa['TotalVotes_Topic'] * 100).round(1)
main = usa[usa['Level'] == 1].sort_values('TotalVotes_Topic', ascending=False)
print(main[['TopicTag', 'YesVotes_Topic', 'NoVotes_Topic', 'AbstainVotes_Topic',
            'TotalVotes_Topic', 'Yes%']].to_string(index=False))

print()
print("=" * 70)
print("CPV — Main Categories (Level 1)")
print("=" * 70)
cpv = tv[(tv['Year'] == 2025) & (tv['Country'] == 'CPV')].copy()
cpv['Level'] = cpv['TopicTag'].map(HIERARCHY)
cpv['Yes%'] = (cpv['YesVotes_Topic'] / cpv['TotalVotes_Topic'] * 100).round(1)
main_cpv = cpv[cpv['Level'] == 1].sort_values('TotalVotes_Topic', ascending=False)
print(main_cpv[['TopicTag', 'YesVotes_Topic', 'NoVotes_Topic', 'AbstainVotes_Topic',
                'TotalVotes_Topic', 'Yes%']].to_string(index=False))
