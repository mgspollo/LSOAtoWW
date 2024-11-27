import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import box

catchments = (
    gpd.read_file("../output/all_catchments.shp")[["geometry", "name"]]
    .reset_index()
    .rename(columns={"index": "catchment_id"})
)
print("Successfully loaded all catchments")

lsoas = gpd.read_file("../data/lsoa/england/LSOA_2021_EW_BFC_V10.shp").set_index(
    "LSOA21CD"
)[["geometry"]]
print("Successfully read LSOAs")

uprns_df = pd.read_csv(
    "../data/uprn/uprns_full.csv",
    usecols=["UPRN", "LATITUDE", "LONGITUDE"],
)

uprns = gpd.GeoDataFrame(
    uprns_df,
    geometry=gpd.points_from_xy(uprns_df["LONGITUDE"], uprns_df["LATITUDE"]),
    crs="EPSG:4326",
)
print("read points from xy")


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
    # lat, lon = (52.612961, -0.713225)
    #
    # lat_offset = 0.1  # Roughly 5km offset; adjust based on location if needed
    # lon_offset = 0.14  # Roughly 5km offset; adjust based on location if needed
    # bbox = box(lon - lon_offset, lat - lat_offset, lon + lon_offset, lat + lat_offset)
    # gdf = gdf[gdf.intersects(bbox)]
    return gdf


catchments = remove_invalid_geometries(catchments)
lsoas = remove_invalid_geometries(lsoas)

catchments = crop_geodataframe(catchments)
lsoas = crop_geodataframe(lsoas)

print("Finished all preprocessing of the data")

df_metadata = pd.read_csv("../data/site_metadata/site_selection_list.csv")

catchments = gpd.GeoDataFrame(
    catchments[catchments.name.isin(df_metadata.water_company_name.unique().tolist())]
)

# Match catchments to LSOAs and compute overlap geometry
catchment_lsoa_overlap = gpd.sjoin(
    lsoas, catchments, how="left", predicate="intersects"
)

lsoas = gpd.GeoDataFrame(lsoas.loc[catchment_lsoa_overlap.index])

# Count UPRNs in each LSOA
uprns_with_lsoa = gpd.sjoin(uprns, lsoas, how="left", predicate="within")
uprns_per_lsoa = (
    uprns_with_lsoa.groupby(["LSOA21CD"]).size().rename("total_uprns").reset_index()
)

catchment_lsoa_overlap["overlap_geometry"] = catchment_lsoa_overlap.apply(
    lambda row: (
        row["geometry"].intersection(catchments.loc[row["index_right"], "geometry"])
        if pd.notnull(row["index_right"])
        else None
    ),
    axis=1,
)

catchment_lsoa_overlap["area_percentage"] = (
    catchment_lsoa_overlap["overlap_geometry"].area
    / catchment_lsoa_overlap["geometry"].area
)

catchment_lsoa_overlap = gpd.GeoDataFrame(
    catchment_lsoa_overlap.reset_index()[
        ["LSOA21CD", "name", "area_percentage", "overlap_geometry"]
    ].rename(columns={"overlap_geometry": "geometry"})
)

# Count UPRNs within each Catchment-LSOA overlap
uprns_with_overlap = gpd.sjoin(
    uprns, catchment_lsoa_overlap, how="left", predicate="intersects"
)
uprns_in_overlap = (
    uprns_with_overlap.groupby(["LSOA21CD", "name"])
    .size()
    .rename("uprns_in_overlap")
    .reset_index()
)

# Merge total UPRNs per LSOA to calculate percentage
uprns_in_overlap = uprns_in_overlap.merge(uprns_per_lsoa, on="LSOA21CD", how="left")
uprns_in_overlap["uprn_percentage"] = (
    uprns_in_overlap["uprns_in_overlap"] / uprns_in_overlap["total_uprns"]
) * 100

lsoa_to_catchment = uprns_in_overlap[["LSOA21CD", "name", "uprn_percentage"]].merge(
    catchment_lsoa_overlap[["LSOA21CD", "area_percentage"]], on="LSOA21CD"
)

lsoa_to_catchment.to_csv(
    "../output/intersections/catchment_lsoa_uprn_percentage_sampled.csv", index=False
)
