# 📋 Product Requirements Document (PRD)

## Geospatial and Statistical Analysis of Child Placement Patterns in Florida

| Field | Detail |
|---|---|
| **Project Title** | Geospatial and Statistical Analysis of Child Placement Patterns in Florida |
| **Author** | Sriram |
| **Date** | March 17, 2026 |
| **Version** | 1.0 |
| **Status** | Draft |

---

## 1. Executive Summary

This project analyzes **foster-care child placement data** published by the Florida Department of Children and Families (DCF) to reveal county-level geographic patterns, demographic disparities, and risk factors associated with child maltreatment and placement instability. The analysis combines **Python-based geospatial mapping**, **R-based statistical modeling**, and **machine-learning classification** to produce actionable insights and interactive visualizations.

---

## 2. Problem Statement

Florida's child welfare system processes hundreds of thousands of placement episodes across 67 counties. Understanding **where** children are placed, **why** they enter care, and **which counties bear disproportionate caseloads** is critical for resource allocation, policy reform, and intervention targeting. Currently, this data exists as raw CSV extracts with no spatial or analytical layer applied.

---

## 3. Objectives

| # | Objective | Success Metric |
|---|---|---|
| O-1 | Clean and prepare the 523 MB placement-history dataset for analysis | Zero critical nulls in join keys (`AFCARS_ID`, `PROVIDER_ZIP`) |
| O-2 | Map provider ZIP codes to Florida counties | ≥ 95 % of records successfully mapped |
| O-3 | Produce county-level choropleth maps of child placement density | All 67 FL counties rendered with correct counts |
| O-4 | Perform statistical analysis of placement counts and maltreatment types | Summary statistics, distribution analysis, regression model produced |
| O-5 | Build a basic ML classifier for high-risk county identification | Model trained; accuracy, precision, recall reported |
| O-6 | Create a dashboard-ready visualization package | Exportable charts / maps suitable for Power BI integration |

---

## 4. Data Sources

### 4.1 Child Placement Dataset

| File | Size | Records (approx.) | Key Fields |
|---|---|---|---|
| `DCF_placement_history.csv` | 523 MB | ~2.5M placement episodes | `AFCARS_ID`, `PROVIDER_ZIP`, `PLACEMENT_BEGIN_DATE`, `PLACEMENT_END_DATE`, `LEAD_AGENCY`, 30 maltreatment flags |
| `child_demographics.csv` | 32 MB | ~310,665 unique children | `AFCARS_ID`, `Gender`, `DOB`, race/ethnicity flags, `Hispanic` |

