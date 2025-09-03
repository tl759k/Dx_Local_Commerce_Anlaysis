import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# -----------------------------
# Inputs (use your existing data)
# -----------------------------
df = June_2025_snapshot.copy()
df['cbsa_code'] = df['cbsa_code'].astype(str).str.zfill(5)

# Load CBSA polygons
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

# Join your metric
merged = cbsa_mainland.merge(
    df[['cbsa_code', 'new_dx_share_of_18plus_population']],
    left_on="CBSAFP",
    right_on="cbsa_code",
    how="left"
)

# DIAGNOSTIC PRINTS
print(f"Total MSAs: {len(merged)}")
print(f"MSAs with data: {merged['new_dx_share_of_18plus_population'].notna().sum()}")
print(f"MSAs without data: {merged['new_dx_share_of_18plus_population'].isna().sum()}")

# Fill NaN with a distinguishable small value
merged['new_dx_share_of_18plus_population'] = merged['new_dx_share_of_18plus_population'].fillna(0.0001)

# Check data range
print(f"Data range: {merged['new_dx_share_of_18plus_population'].min():.6f} to {merged['new_dx_share_of_18plus_population'].max():.6f}")

# Load state boundaries
states = gpd.read_file("./tl_2024_us_state/tl_2024_us_state.shp")
states = states.to_crs(4326)
rep_pts_states = states.geometry.representative_point()
mainland_states_mask = rep_pts_states.x.between(-125, -66) & rep_pts_states.y.between(24, 50)
states_mainland = states.loc[mainland_states_mask].copy()
states_mainland = states_mainland.to_crs(5070)
states_mainland["geometry"] = states_mainland.geometry.simplify(tolerance=1000, preserve_topology=True)

# -----------------------------
# FIXED PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(12, 6))

# Base: state boundaries
states_mainland.boundary.plot(ax=ax, color="black", linewidth=0.8, alpha=0.3)

# Get data range for better color scaling
vmin = merged['new_dx_share_of_18plus_population'].min()
vmax = merged['new_dx_share_of_18plus_population'].max()

# Plot MSAs with COLORBAR and better color settings
merged.plot(
    ax=ax,
    column="new_dx_share_of_18plus_population",
    cmap="viridis",  # Try viridis instead of viridis_r for better contrast
    edgecolor="white",
    linewidth=0.2,
    legend=True,  # ENABLE LEGEND/COLORBAR
    legend_kwds={
        'label': "Dx Share of 18+ Population",
        'orientation': "horizontal",
        'shrink': 0.8,
        'pad': 0.08,
        'format': '%.4f'  # Show more decimal places
    },
    vmin=vmin,
    vmax=vmax
)

# Final touches
ax.set_title("U.S. Mainland MSAs — Dx Share of 18+ Population", fontsize=14, pad=20)
ax.set_aspect("equal")
ax.axis("off")
plt.tight_layout()
plt.show()

print("NaNs remaining:", merged['new_dx_share_of_18plus_population'].isna().sum())
print("Min value:", merged['new_dx_share_of_18plus_population'].min())
print("Max value:", merged['new_dx_share_of_18plus_population'].max())

# Show which MSAs don't have data
no_data_msas = merged[merged['cbsa_code'].isna()]
if len(no_data_msas) > 0:
    print(f"\nMSAs without data ({len(no_data_msas)}):")
    print(no_data_msas[['CBSAFP', 'NAME']].head(10))
