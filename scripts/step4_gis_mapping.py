import os
import logging
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (safe for scripts & notebooks)
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

logger = logging.getLogger(__name__)

COUNTIES_SHP = os.path.join("Counties (1)", "Counties.shp")
INPUT_PATH = os.path.join("outputs", "county_aggregated.csv")
MAP_DIR = os.path.join("outputs", "maps")


def _detect_county_name_col(gdf) -> str:
    """Auto-detect the county-name column in the shapefile."""
    candidates = ["COUNTYNAME", "NAME", "COUNTY", "County", "county_nam", "NAMELSAD"]
    for c in candidates:
        if c in gdf.columns:
            return c
    for c in gdf.columns:
        if gdf[c].dtype == "object" and c.upper() not in ("OBJECTID", "TYPE"):
            return c
    raise ValueError(f"Cannot detect county name column. Columns: {list(gdf.columns)}")


def load_geodata(shapefile: str = COUNTIES_SHP):
    """Load and return counties GeoDataFrame."""
    import geopandas as gpd
    gdf = gpd.read_file(shapefile)
    logger.info(f"Loaded shapefile: {len(gdf)} features, CRS={gdf.crs}")
    return gdf


def merge_data(gdf, county_data: pd.DataFrame):
    """Merge county stats onto the GeoDataFrame."""
    name_col = _detect_county_name_col(gdf)
    logger.info(f"Joining on shapefile column '{name_col}' ↔ COUNTY_NAME")

    # Normalize both sides for reliable join
    gdf["_join_key"] = gdf[name_col].astype(str).str.strip().str.upper()
    county_data["_join_key"] = county_data["COUNTY_NAME"].astype(str).str.strip().str.upper()

    merged = gdf.merge(county_data, on="_join_key", how="left")
    matched = merged["children_count"].notna().sum()
    logger.info(f"  → {matched}/{len(gdf)} counties matched")
    return merged


# ---------------------------------------------------------------------------
# Individual map generators
# ---------------------------------------------------------------------------

def plot_choropleth(
    gdf,
    column: str,
    title: str,
    cmap: str = "YlOrRd",
    label: str = "",
    filename: str = "choropleth.png",
    figsize=(14, 10),
):
    """Generic choropleth plotter."""
    fig, ax = plt.subplots(1, 1, figsize=figsize, facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    gdf.plot(
        column=column,
        cmap=cmap,
        legend=True,
        legend_kwds={
            "label": label,
            "orientation": "horizontal",
            "shrink": 0.6,
            "pad": 0.05,
        },
        edgecolor="#2d2d44",
        linewidth=0.5,
        missing_kwds={"color": "#2d2d44", "label": "No Data"},
        ax=ax,
    )

    ax.set_title(title, fontsize=18, fontweight="bold", color="white", pad=15)
    ax.axis("off")

    # Style legend text color
    cbar = fig.axes[-1] if len(fig.axes) > 1 else None
    if cbar:
        cbar.tick_params(colors="white")
        cbar.set_xlabel(cbar.get_xlabel(), color="white")

    out = os.path.join(MAP_DIR, filename)
    os.makedirs(MAP_DIR, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"  🗺️  Saved {out}")
    return out


def run(
    county_data: pd.DataFrame = None,
    input_path: str = INPUT_PATH,
    shapefile: str = COUNTIES_SHP,
) -> "GeoDataFrame":
    """
    Execute Step 4 — generate choropleth maps.

    Returns
    -------
    GeoDataFrame  (merged county geometry + stats)
    """
    if county_data is None:
        county_data = pd.read_csv(input_path)

    gdf = load_geodata(shapefile)
    merged = merge_data(gdf, county_data)

    # ---- Map 1: Children Count -----------------------------------------------
    plot_choropleth(
        merged,
        column="children_count",
        title="Total Child Placements by County — Florida",
        cmap="YlOrRd",
        label="Total Children Placed",
        filename="choropleth_children_count.png",
    )

    # ---- Map 2: Physical Abuse Prevalence ------------------------------------
    if "pct_physical_abuse" in merged.columns:
        merged["pct_physical_abuse_disp"] = merged["pct_physical_abuse"] * 100
        plot_choropleth(
            merged,
            column="pct_physical_abuse_disp",
            title="Physical Abuse Prevalence by County — Florida",
            cmap="Reds",
            label="Prevalence Rate (%)",
            filename="choropleth_maltreatment.png",
        )

    # ---- Map 3: Demographic — % Black ----------------------------------------
    if "pct_fl_race_black" in merged.columns:
        merged["pct_fl_race_black_disp"] = merged["pct_fl_race_black"] * 100
        plot_choropleth(
            merged,
            column="pct_fl_race_black_disp",
            title="Proportion of Black Children in Placement — Florida",
            cmap="Blues",
            label="Proportion (%)",
            filename="choropleth_demographics.png",
        )

    # ---- Map 4: Average Placement Duration -----------------------------------
    if "avg_placement_duration" in merged.columns:
        plot_choropleth(
            merged,
            column="avg_placement_duration",
            title="Average Placement Duration (Days) — Florida",
            cmap="Purples",
            label="Avg Duration (Days)",
            filename="choropleth_duration.png",
        )

    logger.info("  ✅ All maps generated")
    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
