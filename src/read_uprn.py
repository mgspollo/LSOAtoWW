import pandas as pd
import geopandas as gpd
from utility.utility_functions import crop_geodataframe


def process_uprns(is_crop=False):
    uprns_df = pd.read_csv(
        "../data/uprn/osopenuprn_202409.csv",
        usecols=["UPRN", "LATITUDE", "LONGITUDE"],
    )
    print("read uprns")

    if is_crop:
        uprns = crop_uprns(uprns_df)
        uprns.to_csv("../data/uprn/uprns_crop.csv", index=False)
    else:
        uprns_df.to_csv("../data/uprn/uprns_full.csv", index=False)


def crop_uprns(uprns_df):
    uprns = gpd.GeoDataFrame(
        uprns_df,
        geometry=gpd.points_from_xy(uprns_df["LONGITUDE"], uprns_df["LATITUDE"]),
        crs="EPSG:4326",
    )
    print("read points from xy")

    uprns = crop_geodataframe(uprns)
    print("cropped dataframe")

    uprns = uprns[["UPRN", "LATITUDE", "LONGITUDE"]]
    return uprns


if __name__ == "__main__":
    process_uprns(is_crop=False)
