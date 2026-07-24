import osmium
import json

from collections import Counter

class TagCounter(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.key_counts = Counter()

    def _collect(self, obj):
        for tag in obj.tags:
            self.key_counts[tag.k] += 1

    def node(self, n): self._collect(n)
    def way(self, w): self._collect(w)
    def relation(self, r): self._collect(r)

handler = TagCounter()
handler.apply_file("osm_data/edinburgh.osm.pbf")

for key, count in handler.key_counts.most_common(20):
    print(f"{key}: {count}")