> **Source**: University of Miami Libraries — DOI: [10.17604/y25q-ea68](https://doi.org/10.17604/y25q-ea68)  
> **License**: Open Data Commons Attribution (ODC-By) v1.0

### 4.2 Florida Counties Shapefile

| File | Records | Key Fields |
|---|---|---|
| `Counties/Counties.shp` | 245 features | `OBJECTID`, `TYPE`, `TYPE_DESC`, geometry |
| `Counties_-_Detailed_Shoreline/` | Alternate high-res version | Same schema |

> **Note**: The shapefile contains 245 features (multi-part polygons for 67 counties). A `COUNTYNAME` or equivalent field will be confirmed during Step 1.

---

## 5. Scope

### 5.1 In Scope (MVP)

| Feature | Description |
|---|---|
| **Data Cleaning** | Handle nulls, standardize dates, validate ZIP codes |
| **ZIP → County Mapping** | Crosswalk `PROVIDER_ZIP` to county names using ZCTA lookup or spatial join |
| **County Aggregation** | Children per county, placements per county, maltreatment-type breakdowns |
| **Choropleth Mapping** | Static maps using GeoPandas + Matplotlib |
| **Statistical Summary (R)** | Descriptive statistics, distribution fitting, linear regression |
| **ML Classification (Python)** | Random Forest classifier for high-risk vs. low-risk counties |
| **Exported Outputs** | CSV aggregates, PNG/SVG maps, model metrics report |

### 5.2 Out of Scope (Future Phases)

| Feature | Notes |
|---|---|
| ArcGIS Pro integration | Can reference familiarity; deep integration deferred |
| Interactive web dashboards | Power BI / Tableau layer is post-analysis |
| Longitudinal / time-series analysis | Could be Phase 2 |
| Provider-level network analysis | Requires additional provider relationship data |

---

## 6. User Stories

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US-1 | Policy Analyst | See which counties have the highest child-placement density | I can prioritize resource allocation |
| US-2 | Researcher | Understand demographic disparities in placement patterns | I can publish findings on equity |
| US-3 | Social Work Director | Identify high-risk counties using ML | I can deploy prevention programs proactively |
| US-4 | Stakeholder | View a clear choropleth map of Florida | I can quickly grasp geographic patterns |

---

## 7. Functional Requirements

### FR-1: Data Ingestion & Cleaning
- Load `DCF_placement_history.csv` and `child_demographics.csv`
- Join on `AFCARS_ID`
- Drop records with null `PROVIDER_ZIP`
- Parse date columns to `datetime`
- Standardize ZIP codes to 5-digit format

### FR-2: ZIP-to-County Mapping
- Use a **ZIP → County crosswalk table** (HUD USPS or Census ZCTA)
- Fallback: spatial join of ZIP centroids against county polygons
- Output: new column `COUNTY_NAME` on every placement record

### FR-3: Aggregation
- Count unique children per county
- Count total placement episodes per county
- Compute maltreatment-flag prevalence per county (e.g., `% PHYSICAL_ABUSE`)
- Compute demographic breakdowns per county (race, gender, age-at-removal)

### FR-4: Geospatial Visualization
- Merge aggregated data with `Counties.shp` on county name/ID
- Generate choropleth maps for:
  - Total children placed
  - Maltreatment prevalence (heatmap)
  - Demographic distribution
- Export as PNG / SVG

### FR-5: Statistical Analysis (R)
- Descriptive statistics (`summary()`, histograms)
- Distribution analysis of `children_count` per county
- Simple linear regression model
- Correlation matrix across maltreatment types

### FR-6: Machine Learning Classification
- Binary target: `high_risk = 1` if county placement count > median
- Features: placement counts, maltreatment rates, demographic proportions
- Model: Random Forest Classifier
- Output: accuracy, precision, recall, feature importance chart

### FR-7: Export & Reporting
- Aggregated county-level CSV for Power BI
- Map images (PNG/SVG)
- Model performance summary (text/markdown)

---

## 8. Non-Functional Requirements

| Requirement | Detail |
|---|---|
| **Performance** | All scripts must complete on a standard laptop (16 GB RAM) within 30 minutes |
| **Reproducibility** | All steps scripted; no manual Excel operations |
| **Data Privacy** | Dataset is already anonymized (AFCARS_ID). No PII is present |
| **Portability** | Python scripts runnable via `pip install` dependencies; R scripts via standard CRAN packages |

---

## 9. Deliverables

| # | Deliverable | Format |
|---|---|---|
| D-1 | Cleaned & merged dataset | CSV |
| D-2 | County-aggregated dataset | CSV |
| D-3 | Choropleth maps | PNG / SVG |
| D-4 | R statistical report | R script + output |
| D-5 | ML model metrics | Python notebook / script |
| D-6 | Final project summary | Markdown / PDF |

---

## 10. Milestones

| Phase | Milestone | Target |
|---|---|---|
| **Step 1** | Data cleaned, merged, ZIP validated | Week 1 |
| **Step 2** | ZIP → County mapping complete | Week 1 |
| **Step 3** | County aggregation complete | Week 1 |
| **Step 4** | Choropleth maps generated | Week 2 |
| **Step 5** | R statistical analysis complete | Week 2 |
| **Step 6** | ML classification trained & evaluated | Week 3 |
| **Step 7** | Power BI-ready exports delivered | Week 3 |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `PROVIDER_ZIP` has high null rate | Many records unmapped | Use `LEAD_AGENCY` as backup geographic proxy |
| ZIP spans multiple counties | Incorrect county assignment | Use population-weighted ZCTA crosswalk |
| Shapefile county names don't match data | Join failures | Normalize names; manual review of 67 counties |
| 523 MB file causes memory issues | Script crashes | Process in chunks via `pandas.read_csv(chunksize=)` |

---

## 12. ArcGIS Integration Statement

> *"The geospatial analysis was performed using Python (GeoPandas) for choropleth mapping and spatial joins. The workflow is designed to be portable to ArcGIS Pro for advanced cartography, spatial statistics (Hot Spot Analysis, Spatial Autocorrelation), and enterprise geodatabase integration."*

---

## 13. References

- Latham, R. (2022). *Child Placement Administrative Data from Florida DCF SACWIS*. University of Miami Libraries. DOI: [10.17604/y25q-ea68](https://doi.org/10.17604/y25q-ea68)
- Florida Department of Children and Families — [myflfamilies.com](https://www.myflfamilies.com)
- HUD USPS ZIP Code Crosswalk — [huduser.gov](https://www.huduser.gov/portal/datasets/usps_crosswalk.html)
