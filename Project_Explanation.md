# Florida Child Placement Intelligence Insights
**Geospatial & Statistical Analysis of Child Placement Patterns**

## Executive Summary
This project analyzes child placement data within Florida by integrating large-scale datasets from the Department of Children and Families (DCF). The goal is to surface actionable intelligence regarding placement durations, child demographics, physical abuse prevalence, and geographical hotspots to assist stakeholders in making informed, data-driven decisions.

## Objectives
1. **Data Unification:** Merge complex DCF placement histories with demographic profiles to build a comprehensive foundation for analysis.
2. **Geospatial Mapping:** Translate raw zip code metrics into high-resolution county-level insights using programmatic GIS mapping techniques, producing visual choropleth hotspots for at-risk areas.
3. **Statistical & ML Analysis:** Uncover correlations between abuse factors and placement counts (via R-based linear models) and use Random Forest classification to predict critical factors driving placement durations.
4. **Actionable BI:** Output clean dimension tables for direct consumption in an interactive Power BI dashboard featuring dynamic filtering, KPI tracking, and geographic visualization.

## Technical Architecture
- **Data Engineering (Python/Pandas):** Implements robust cleaning, validation, date parsing, and robust crosswalks to correctly assign placements geographically.
- **Geospatial Processing (GeoPandas/Matplotlib):** Reads raw Florida shapefiles and mathematically intersections them with placement metrics to generate publication-ready visual assets.
- **Statistical Modeling (R):** Deployed for formal hypothesis testing and correlation calculations across high-variance datasets.
- **Machine Learning (Scikit-Learn):** Predicts long vs. short-term placement risks, analyzing feature importance (such as physical abuse or demographic impacts) to extract critical systemic trends. 
- **AI Persona Clustering (K-Means):** Groups counties into distinct actionable profiles (e.g., "High Volume / Severe Risk" vs "Low Volume / Stable"), allowing tailored intervention strategies.

## Outcomes
The automated, 8-step reproducible pipeline effectively converts million-row raw records into optimized BI intelligence, supporting immediate consumption in tools like Power BI and providing continuous, evolving insights into child placement dynamics across Florida.
