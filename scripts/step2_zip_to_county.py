import os
import logging
import urllib.request
import pandas as pd

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join("outputs", "cleaned_merged_data.csv")
OUTPUT_PATH = os.path.join("outputs", "cleaned_with_county.csv")

CROSSWALK_URL = "https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv"
CROSSWALK_PATH = os.path.join("utils", "zip_county_crosswalk.csv")


def _download_crosswalk():
    """Download the ZIP-County crosswalk if it doesn't exist."""
    os.makedirs(os.path.dirname(CROSSWALK_PATH), exist_ok=True)
    if not os.path.exists(CROSSWALK_PATH):
        logger.info(f"Downloading ZIP-to-County crosswalk from {CROSSWALK_URL} ...")
        urllib.request.urlretrieve(CROSSWALK_URL, CROSSWALK_PATH)
        logger.info(f"  → Downloaded {CROSSWALK_PATH}")


def build_zip_county_lookup() -> dict:
    """
    Build a {zip_code: county_name} lookup dictionary extracting only FL counties.
    """
    _download_crosswalk()
    cw = pd.read_csv(CROSSWALK_PATH)
    
    # Filter to Florida
    fl = cw[cw["state_abbr"] == "FL"].copy()
    
    # Clean up county name (remove " County")
    fl["county"] = fl["county"].astype(str).str.replace(r"(?i)\s+County$", "", regex=True)
    fl["county"] = fl["county"].str.strip().str.upper()
    
    # Ensure ZIPs are 5-character zero-padded strings
    fl["zipcode"] = fl["zipcode"].astype(str).str.zfill(5)
    
    lookup = dict(zip(fl["zipcode"], fl["county"]))
    logger.info(f"  → Loaded {len(lookup):,} FL ZIP codes into lookup dictionary")
    return lookup


def run(
    df: pd.DataFrame = None,
    input_path: str = INPUT_PATH,
    output_path: str = OUTPUT_PATH,
    save: bool = True,
) -> pd.DataFrame:
    """
    Execute Step 2 — map PROVIDER_ZIP to COUNTY_NAME.
    """
    if df is None:
        logger.info(f"Loading cleaned data from {input_path} …")
        df = pd.read_csv(
            input_path,
            dtype={"PROVIDER_ZIP": str, "AFCARS_ID": str},
            low_memory=False,
        )

    logger.info(f"Step 2: Mapping {len(df):,} rows to FL counties …")

    lookup = build_zip_county_lookup()

    # ---- Apply mapping -------------------------------------------------------
    df = df.copy()
    # Ensure placement ZIPs are 5-character zero-padded strings
    df["_zip_clean"] = df["PROVIDER_ZIP"].astype(str).str.strip().str.zfill(5)
    df["COUNTY_NAME"] = df["_zip_clean"].map(lookup)

    # ---- Coverage stats ------------------------------------------------------
    total = len(df)
    mapped = df["COUNTY_NAME"].notna().sum()
    unmapped = total - mapped
    pct = (mapped / total * 100) if total else 0.0

    logger.info(f"  → Mapped:   {mapped:,} / {total:,}  ({pct:.1f}%)")
    logger.info(f"  → Unmapped: {unmapped:,} rows (non-FL or invalid ZIP)")
    logger.info(f"  → Unique FL counties found: {df['COUNTY_NAME'].nunique()}")

    # ---- Drop rows that couldn't be mapped -----------------------------------
    before = len(df)
    df = df.dropna(subset=["COUNTY_NAME"]).drop(columns=["_zip_clean"])
    logger.info(f"  → Dropped {before - len(df):,} unmapped rows")

    # ---- Save ----------------------------------------------------------------
    if save:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"  ✅ Saved mapped data → {output_path}")

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    run()
