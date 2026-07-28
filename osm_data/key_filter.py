import json
import urllib.request

with open("osm_data/edinburgh_tags_raw.json") as f:
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
print(f"{len(kept_keys)} after removing {len(common_keys) - len(kept_keys)} discardable keys")