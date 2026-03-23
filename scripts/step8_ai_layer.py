import os
import logging
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join("outputs", "county_aggregated.csv")
AI_DIR = os.path.join("outputs", "ai_insights")

# Predictor features for finding behavioral clusters
FEATURES = [
    "pct_physical_abuse", "pct_physical_neglect", "pct_drug_abuse_parent", 
    "avg_placement_duration", "pct_domestic_violence", "pct_fl_race_black"
]

def run(df=None, save=True):
    if df is None:
        df = pd.read_csv(INPUT_PATH)

    os.makedirs(AI_DIR, exist_ok=True)
    
    # 1. Prepare Data
    cols = [c for c in FEATURES if c in df.columns]
    X_raw = df[cols].fillna(0)
    
    # Scale data for KMeans
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 2. Train AI Clustering Model (K=3 Personas)
    logger.info("Training Unsupervised AI Clustering Model...")
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["AI_Cluster_ID"] = kmeans.fit_predict(X_scaled)
    
    # Map raw cluster IDs to Semantic Archetypes
    # We find which cluster has the highest drug abuse, etc.
    centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=cols)
    
    archetypes = {}
    for i in range(3):
        profile = "Standard Profile"
        if centroids.loc[i, "pct_drug_abuse_parent"] > centroids["pct_drug_abuse_parent"].median() * 1.2:
            profile = "High Substance Abuse Risk"
        elif centroids.loc[i, "pct_physical_neglect"] > centroids["pct_physical_neglect"].median() * 1.2:
            profile = "High Neglect & Poverty Risk"
        elif "avg_placement_duration" in centroids.columns and centroids.loc[i, "avg_placement_duration"] > centroids["avg_placement_duration"].median() * 1.2:
            profile = "Chronic Long-Term Care"
        archetypes[i] = profile

    df["AI_Archetype"] = df["AI_Cluster_ID"].map(archetypes)
    
    logger.info(f"AI Discovered Personas:")
    for arch, count in df["AI_Archetype"].value_counts().items():
        logger.info(f"  - {arch}: {count} counties")

    # 3. Generate Visual AI Insight
    if len(cols) >= 2:
        fig, ax = plt.subplots(figsize=(8, 6), facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        
        scatter = ax.scatter(X_raw.iloc[:, 0], X_raw.iloc[:, 1], c=df["AI_Cluster_ID"], cmap="cool", s=100, alpha=0.8, edgecolors="white")
        ax.set_xlabel(cols[0].replace("pct_", "").replace("_", " ").title() + " (%)", color="white", fontsize=11)
        ax.set_ylabel(cols[1].replace("pct_", "").replace("_", " ").title() + " (%)", color="white", fontsize=11)
        ax.set_title("AI Automated County Clustering", color="white", fontsize=14, fontweight="bold")
        ax.tick_params(colors="white")
        
        plot_path = os.path.join(AI_DIR, "ai_cluster_scatter.png")
        plt.savefig(plot_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info(f"  📈 Saved AI Insight Plot -> {plot_path}")

    # 4. Save enhanced CSV
    if save:
        out_csv = os.path.join(AI_DIR, "county_ai_personas.csv")
        df.to_csv(out_csv, index=False)
        logger.info(f"  ✅ Saved AI Enhanced Dataset -> {out_csv}")
    
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
