import json
import time
import urllib.request
from collections import defaultdict

with open("osm_data/data/edinburgh_tags_raw.json") as f:
    stats = json.load(f)
key_counts = stats["key_counts"]

# filter out least common keys
common_keys = {key: value for key, value in key_counts.items() if value >= 10}  # arbitrary minimum count
print(f"Total keys: {len(key_counts)}, keys above count threshold: {len(common_keys)}")

# filter out official "discardable keys" - credits to Claude for this bit
def taginfo_get(path):
    # access taginfo's API
    req = urllib.request.Request(f"https://taginfo.openstreetmap.org/api/4/{path}", headers={"User-Agent": "learning-project-tag-filter/1.0 (personal use)"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

discardable = taginfo_get("keys/discardable?page=1&rp=200")["data"]
# each entry looks like {"key": "source", ...} -- normalise to just the key names
discardable_names = {d["key"] for d in discardable}
kept_keys = {k: v for k, v in common_keys.items() if k not in discardable_names}
print(f"{len(kept_keys)} keys kept after removing {len(common_keys) - len(kept_keys)} discardable keys")

# group keys that have the same top-level prefix (eg addr:street and addr:postcode)
groups = defaultdict(dict)
for k, v in kept_keys.items():
    prefix = k.split(":")[0]
    groups[prefix][k] = v
print(f"collapsed into {len(groups)} prefix groups")

# get wiki description for each top-level prefix
descriptions = {}
top_level_keys = sorted(groups.keys(), key=lambda k: -sum(groups[k].values()))
for key in top_level_keys:
    try:
        data = taginfo_get(f"key/wiki_pages?key={key}")
        pages = data.get("data", [])
        en = next((p for p in pages if p.get("lang") == "en"), pages[0] if pages else None)
        descriptions[key] = en.get("description") if en else None
    except Exception as e:
        descriptions[key] = None
    time.sleep(0.1)  # be kind to the API

# write to file
output = []
for prefix, members in sorted(groups.items(), key=lambda item: -sum(item[1].values())):
    # prefix eg "addr:", member eg "addr:street"
    output.append({
        "prefix": prefix,
        "total_count": sum(members.values()),
        "description": descriptions.get(prefix),
        "keys": dict(sorted(members.items(), key=lambda kv: -kv[1])),
    })
with open("osm_data/data/key_data.json", "w") as f:
    json.dump(output, f, indent=2)