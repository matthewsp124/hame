-- define output projection to use, EPSG 3857 is the Mercator projection which is standard for tiled web maps
local srid = 3857

-- define prefix for table names
local prefix = 'edinburgh'

-- don't use OSM coastline data
local keep_coastlines = false

-- write multipolygons into database as multipolygons
local multi_geometry = true

-- initialise storage for defining SQL tables
local tables = {}