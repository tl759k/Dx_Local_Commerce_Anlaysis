import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Assuming June_2025_snapshot is already defined in your notebook
# If running as standalone script, you'll need to load the data first
# For notebook use, just run this after your data preparation cells

def create_cbsa_map(df_data, column_name='new_dx_share_of_18plus_population', 
                   title_suffix='', cmap='viridis_r'):
    """
    Create a CBSA map with color-coded data
    
    Parameters:
    df_data: DataFrame containing cbsa_code and the column to map
    column_name: Name of the column to use for coloring
    title_suffix: Additional text for the title
    cmap: Colormap to use
    """
    
    # Copy and prepare data
    df = df_data.copy()
    df['cbsa_code'] = df['cbsa_code'].astype(str)
    
    # Load CBSA shapefile
    cbsa = gpd.read_file("./tl_2024_us_cbsa/tl_2024_us_cbsa.shp")
    cbsa['CBSAFP'] = cbsa['CBSAFP'].astype(str)
    
    # Load State shapefile for boundaries
    states = gpd.read_file("./tl_2024_us_state/tl_2024_us_state.shp")
    
    # Reproject to US Albers Equal Area for better mainland US visualization
    cbsa = cbsa.to_crs("EPSG:5070")
    states = states.to_crs("EPSG:5070")
    
    # Filter to mainland US by removing Alaska & Hawaii using centroid bounds
    # Mainland US approximate bounds in EPSG:5070 (meters)
    xmin, xmax = -2500000, -1000000  # Adjusted bounds for better coverage
    ymin, ymax = 1000000, 3000000
    
    # Calculate centroids for filtering
    cbsa_centroids = cbsa.geometry.centroid
    mainland_mask = (
        cbsa_centroids.x.between(-2500000, -1000000) & 
        cbsa_centroids.y.between(1000000, 3000000)
    )
    cbsa_mainland = cbsa[mainland_mask].copy()
    
    # If no data in mainland bounds, use broader bounds
    if len(cbsa_mainland) == 0:
        print("No data in strict mainland bounds, using broader bounds...")
        xmin, xmax = -3000000, -500000
        ymin, ymax = 500000, 3500000
        mainland_mask = (
            cbsa_centroids.x.between(xmin, xmax) & 
            cbsa_centroids.y.between(ymin, ymax)
        )
        cbsa_mainland = cbsa[mainland_mask].copy()
    
    # Filter states to mainland US as well
    states_centroids = states.geometry.centroid
    states_mainland_mask = (
        states_centroids.x.between(xmin, xmax) & 
        states_centroids.y.between(ymin, ymax)
    )
    states_mainland = states[states_mainland_mask].copy()
    
    # Simplify geometries for better performance
    cbsa_mainland["geometry"] = cbsa_mainland["geometry"].simplify(
        tolerance=1000, preserve_topology=True
    )
    states_mainland["geometry"] = states_mainland["geometry"].simplify(
        tolerance=2000, preserve_topology=True
    )
    
    # Merge shapefile with your data
    merged = cbsa_mainland.merge(df, left_on="CBSAFP", right_on="cbsa_code", how="left")
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Plot CBSAs without data in light gray
    merged[merged[column_name].isna()].plot(
        color='lightgray',
        linewidth=0.1,
        edgecolor="white",
        ax=ax,
        alpha=0.5
    )
    
    # Plot CBSAs with data
    data_to_plot = merged[merged[column_name].notna()]
    
    if len(data_to_plot) > 0:
        # Create the main plot with color mapping
        im = data_to_plot.plot(
            column=column_name,
            cmap=cmap,
            linewidth=0.1,
            edgecolor="white",
            legend=False,  # We'll add a custom colorbar
            ax=ax,
            alpha=0.8
        )
        
        # Add colorbar
        vmin = data_to_plot[column_name].min()
        vmax = data_to_plot[column_name].max()
        
        # Create colorbar
        sm = plt.cm.ScalarMappable(
            cmap=cmap, 
            norm=plt.Normalize(vmin=vmin, vmax=vmax)
        )
        sm.set_array([])
        
        # Add colorbar to the plot
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6, aspect=20)
        cbar.set_label(f'{column_name.replace("_", " ").title()}', 
                      rotation=270, labelpad=20, fontsize=12)
        
        # Format colorbar labels
        if column_name == 'new_dx_share_of_18plus_population':
            # Format as percentage
            cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
    
    # Add state boundary lines
    states_mainland.plot(
        ax=ax,
        facecolor='none',        # No fill
        edgecolor='black',       # Black boundary lines
        linewidth=1.2,           # Slightly thicker lines for visibility
        alpha=0.8                # Slight transparency
    )
    
    # Set title
    title_text = f"U.S. Mainland CBSA Map - {column_name.replace('_', ' ').title()}"
    if title_suffix:
        title_text += f" {title_suffix}"
    
    ax.set_title(title_text, fontsize=16, pad=20, fontweight='bold')
    ax.axis("off")
    
    # Add some statistics as text
    if len(data_to_plot) > 0:
        stats_text = f"""
        CBSAs with data: {len(data_to_plot):,}
        CBSAs without data: {len(merged[merged[column_name].isna()]):,}
        Min: {data_to_plot[column_name].min():.3f}
        Max: {data_to_plot[column_name].max():.3f}
        Mean: {data_to_plot[column_name].mean():.3f}
        """
        
        ax.text(0.02, 0.98, stats_text.strip(), transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    return fig, ax, merged, states_mainland

# Main execution code
if __name__ == "__main__":
    # For standalone script, you'd need to load June_2025_snapshot here
    # For notebook, just call the function with your data
    
    # Example usage (uncomment when running in notebook):
    # fig, ax, merged_data, states_data = create_cbsa_map(
    #     June_2025_snapshot, 
    #     'new_dx_share_of_18plus_population',
    #     '(June 2025 Snapshot)'
    # )
    # plt.show()
    
    print("Geo mapping functions defined. Use create_cbsa_map() to generate your map.")
