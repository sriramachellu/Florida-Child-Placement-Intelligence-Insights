import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join("outputs", "cleaned_with_county.csv")
OUTPUT_PATH = os.path.join("outputs", "county_aggregated.csv")

# Maltreatment flag columns (Y/N)
MALTREATMENT_FLAGS = [
    "PHYSICAL_ABUSE", "SEXUAL_ABUSE", "EMOTIONAL_ABUSE_NEGLECT",
    "ALCOHOL_ABUSE_CHILD", "DRUG_ABUSE_CHILD",
    "ALCOHOL_ABUSE_PARENT", "DRUG_ABUSE_PARENT",
    "PHYSICAL_NEGLECT", "DOMESTIC_VIOLENCE", "INADEQUATE_HOUSING",
    "CHILD_BEHAVIOR_PROBLEM", "CHILD_DISABILITY",
    "INCARCERATION_OF_PARENT", "DEATH_OF_PARENT",
    "CAREGIVER_INABILITY_TO_COPE", "ABANDONMENT",
    "INADEQUATE_SUPERVISION", "MEDICAL_NEGLECT",
    "CSEC", "LABOR_TRAFFICKING", "SEXUAL_ABUSE_SEXUAL_EXPLOITATION",
]

# Race flag columns (Y/N)
RACE_FLAGS = [
    "FL_RACE_BLACK", "FL_RACE_WHITE", "FL_RACE_ASIAN",
    "FL_RACE_AMERICAN", "FL_RACE_HAWAIIAN", "FL_MULTI_RCL",
]


def _yn_mean(series: pd.Series) -> float:
    """Compute mean of a Y/N flag column (percentage as 0–1)."""
    return (series.astype(str).str.upper() == "Y").mean()


def run(
    df: pd.DataFrame = None,
    input_path: str = INPUT_PATH,
    output_path: str = OUTPUT_PATH,
    save: bool = True,
) -> pd.DataFrame:
    """
    Execute Step 3 — aggregate to county level.

    Returns
    -------
    pd.DataFrame  with one row per county.
    """
    if df is None:
        logger.info(f"Loading mapped data from {input_path} …")
        df = pd.read_csv(input_path, dtype={"PROVIDER_ZIP": str, "AFCARS_ID": str}, low_memory=False)

    logger.info(f"Aggregating {len(df):,} rows to county level …")

    # ---- Core counts ---------------------------------------------------------
    agg_dict = {
        "AFCARS_ID": [
            ("children_count", "nunique"),
            ("placement_count", "size"),
        ],
    }

    core = df.groupby("COUNTY_NAME").agg(
        children_count=("AFCARS_ID", "nunique"),
        placement_count=("AFCARS_ID", "size"),
    ).reset_index()

    # ---- Duration & age stats ------------------------------------------------
    if "PLACEMENT_DURATION_DAYS" in df.columns:
        dur = df.groupby("COUNTY_NAME")["PLACEMENT_DURATION_DAYS"].mean().reset_index()
        dur.columns = ["COUNTY_NAME", "avg_placement_duration"]
        core = core.merge(dur, on="COUNTY_NAME", how="left")

    if "AGE_AT_REMOVAL" in df.columns:
        age = df.groupby("COUNTY_NAME")["AGE_AT_REMOVAL"].mean().reset_index()
        age.columns = ["COUNTY_NAME", "avg_age_at_removal"]
        core = core.merge(age, on="COUNTY_NAME", how="left")

    # ---- Maltreatment prevalence (% of placements with flag = Y) -------------
    for flag in MALTREATMENT_FLAGS:
        if flag in df.columns:
            col_name = f"pct_{flag.lower()}"
            rates = df.groupby("COUNTY_NAME")[flag].apply(_yn_mean).reset_index()
            rates.columns = ["COUNTY_NAME", col_name]
            core = core.merge(rates, on="COUNTY_NAME", how="left")

    # ---- Demographic proportions ---------------------------------------------
    for flag in RACE_FLAGS:
        if flag in df.columns:
            col_name = f"pct_{flag.lower()}"
            rates = df.groupby("COUNTY_NAME")[flag].apply(_yn_mean).reset_index()
            rates.columns = ["COUNTY_NAME", col_name]
            core = core.merge(rates, on="COUNTY_NAME", how="left")

    # Hispanic may be "Yes"/"No" rather than Y/N
    if "Hispanic" in df.columns:
        h = df.groupby("COUNTY_NAME")["Hispanic"].apply(
            lambda s: (s.astype(str).str.lower().isin(["y", "yes"])).mean()
        ).reset_index()
        h.columns = ["COUNTY_NAME", "pct_hispanic"]
        core = core.merge(h, on="COUNTY_NAME", how="left")

    # Gender split
    if "Gender" in df.columns:
        g = df.groupby("COUNTY_NAME")["Gender"].apply(
            lambda s: (s.astype(str).str.upper() == "MALE").mean()
        ).reset_index()
        g.columns = ["COUNTY_NAME", "pct_male"]
        core = core.merge(g, on="COUNTY_NAME", how="left")

    logger.info(f"  → {len(core)} counties aggregated, {len(core.columns)} columns")

    # ---- Save ----------------------------------------------------------------
    if save:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        core.to_csv(output_path, index=False)
        logger.info(f"  ✅ Saved aggregated data → {output_path}")

    return core


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
