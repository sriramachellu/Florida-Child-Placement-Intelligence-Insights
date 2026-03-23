import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------
PLACEMENT_PATH = os.path.join("Child Placement Dataset", "DCF_placement_history.csv")
DEMOGRAPHICS_PATH = os.path.join("Child Placement Dataset", "child_demographics.csv")
OUTPUT_PATH = os.path.join("outputs", "cleaned_merged_data.csv")


DATE_COLS_PLACEMENT = [
    "REMOVAL_DATE",
    "PLACEMENT_BEGIN_DATE",
    "PLACEMENT_END_DATE",
    "DISCHARGE_DATE",
]


def _parse_dates(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Convert date columns using pd.to_datetime (extracts YYYY-MM-DD from raw)."""
    for col in cols:
        if col in df.columns:
            # The raw data has formats like 2005-02-09-00.01.00.000000
            df[col] = pd.to_datetime(df[col].astype(str).str[:10], errors="coerce")
    return df


def load_placement(path: str = PLACEMENT_PATH) -> pd.DataFrame:
    """Load placement history with controlled dtypes."""
    logger.info("Loading placement history …")
    df = pd.read_csv(
        path,
        dtype={"PROVIDER_ZIP": str, "AFCARS_ID": str, "PROVIDER_ID": str},
        low_memory=False,
    )
    df = _parse_dates(df, DATE_COLS_PLACEMENT)
    logger.info(f"  → {len(df):,} placement rows loaded")
    return df


def load_demographics(path: str = DEMOGRAPHICS_PATH) -> pd.DataFrame:
    """Load child demographics."""
    logger.info("Loading child demographics …")
    df = pd.read_csv(
        path,
        dtype={"AFCARS_ID": str},
    )
    df = _parse_dates(df, ["DOB"])
    logger.info(f"  → {len(df):,} demographic rows loaded")
    return df


def clean_zip(series: pd.Series) -> pd.Series:
    """Standardize ZIP codes to 5-digit strings and drop invalid."""
    s = series.astype(str).str.strip().str[:5]
    s = s.where(s.str.match(r"^\d{5}$"), other=pd.NA)
    return s


def run(
    placement_path: str = PLACEMENT_PATH,
    demographics_path: str = DEMOGRAPHICS_PATH,
    output_path: str = OUTPUT_PATH,
    save: bool = True,
) -> pd.DataFrame:
    """
    Execute Step 1 — full data-cleaning pipeline.

    Returns
    -------
    pd.DataFrame
        Merged and cleaned DataFrame.
    """
    # ---- Load ---------------------------------------------------------------
    placement = load_placement(placement_path)
    demographics = load_demographics(demographics_path)

    # ---- Clean ZIP ----------------------------------------------------------
    before = len(placement)
    placement["PROVIDER_ZIP"] = clean_zip(placement["PROVIDER_ZIP"])
    placement = placement.dropna(subset=["PROVIDER_ZIP"])
    logger.info(
        f"  → Dropped {before - len(placement):,} rows with invalid/missing ZIP"
    )

    # ---- Drop rows missing AFCARS_ID ----------------------------------------
    placement = placement.dropna(subset=["AFCARS_ID"])
    demographics = demographics.dropna(subset=["AFCARS_ID"])

    # ---- Merge ---------------------------------------------------------------
    logger.info("Merging placement + demographics on AFCARS_ID …")
    merged = placement.merge(demographics, on="AFCARS_ID", how="left")
    logger.info(f"  → {len(merged):,} rows after merge")

    # ---- Derived columns -----------------------------------------------------
    merged["AGE_AT_REMOVAL"] = (
        (merged["REMOVAL_DATE"] - merged["DOB"]).dt.days / 365.25
    ).round(1)

    merged["PLACEMENT_DURATION_DAYS"] = (
        merged["PLACEMENT_END_DATE"] - merged["PLACEMENT_BEGIN_DATE"]
    ).dt.days

    # ---- Save ---------------------------------------------------------------
    if save:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        merged.to_csv(output_path, index=False)
        logger.info(f"  ✅ Saved cleaned data → {output_path}")

    return merged


# ---------------------------------------------------------------------------
# Allow direct execution: python scripts/step1_data_cleaning.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
