import geopandas as gpd
import matplotlib.pyplot as plt


gdf_ni = gpd.read_file("../data/lsoa/northern_ireland/DZ2021.shp")
gdf_ni.plot()

gdf_scot = gpd.read_file("../data/lsoa/scotland/OutputArea2022_MHW.shp")
gdf_scot.plot()
plt.show()
