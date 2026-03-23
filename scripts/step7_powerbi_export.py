import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Input paths
FACT_INPUT = os.path.join("outputs", "cleaned_with_county.csv")
DIM_INPUT = os.path.join("outputs", "county_aggregated.csv")

# Output paths
PBI_DIR = os.path.join("outputs", "powerbi")
FACT_OUTPUT = os.path.join(PBI_DIR, "Placements_Fact.csv")
DIM_OUTPUT = os.path.join(PBI_DIR, "County_Stats_Dim.csv")


def _clean_col_name(col: str) -> str:
    """Convert raw snake_case column names into PowerBI friendly names."""
    if col == "AFCARS_ID":
        return "AFCARS ID"
    col = col.replace("pct_fl_race_", "Race ")
    col = col.replace("pct_", "")
    col = col.replace("_", " ")
    return col.title()


def export_fact_table(input_path=FACT_INPUT, output_path=FACT_OUTPUT):
    """Clean and export the granular placements fact table."""
    logger.info(f"Loading Fact Table from {input_path}...")
    if not os.path.exists(input_path):
        logger.error(f"Missing input file: {input_path}")
        return

    # Load with low_memory=False to avoid mixed type warnings on large datasets
    df = pd.read_csv(input_path, dtype=str, low_memory=False)

    # Convert column names to Title Case
    df.columns = [_clean_col_name(c) for c in df.columns]

    # Geolocation Fix: Append State so PowerBI maps natively to Florida
    if "County Name" in df.columns:
        df["County Name"] = df["County Name"].astype(str).str.title() + " County, FL"
        # We also add a dedicated State column just in case
        df["State"] = "FL"

    # Save
    os.makedirs(PBI_DIR, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"  ✅ Saved PowerBI Fact Table -> {output_path} ({len(df):,} rows)")


def export_dim_table(input_path=DIM_INPUT, output_path=DIM_OUTPUT):
    """Clean and export the county dimension table."""
    logger.info(f"Loading Dimension Table from {input_path}...")
    if not os.path.exists(input_path):
        logger.error(f"Missing input file: {input_path}")
        return

    df = pd.read_csv(input_path)

    # Round floating point columns to 3 decimal places for clean display
    float_cols = df.select_dtypes(include=['float64']).columns
    df[float_cols] = df[float_cols].round(3)

    # Rename specific columns for ultimate clarity
    rename_map = {
        "COUNTY_NAME": "County Name",
        "children_count": "Total Children Placed",
        "placement_count": "Total Placements",
        "avg_placement_duration": "Avg Placement Duration (Days)",
        "avg_age_at_removal": "Average Age at Removal",
    }
    df.rename(columns=rename_map, inplace=True)

    # Rename remaining columns nicely
    df.columns = [_clean_col_name(c) if c not in rename_map.values() else c for c in df.columns]

    # Geolocation Fix: Fix ambiguous Bing Maps geolocation
    if "County Name" in df.columns:
        df["County Name"] = df["County Name"].astype(str).str.title() + " County, FL"
        df["State"] = "FL"

    # Save
    os.makedirs(PBI_DIR, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"  ✅ Saved PowerBI Dim Table -> {output_path} ({len(df):,} counties)")


def run():
    export_dim_table()
    export_fact_table()
    logger.info("🎉 PowerBI Export Complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
