import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_population = pd.read_csv("../data/lsoa/demographics/england_population.csv")
df_lsoa_catchment = pd.read_csv(
    "../output/intersections/catchment_lsoa_uprn_percentage_sampled.csv"
)

df_lsoa_catchment_pop = pd.merge(df_population, df_lsoa_catchment, on="LSOA21CD")
df_lsoa_catchment_pop["uprn_population"] = (
    df_lsoa_catchment_pop["Total"] * df_lsoa_catchment_pop["uprn_percentage"]
) / 100
df_lsoa_catchment_pop["area_population"] = (
    df_lsoa_catchment_pop["Total"] * df_lsoa_catchment_pop["area_percentage"]
)

df = (
    df_lsoa_catchment_pop.groupby(by="name")[
        ["uprn_population", "area_population", "Total"]
    ]
    .sum()
    .reset_index()
)

# Calculate error values
lower_error = df["uprn_population"] - df["area_population"]
upper_error = df["Total"] - df["uprn_population"]
errors = [lower_error, upper_error]

# Create the plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    df["name"],
    df["uprn_population"],
    yerr=errors,
    capsize=5,
    color="skyblue",
    label="Central Estimate",
)

# Add labels and title
ax.set_xlabel("Category")
ax.set_ylabel("Population")
ax.set_title("Population Estimates with Error Bars")
ax.legend()

ax.set_xticklabels(df["name"], rotation=45, ha="right")

# Show the plot
plt.tight_layout()
plt.show()
