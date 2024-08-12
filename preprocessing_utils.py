import math

def TileLatLonBounds(z, size, tx, ty):
    "Returns bounds of the given tile in latitude/longitude using WGS84 datum"

    bounds = TileBounds(z, size, tx, ty)
    minLat, minLon = MetersToLatLon(z, size, bounds[0], bounds[1])
    maxLat, maxLon = MetersToLatLon(z, size, bounds[2], bounds[3])
        
    return (minLat, minLon, maxLat, maxLon)

def LatLonToMeters(z, size, lat, lon):
    "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:3857"

    mx = lon * 20037508.342789244 / 180.0
    #my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    my = math.log(math.tan((90 - lat) * math.pi / 360.0)) / (math.pi / 180.0)

    my = my * 20037508.342789244 / 180.0
    return mx, my

def MetersToTile(z, size, mx, my):
    "Returns tile for given mercator coordinates"
    
    px, py = MetersToPixels(z, size, mx, my)
    return PixelsToTile(z, size, px, py)

def TileBounds(z, size, tx, ty):
    "Returns bounds of the given tile in EPSG:3857 coordinates"

    minx, miny = PixelsToMeters(z, size, tx * 256, ty * 256)
    maxx, maxy = PixelsToMeters(z, size, (tx + 1) * 256, (ty + 1) * 256)
    return (minx, miny, maxx, maxy)

def PixelsToMeters(z, size, px, py):
    "Converts pixel coordinates in given zoom level of pyramid to EPSG:3857"

    res = Resolution(z, size)
    mx = px * res - 20037508.342789244
    my = py * res - 20037508.342789244
    return mx, my

def Resolution(z, size):
    "Resolution (meters/pixel) for given zoom level (measured at Equator)"

    initialResolution = 2 * math.pi * 6378137 / size
    #return initialResolution / (2**zoom)
    return 156543.03392804062 / (2**z)

def MetersToLatLon(z, size, mx, my):
    "Converts XY point from Spherical Mercator EPSG:3857 to lat/lon in WGS84 Datum"

    lon = (mx / 20037508.342789244) * 180.0
    lat = (my / 20037508.342789244) * 180.0

    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon

def MetersToPixels(z, size, mx, my):
    "Converts EPSG:3857 to pyramid pixel coordinates in given zoom level"

    res = Resolution(z, size)
    px = (mx + 20037508.342789244) / res
    py = (my + 20037508.342789244) / res
    return px, py

def PixelsToTile(z, size, px, py):
    "Returns a tile covering region in given pixel coordinates"

    tx = int(math.ceil(px / float(256)) - 1)
    ty = int(math.ceil(py / float(256)) - 1)
    return tx, ty
    