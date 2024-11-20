import geopandas as gpd
import pandas as pd
import folium

catchments = gpd.read_file(
    "../data/processed_ww_catchments/catchments_consolidated.shp"
).set_index("identifier")
catchments.set_crs(epsg=27700, inplace=True)
catchments = catchments.to_crs(4326)

gdf = catchments[catchments.company == "anglian_water"]
# Apply a small buffer to expand the polygons
buffered_catchments = gdf.geometry.buffer(0.01)  # adjust buffer size as needed

# Perform a unary union to combine all polygons
combined_area = buffered_catchments.union_all()

# Optionally, compute the convex hull of the union
convex_hull = combined_area.convex_hull

# Create a GeoDataFrame for the resulting area
result_gdf = gpd.GeoDataFrame(geometry=[convex_hull], crs=gdf.crs)

result_gdf.to_file("../../AngliaWaterPPM/data/bounding_area/bounding_area.shp")

m = folium.Map(zoom_start=5)

# Convert GeoDataFrame to GeoJSON
geojson_data = result_gdf.__geo_interface__

# Add the GeoJSON layer to the map
folium.GeoJson(
    result_gdf,
    name="Catchments",
).add_to(m)

# Save the map to an HTML file
m.save("catchments_map_anglian.html")
