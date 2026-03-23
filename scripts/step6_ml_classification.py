import os
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join("outputs", "county_aggregated.csv")
ML_DIR = os.path.join("outputs", "ml")

# Feature columns to use (will skip any that don't exist in the data)
CANDIDATE_FEATURES = [
    "placement_count",
    "avg_placement_duration",
    "avg_age_at_removal",
    "pct_physical_abuse",
    "pct_sexual_abuse",
    "pct_physical_neglect",
    "pct_domestic_violence",
    "pct_drug_abuse_parent",
    "pct_alcohol_abuse_parent",
    "pct_inadequate_housing",
    "pct_inadequate_supervision",
    "pct_abandonment",
    "pct_fl_race_black",
    "pct_fl_race_white",
    "pct_hispanic",
    "pct_male",
]


def _prepare_data(df: pd.DataFrame):
    """Select features, create target, return X, y, feature_names."""
    # Target: above-median children count = high risk
    median_val = df["children_count"].median()
    df = df.copy()
    df["high_risk"] = (df["children_count"] > median_val).astype(int)

    # Select available features
    features = [c for c in CANDIDATE_FEATURES if c in df.columns]
    if not features:
        raise ValueError("No feature columns found in the data.")

    X = df[features].fillna(0).values
    y = df["high_risk"].values
    return X, y, features, median_val


def run(
    df: pd.DataFrame = None,
    input_path: str = INPUT_PATH,
    save: bool = True,
) -> dict:
    """
    Execute Step 6 — train and evaluate Random Forest classifier.

    Returns
    -------
    dict with keys: model, report, feature_importance, threshold
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import (
        cross_val_score,
        StratifiedKFold,
        train_test_split,
    )
    from sklearn.metrics import (
        classification_report,
        confusion_matrix,
        ConfusionMatrixDisplay,
    )

    if df is None:
        df = pd.read_csv(input_path)

    X, y, features, median_val = _prepare_data(df)
    logger.info(f"Features ({len(features)}): {features}")
    logger.info(f"Samples: {len(y)}  |  High-risk: {y.sum()}  |  Low-risk: {(1-y).sum()}")
    logger.info(f"Median threshold: {median_val}")

    # ---- Train / test split --------------------------------------------------
    if len(y) >= 20:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y,
        )
    else:
        # With only 67 counties, use all data + cross-validation
        X_train, X_test, y_train, y_test = X, X, y, y
        logger.info("  ℹ️  Small dataset — using full data with cross-validation")

    # ---- Model training ------------------------------------------------------
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_split=3,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    # ---- Evaluation ----------------------------------------------------------
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"])
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\n{report}")

    # Cross-validation
    cv = StratifiedKFold(n_splits=min(5, len(y) // 2), shuffle=True, random_state=42)
    cv_scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    cv_text = f"CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}"
    logger.info(f"  {cv_text}")

    os.makedirs(ML_DIR, exist_ok=True)

    # ---- Feature Importance Plot ---------------------------------------------
    importances = pd.Series(clf.feature_importances_, index=features).sort_values()

    fig, ax = plt.subplots(figsize=(10, max(6, len(features) * 0.4)), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    bars = ax.barh(range(len(importances)), importances.values, color="#6366f1", edgecolor="#818cf8")
    ax.set_yticks(range(len(importances)))

    friendly_map = {
        "placement_count": "Total Placements",
        "avg_placement_duration": "Avg Placement Duration (Days)",
        "avg_age_at_removal": "Average Age at Removal",
    }
    
    def _clean_name(name):
        if name in friendly_map:
            return friendly_map[name]
        return name.replace("pct_fl_race_", "Race ").replace("pct_", "").replace("_", " ").title() + " (%)"

    ax.set_yticklabels([_clean_name(f) for f in importances.index],
                       color="white", fontsize=11)
    ax.set_xlabel("Relative Importance", color="white", fontsize=12)
    ax.set_title("Feature Importance — High-Risk County Classification",
                 color="white", fontsize=14, fontweight="bold", pad=12)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("#2d2d44")

    fi_path = os.path.join(ML_DIR, "feature_importance.png")
    plt.savefig(fi_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"  📊 Saved {fi_path}")

    # ---- Confusion Matrix Plot -----------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    disp = ConfusionMatrixDisplay(cm, display_labels=["Low Risk", "High Risk"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion Matrix: High-Risk County Prediction", color="white", fontsize=14, fontweight="bold")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(colors="white")

    cm_path = os.path.join(ML_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"  📊 Saved {cm_path}")

    # ---- Save Metrics --------------------------------------------------------
    if save:
        metrics_path = os.path.join(ML_DIR, "model_metrics.txt")
        with open(metrics_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("  RANDOM FOREST CLASSIFICATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(report)
            f.write(f"\n{cv_text}\n")
            f.write(f"\nMedian Threshold: {median_val}\n")
            f.write(f"Training samples: {len(y_train)}\n")
            f.write(f"Test samples:     {len(y_test)}\n")
            f.write(f"\nFeatures used:\n")
            for feat, imp in importances.items():
                f.write(f"  {feat:40s} {imp:.4f}\n")
            f.write(f"\nConfusion Matrix:\n{cm}\n")
        logger.info(f"  ✅ Saved {metrics_path}")

    # ---- County-level predictions -------------------------------------------
    df = df.copy()
    df["predicted_risk"] = clf.predict(_prepare_data(df)[0])
    df["risk_label"] = df["predicted_risk"].map({0: "Low Risk", 1: "High Risk"})

    if save:
        risk_path = os.path.join(ML_DIR, "county_risk_predictions.csv")
        df[["COUNTY_NAME", "children_count", "risk_label"]].to_csv(risk_path, index=False)
        logger.info(f"  ✅ Saved {risk_path}")

    return {
        "model": clf,
        "report": report,
        "cv_scores": cv_scores,
        "feature_importance": importances,
        "threshold": median_val,
        "predictions": df,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
