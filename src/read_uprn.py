import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from shapely.geometry import box


def crop_geodataframe(gdf):
    gdf = gdf.to_crs("EPSG:4326")
    lat, lon = (52.612961, -0.713225)
    lat_offset = 0.1  # Roughly 5km offset; adjust based on location if needed
    lon_offset = 0.14  # Roughly 5km offset; adjust based on location if needed
    bbox = box(lon - lon_offset, lat - lat_offset, lon + lon_offset, lat + lat_offset)
    gdf = gdf[gdf.intersects(bbox)]
    return gdf


uprns_df = pd.read_csv(
    "../data/uprn/osopenuprn_202409.csv",
    usecols=["UPRN", "LATITUDE", "LONGITUDE"],
)
print("read uprns")

uprns = gpd.GeoDataFrame(
    uprns_df,
    geometry=gpd.points_from_xy(uprns_df["LONGITUDE"], uprns_df["LATITUDE"]),
    crs="EPSG:4326",
)
print("read points from xy")

uprns = crop_geodataframe(uprns)
print("cropped dataframe")
uprns = uprns[["UPRN", "LATITUDE", "LONGITUDE"]]

uprns.to_csv("../data/uprn/uprns_crop.csv", index=False)
