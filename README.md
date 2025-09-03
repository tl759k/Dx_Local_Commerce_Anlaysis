# Local E-commerce Analysis - Half Pager Questions

This repository contains analysis related to local e-commerce market penetration and geographic visualization of key metrics.

## 📊 Analysis Overview

This project analyzes DoorDash market penetration using MSA (Metropolitan Statistical Area) level data, focusing on:
- New Dasher (Dx) share of 18+ population by MSA
- Geographic visualization of market saturation
- Unemployment rate correlations
- Market-level insights for strategic planning

## 🗂️ Repository Structure

```
half_pager_qs/
├── analysis.ipynb                    # Main analysis notebook
├── q1_lifetime_apps_and_new_dx_by_msa.sql   # SQL query for lifetime applications and new dashers
├── q2_monthly_active_dx_by_msa.sql          # SQL query for monthly active dashers
├── fixed_geo_map.py                  # Geographic mapping visualization script
├── fixed_map_code.py                 # Corrected mapping code
├── improved_map_diagnosis.py         # Diagnostic tools for map visualization
├── simple_geo_map_fix.py            # Simplified mapping script
├── data files/
│   ├── 1_lifetime_new_dx_by_msa.csv         # Lifetime new Dasher data
│   ├── df_msa_saturation_ur.csv             # MSA saturation with unemployment rates
│   ├── unemployment_rate.csv               # Base unemployment rate data
│   └── UR_updated.csv                      # Updated unemployment rate data
└── geographic_data/
    ├── tl_2024_us_cbsa/                    # US CBSA (MSA) shapefiles
    └── tl_2024_us_state/                   # US state boundary shapefiles
```

## 🛠️ Technical Requirements

### Python Dependencies
- `pandas` - Data manipulation and analysis
- `geopandas` - Geographic data processing
- `matplotlib` - Data visualization
- `numpy` - Numerical computations

### Data Sources
- **Census TIGER/Line Shapefiles**: US CBSA and state boundaries
- **Internal DoorDash Data**: Dasher application and activity metrics
- **BLS Data**: Unemployment rates by MSA

## 🗺️ Key Visualizations

### Geographic Market Penetration Map
The main visualization shows US mainland MSAs colored by new Dasher share of 18+ population:
- **Dark areas**: Higher market penetration
- **Light areas**: Lower market penetration
- **White areas**: No data available

### Features:
- Mainland US focus (excludes Alaska, Hawaii, Puerto Rico)
- MSA-level granularity
- State boundary overlays for reference
- Color-coded penetration rates

## 📈 Key Metrics

- **New Dx Share of 18+ Population**: Primary market penetration metric
- **MSA Coverage**: Analysis covers mainland US Metropolitan Statistical Areas
- **Unemployment Rate Correlation**: Secondary analysis factor

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   pip install pandas geopandas matplotlib numpy
   ```

2. **Run Main Analysis**:
   ```bash
   jupyter notebook analysis.ipynb
   ```

3. **Generate Maps**:
   ```bash
   python fixed_geo_map.py
   ```

## 📝 Notes

- Shapefiles are from 2024 Census TIGER/Line data
- Analysis focuses on mainland US MSAs only
- Data is aggregated at MSA level for privacy and analytical purposes
- Missing data areas are filled with minimal values for visualization consistency

## 🔍 Analysis Insights

Key findings from this analysis include market penetration patterns, geographic clustering of high/low penetration areas, and correlations with unemployment rates at the MSA level.

---

**Generated**: January 2025  
**Data Sources**: Internal DoorDash analytics, US Census Bureau, Bureau of Labor Statistics
