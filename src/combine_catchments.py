import geopandas as gpd
import pandas as pd
import folium

# loading the catchments from the FOI request
gdf_sww = gpd.read_file(
    "../data/raw_ww_catchments/sww_catchments/EIR24252 CATCHMENT POLYGONS.shp"
)
gdf_sww.set_crs(epsg=27700, inplace=True)
gdf_sww = gdf_sww.to_crs(4326)
gdf_sww = gdf_sww[["CATCHMENT1", "geometry"]].rename(columns={"CATCHMENT1": "name"})

gdf_ni = gpd.read_file(
    "../data/raw_ww_catchments/NorthernIrelandWater/WWTW Upstream Catchment Areas.shp"
)
# gdf_ni.set_crs(epsg=27700, inplace=True)
gdf_ni = gdf_ni.to_crs(4326)
gdf_ni = gdf_ni[["NAME", "geometry"]].rename(columns={"NAME": "name"})


catchments = gpd.read_file(
    "../data/processed_ww_catchments/catchments_consolidated.shp"
).set_index("identifier")
catchments.set_crs(epsg=27700, inplace=True)
catchments = catchments.to_crs(4326)

gdf = gpd.GeoDataFrame(pd.concat([catchments, gdf_sww, gdf_ni]), geometry="geometry")

gdf.to_file("../output/all_catchments.shp")

# m = folium.Map(location=[55, -3], zoom_start=5)
#
# # Convert GeoDataFrame to GeoJSON
# geojson_data = gdf.__geo_interface__
#
# # Add the GeoJSON layer to the map
# folium.GeoJson(
#     geojson_data,
#     name="Catchments",
#     tooltip=folium.GeoJsonTooltip(
#         fields=["name"]
#     ),  # Replace with your field names for tooltips
# ).add_to(m)
#
# # Save the map to an HTML file
# m.save("catchments_map_all.html")
