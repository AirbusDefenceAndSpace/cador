def img2latlon(x, y, offset_lat, offset_lon, step_lat, step_lon):
    """
    Convert img coords to latlon
    return lat, lon
    """
    return offset_lat + y * step_lat, offset_lon + x * step_lon


def img_geometry_to_latlon_geometry(geometry, offset_lat, offset_lon, step_lat, step_lon):
    """
    Convert an img geojson to a lat lon geojson
    """
    for i in geometry['coordinates'][0]:
        i[1], i[0] = img2latlon(i[0], i[1], offset_lat, offset_lon, step_lat, step_lon)
    return geometry
