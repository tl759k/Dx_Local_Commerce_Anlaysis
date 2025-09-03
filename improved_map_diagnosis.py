import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# Assuming your data is already prepared as in your original code
# df = June_2025_snapshot.copy()
# df['cbsa_code'] = df['cbsa_code'].astype(str).str.zfill(5)

# Load CBSA polygons (MSA+µSA) from local file
cbsa = gpd.read_file("./tl_2024_us_cbsa/tl_2024_us_cbsa.shp")
cbsa['CBSAFP'] = cbsa['CBSAFP'].astype(str).str.zfill(5)

# Keep only MSAs and mainland
if 'LSAD' in cbsa.columns:
    cbsa = cbsa[cbsa['LSAD'] == 'M1'].copy()

cbsa_ll = cbsa.to_crs(4326)
rep_pts = cbsa_ll.geometry.representative_point()
mainland_mask = rep_pts.x.between(-125, -66) & rep_pts.y.between(24, 50)
cbsa_mainland = cbsa.loc[mainland_mask].copy()
cbsa_mainland = cbsa_mainland.to_crs(5070)
cbsa_mainland["geometry"] = cbsa_mainland.geometry.simplify(tolerance=1000, preserve_topology=True)

# DIAGNOSTIC 1: Check how many MSAs we have
print(f"Total mainland MSAs: {len(cbsa_mainland)}")

# Join your metric (assuming df is your data)
# Replace this with your actual data loading
# For now, I'll create sample data to demonstrate
print("Creating sample data for demonstration...")
sample_data = pd.DataFrame({
    'cbsa_code': cbsa_mainland['CBSAFP'].head(50),  # Only first 50 MSAs have data
    'new_dx_share_of_18plus_population': np.random.uniform(0.001, 0.01, 50)
})

merged = cbsa_mainland.merge(
    sample_data[['cbsa_code', 'new_dx_share_of_18plus_population']],
    left_on="CBSAFP",
    right_on="cbsa_code",
    how="left"
)

# DIAGNOSTIC 2: Check merge results
print(f"MSAs with data: {merged['new_dx_share_of_18plus_population'].notna().sum()}")
print(f"MSAs without data: {merged['new_dx_share_of_18plus_population'].isna().sum()}")

# Fill NaN with a very small value instead of 0.002
merged['new_dx_share_of_18plus_population'] = merged['new_dx_share_of_18plus_population'].fillna(0.0001)

# DIAGNOSTIC 3: Check data distribution
print(f"Data range: {merged['new_dx_share_of_18plus_population'].min():.6f} to {merged['new_dx_share_of_18plus_population'].max():.6f}")
print(f"Data distribution:")
print(merged['new_dx_share_of_18plus_population'].describe())

# Load state boundaries
states = gpd.read_file("./tl_2024_us_state/tl_2024_us_state.shp")
states = states.to_crs(4326)
rep_pts_states = states.geometry.representative_point()
mainland_states_mask = rep_pts_states.x.between(-125, -66) & rep_pts_states.y.between(24, 50)
states_mainland = states.loc[mainland_states_mask].copy()
states_mainland = states_mainland.to_crs(5070)
states_mainland["geometry"] = states_mainland.geometry.simplify(tolerance=1000, preserve_topology=True)

# -----------------------------
# IMPROVED PLOTTING
# -----------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# PLOT 1: Show which areas have data vs no data
has_data = merged['cbsa_code'].notna()
no_data_msas = merged.loc[~has_data]
data_msas = merged.loc[has_data]

# Base: state boundaries for both plots
states_mainland.boundary.plot(ax=ax1, color="lightgray", linewidth=0.5)
states_mainland.boundary.plot(ax=ax2, color="lightgray", linewidth=0.5)

# Plot 1: Data availability
if len(no_data_msas) > 0:
    no_data_msas.plot(ax=ax1, color="lightgray", edgecolor="white", linewidth=0.1, alpha=0.5, label="No Data")
if len(data_msas) > 0:
    data_msas.plot(ax=ax1, color="darkblue", edgecolor="white", linewidth=0.1, alpha=0.7, label="Has Data")

ax1.set_title(f"Data Availability\n({len(data_msas)} MSAs with data, {len(no_data_msas)} without)", fontsize=12)
ax1.set_aspect("equal")
ax1.axis("off")
ax1.legend()

# PLOT 2: Improved color mapping with colorbar
# Use a different approach for better visibility
vmin = merged['new_dx_share_of_18plus_population'].min()
vmax = merged['new_dx_share_of_18plus_population'].max()

# Create the plot with colorbar
im = merged.plot(
    ax=ax2,
    column="new_dx_share_of_18plus_population",
    cmap="viridis",  # Try viridis instead of viridis_r
    edgecolor="white",
    linewidth=0.1,
    legend=True,
    legend_kwds={
        'label': "Dx Share of 18+ Population",
        'orientation': "horizontal",
        'shrink': 0.8,
        'pad': 0.05
    },
    vmin=vmin,
    vmax=vmax
)

ax2.set_title(f"Dx Share of 18+ Population\n(Range: {vmin:.4f} to {vmax:.4f})", fontsize=12)
ax2.set_aspect("equal")
ax2.axis("off")

plt.tight_layout()
plt.show()

# DIAGNOSTIC 4: Final checks
print("\nFinal diagnostics:")
print(f"NaNs remaining: {merged['new_dx_share_of_18plus_population'].isna().sum()}")
print(f"Zero values: {(merged['new_dx_share_of_18plus_population'] == 0).sum()}")
print(f"Very small values (< 0.001): {(merged['new_dx_share_of_18plus_population'] < 0.001).sum()}")

# Show some examples of MSAs without data
if len(no_data_msas) > 0:
    print(f"\nFirst 5 MSAs without data:")
    print(no_data_msas[['CBSAFP', 'NAME']].head())
