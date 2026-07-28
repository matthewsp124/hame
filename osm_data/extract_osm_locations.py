import osmium
import json

"""
Info I want:

- latitude
- longitude
- address
- keys

Keys:
amenity, shop, tourism, historic, leisure, surface, bridge, footway, foot, smoothness, crossing, sidewalk, sport, golf, wheelchair, railway=platform, barrier, public_transport, tactile_paving
?highway?, ?access?, ?bicycle?
considered railway=level_crossing, but there's only one in edinburgh

New plan: write a script to count tags in dataset rather than manually going through the full list

Don't care about relations
"""

target_categories = ['amenity', 'shop', 'tourism', 'historic', 'leisure']

