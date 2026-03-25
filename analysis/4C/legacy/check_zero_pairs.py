"""Quick check: how many zero-sim pairs in 2025, and which countries are affected?"""
import os, json, urllib.request, urllib.parse, ssl
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

def q(table, select="*", params=None, limit=50000):
    ctx = ssl.create_default_context()
    url = f"{URL}/rest/v1/{table}?select={urllib.parse.quote(select)}"
    if params:
        for k, v in params.items():
            url += f"&{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}"
    rows, offset = [], 0
    while True:
        pu = url + f"&limit=1000&offset={offset}"
        req = urllib.request.Request(pu, headers={
            "apikey": KEY, "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=ctx) as r:
            d = json.loads(r.read().decode())
            if not d: break
            rows.extend(d)
            if len(d) < 1000: break
            offset += 1000
            if len(rows) >= limit: break
    return rows

# Zero-similarity pairs in 2025
pw_zero = q("pairwise_similarity_yearly",
            select="Country1_ISO3,Country2_ISO3",
            params={"Year": "eq.2025", "CosineSimilarity": "eq.0"})
print(f"Stored pairs with sim=0.0 in 2025: {len(pw_zero)}")

afg_ven = [r for r in pw_zero
           if r["Country1_ISO3"] in ("AFG", "VEN") or r["Country2_ISO3"] in ("AFG", "VEN")]
print(f"  Involving AFG/VEN: {len(afg_ven)}")
others = [r for r in pw_zero
          if r["Country1_ISO3"] not in ("AFG", "VEN") and r["Country2_ISO3"] not in ("AFG", "VEN")]
print(f"  Other zero pairs: {len(others)}")

# Which countries appear in these non-AFG/VEN zeros?
c = Counter()
for r in others:
    c[r["Country1_ISO3"]] += 1
    c[r["Country2_ISO3"]] += 1

print(f"\nCountries most frequently in spurious zero pairs:")
for iso, cnt in c.most_common(20):
    ann = q("annual_scores", select="Total Votes in Year",
            params={"Country name": f"eq.{iso}", "Year": "eq.2025"})
    total = ann[0]["Total Votes in Year"] if ann else "N/A"
    print(f"  {iso}: {cnt} zero-sim pairs, Total Votes={total}")
