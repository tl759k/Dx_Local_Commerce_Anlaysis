# Fixed version of your original code
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# Your data preparation (assuming June_2025_snapshot is already defined)
df = June_2025_snapshot.copy()
df['cbsa_code'] = df['cbsa_code'].astype(str)

# Load CBSA shapefile
cbsa = gpd.read_file("./tl_2024_us_cbsa/tl_2024_us_cbsa.shp")
cbsa['CBSAFP'] = cbsa['CBSAFP'].astype(str)

# Load State shapefile for boundaries
states = gpd.read_file("./tl_2024_us_state/tl_2024_us_state.shp")

# Reproject to US Albers Equal Area
cbsa = cbsa.to_crs("EPSG:5070")
states = states.to_crs("EPSG:5070")

# --- Drop Alaska & Hawaii by filtering centroids ---
# Adjusted mainland bounds (in EPSG:5070 meters) for better coverage
xmin, xmax = -2500000, -1000000
ymin, ymax = 1000000, 3000000

# Calculate centroids for filtering
cbsa_centroids = cbsa.geometry.centroid
mainland_filter = (
    cbsa_centroids.x.between(xmin, xmax) & 
    cbsa_centroids.y.between(ymin, ymax)
)

# Apply filter to CBSAs
cbsa = cbsa[mainland_filter]

# Filter states to mainland US as well
states_centroids = states.geometry.centroid
states_mainland_filter = (
    states_centroids.x.between(xmin, xmax) & 
    states_centroids.y.between(ymin, ymax)
)
states = states[states_mainland_filter]

# Simplify geometries
cbsa["geometry"] = cbsa["geometry"].simplify(tolerance=1000, preserve_topology=True)
states["geometry"] = states["geometry"].simplify(tolerance=2000, preserve_topology=True)

# Merge shapefile with your data
merged = cbsa.merge(df, left_on="CBSAFP", right_on="cbsa_code", how="left")

# --- Plot ---
fig, ax = plt.subplots(1, 1, figsize=(16, 10))

# Plot CBSAs without data in light gray
no_data_mask = merged["new_dx_share_of_18plus_population"].isna()
merged[no_data_mask].plot(
    color='lightgray',
    linewidth=0.1,
    edgecolor="white",
    ax=ax,
    alpha=0.5
)

# Plot CBSAs with data
data_cbsas = merged[~no_data_mask]
if len(data_cbsas) > 0:
    data_cbsas.plot(
        column="new_dx_share_of_18plus_population",
        cmap="viridis_r",
        linewidth=0.1,
        edgecolor="white",
        legend=False,
        ax=ax,
        alpha=0.8
    )
    
    # Add colorbar
    vmin = data_cbsas["new_dx_share_of_18plus_population"].min()
    vmax = data_cbsas["new_dx_share_of_18plus_population"].max()
    
    sm = plt.cm.ScalarMappable(
        cmap="viridis_r", 
        norm=plt.Normalize(vmin=vmin, vmax=vmax)
    )
    sm.set_array([])
    
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, aspect=20)
    cbar.set_label('New Dx Share of 18+ Population', rotation=270, labelpad=20, fontsize=12)
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))

# Add state boundary lines
states.plot(
    ax=ax,
    facecolor='none',        # No fill
    edgecolor='black',       # Black boundary lines
    linewidth=1.2,           # Slightly thicker lines for visibility
    alpha=0.8                # Slight transparency
)

# Add statistics
if len(data_cbsas) > 0:
    stats_text = f"""CBSAs with data: {len(data_cbsas):,}
CBSAs without data: {len(merged[no_data_mask]):,}
Range: {data_cbsas['new_dx_share_of_18plus_population'].min():.3f} - {data_cbsas['new_dx_share_of_18plus_population'].max():.3f}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.set_title("U.S. Mainland CBSA Map - New Dx Share of 18+ Population (June 2025)", 
             fontsize=16, pad=20, fontweight='bold')
ax.axis("off")

plt.tight_layout()
plt.show()

# Print some basic info about the merge
print(f"\nData Summary:")
print(f"Total CBSAs in shapefile (mainland): {len(cbsa):,}")
print(f"CBSAs in your data: {len(df):,}")
print(f"CBSAs with matched data: {len(data_cbsas):,}")
print(f"CBSAs without data: {len(merged[no_data_mask]):,}")

if len(data_cbsas) > 0:
    print(f"\nMetric Statistics:")
    print(f"Min: {data_cbsas['new_dx_share_of_18plus_population'].min():.4f} ({data_cbsas['new_dx_share_of_18plus_population'].min():.2%})")
    print(f"Max: {data_cbsas['new_dx_share_of_18plus_population'].max():.4f} ({data_cbsas['new_dx_share_of_18plus_population'].max():.2%})")
    print(f"Mean: {data_cbsas['new_dx_share_of_18plus_population'].mean():.4f} ({data_cbsas['new_dx_share_of_18plus_population'].mean():.2%})")
    print(f"Median: {data_cbsas['new_dx_share_of_18plus_population'].median():.4f} ({data_cbsas['new_dx_share_of_18plus_population'].median():.2%})")
