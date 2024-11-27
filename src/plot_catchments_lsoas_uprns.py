import fiona
import geopandas as gpd
from tqdm.notebook import tqdm
import pandas as pd
import pathlib
import folium
from shapely.geometry import box

uprns_in_overlap = pd.read_csv(
    "../output/intersections/catchment_lsoa_uprn_percentage.csv"
)

catchments = (
    gpd.read_file("../output/all_catchments.shp")[["geometry"]]
    .reset_index()
    .rename(columns={"index": "catchment_id"})
)
print("Successfully loaded all catchments")

lsoas = gpd.read_file("..data/lsoa/england/LSOA_2021_EW_BFC_V10.shp").set_index(
    "LSOA21CD"
)[["geometry"]]
print("Successfully read LSOAs")

uprns_df = pd.read_csv(
    "../data/uprn/uprns_crop.csv",
    usecols=["UPRN", "LATITUDE", "LONGITUDE"],
)

uprns = gpd.GeoDataFrame(
    uprns_df,
    geometry=gpd.points_from_xy(uprns_df["LONGITUDE"], uprns_df["LATITUDE"]),
    crs="EPSG:4326",
)
print("read points from xy")


def crop_geodataframe(gdf):
    gdf = gdf.to_crs("EPSG:4326")
    lat, lon = (52.612961, -0.713225)
    lat_offset = 0.10  # Roughly 5km offset; adjust based on location if needed
    lon_offset = 0.14  # Roughly 5km offset; adjust based on location if needed
    bbox = box(lon - lon_offset, lat - lat_offset, lon + lon_offset, lat + lat_offset)
    gdf = gdf[gdf.intersects(bbox)]
    return gdf


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


catchments = remove_invalid_geometries(catchments)
lsoas = remove_invalid_geometries(lsoas)

catchments = crop_geodataframe(catchments)
lsoas = crop_geodataframe(lsoas)

lsoas = gpd.GeoDataFrame(pd.merge(lsoas, uprns_in_overlap, on="LSOA21CD"))

# Create the folium map centered at the bounding box center in lat/lon
m = folium.Map(location=[52.612961, -0.713225], zoom_start=12, crs="EPSG3857")

lsoa_uprn_layer = folium.FeatureGroup(name="LSOAs by UPRN Coverage", show=True)
catchment_layer = folium.FeatureGroup(name="Catchment Boundaries", show=True)
uprn_layer = folium.FeatureGroup(name="UPRNs", show=True)


# Function to assign colors based on percentage covered
def get_color(percentage):
    if percentage > 75:
        return "darkgreen"
    elif percentage > 50:
        return "green"
    elif percentage > 25:
        return "orange"
    else:
        return "gray"


for _, row in lsoas.iterrows():
    color = get_color(row["percentage"])
    folium.GeoJson(
        row["geometry"],
        style_function=lambda feature, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.6,
        },
    ).add_to(lsoa_uprn_layer)

# Overlay catchment boundaries on the catchment layer
for _, row in catchments.iterrows():
    folium.GeoJson(
        row["geometry"],
        style_function=lambda feature: {
            "fillColor": "blue",
            "color": "blue",
            "weight": 1,
            "fillOpacity": 0.2,
        },
    ).add_to(catchment_layer)

# Add UPRNs as points to the map in the UPRN layer
for _, row in uprns.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=2,
        color="red",
        fill=True,
        fill_opacity=0.6,
    ).add_to(uprn_layer)

# Add layers to the map
lsoa_uprn_layer.add_to(m)
catchment_layer.add_to(m)
uprn_layer.add_to(m)

# Add a Layer Control to toggle layers on/off
folium.LayerControl().add_to(m)

# Display the map
m.save("LSOA_UPRN_map.html")
