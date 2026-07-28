import json

with open("osm_data/edinburgh_tags_raw.json") as f:
    stats = json.load(f)
key_counts = stats["key_counts"]

# filter out least common keys
common_keys = {key: value for key, value in key_counts.items() if value >= 10}  # arbitrary minimum count
print(f"Total keys: {len(key_counts)}, keys above count threshold: {len(common_keys)}")

