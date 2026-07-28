"""
OSM data has thousands of possible tags. This is a simple programme to count which ones are most 
prevalent in the Edinburgh extract.

I doubt relations will be particularly useful to my use-case but included for completeness.
"""

import osmium
import json
from collections import Counter

key_counts = Counter()  # counts instances of each key
tag_counts = Counter()  # counts instances of each key-value pair
element_counts = Counter()  # counts nodes, ways and relations

for object in osmium.FileProcessor("osm_data/edinburgh.osm.pbf"):
    element_counts[object.type_str()] += 1  # type_str() can be n (node), w (way), r (relation) or a (area) (or technically c (changeset), but this is metadata stuff)
    for tag in object.tags:
        key_counts[tag.k] += 1
        tag_counts[f"{tag.k}={tag.v}"] += 1

output = {
    "element_counts": dict(element_counts),
    "distinct_keys": len(key_counts),
    "key_counts": dict(key_counts.most_common()),  # sort by frequency
    "top_key_value_pairs": dict(tag_counts.most_common(200))
}

with open("osm_data/edinburgh_tags.json", "w") as f:
    f.write(output)