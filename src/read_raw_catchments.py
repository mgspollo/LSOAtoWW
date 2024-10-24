import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

water_company_to_file_name = {
    "WXW": "../data/raw_ww_catchments/WxW WRC Catchments Dec2021/WxW_WRC_Catchments_Dec2021.shp",
    "AW": "../data/raw_ww_catchments/WWCATCHPOLY 23 04 2021/WWCATCHPOLY.shp",
    "UU": "../data/raw_ww_catchments/UUDrainageAreas040122/UUDrainageAreas040122.shp",
    "NW": "../data/raw_ww_catchments/STW Catchments/Export/NWGIS.STW_AREA_polygon.shp",
    "SW": "../data/raw_ww_catchments/swsdrain region/swsdrain_region.shp",
    "TW": "../data/raw_ww_catchments/SDAC/SDAC.shp",
    "YW": "../data/raw_ww_catchments/EIR Wastewater Catchments/EIR - Wastewater Catchments/Wastewater Catchments.shp",
    "SCW": "../data/raw_ww_catchments/DOAs and WWTWs/DOAs and WWTWs/DOA_Zones.shp",
    "WW": "../data/raw_ww_catchments/DCWW Catchments/DCWW_Catchments1.shp",
    "SWW": "../data/raw_ww_catchments/sww_catchments/EIR24252 CATCHMENT POLYGONS.shp",
}

gdf_all = gpd.GeoDataFrame()
for wc, fn in water_company_to_file_name.items():
    gdf = gpd.read_file(fn)
    gdf = gdf.to_crs(4326)
    gdf_all = gpd.GeoDataFrame(pd.concat([gdf_all, gdf]))

fig, ax = plt.subplots(figsize=(20, 20))
gdf_all.plot(ax=ax)
ax.axis('off')
plt.show()