from shapely.geometry import box


def remove_invalid_geometries(gdf):
    # Check for invalid geometries in the GeoDataFrame
    invalid_geometries = gdf[~gdf.is_valid]

    # Print invalid geometries if any
    if not invalid_geometries.empty:
        print(f"Invalid geometries found: {len(invalid_geometries)}")
        # print(invalid_geometries)
    else:
        print("All geometries are valid.")

    gdf = gdf.drop(index=invalid_geometries.index)
    return gdf


def crop_geodataframe(gdf):
    gdf = gdf.to_crs("EPSG:4326")
    lat, lon = (52.612961, -0.713225)

    lat_offset = 0.1  # Roughly 5km offset; adjust based on location if needed
    lon_offset = 0.14  # Roughly 5km offset; adjust based on location if needed
    bbox = box(lon - lon_offset, lat - lat_offset, lon + lon_offset, lat + lat_offset)
    gdf = gdf[gdf.intersects(bbox)]
    return gdf
