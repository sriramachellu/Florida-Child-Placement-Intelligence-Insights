cat("=============================================================\n")
cat("  Step 5 — Statistical Analysis of Child Placement by County\n")
cat("=============================================================\n\n")

# ---- Load data -------------------------------------------------------------
data <- read.csv("outputs/county_aggregated.csv", stringsAsFactors = FALSE)
cat("Loaded", nrow(data), "counties\n\n")

# ---- Install / load packages -----------------------------------------------
required_packages <- c("ggplot2", "corrplot")
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cran.r-project.org")
  }
  library(pkg, character.only = TRUE)
}

# ---- 1. Descriptive Statistics ---------------------------------------------
cat("=== DESCRIPTIVE STATISTICS ===\n")
cat("Children per county:\n")
print(summary(data$children_count))
cat("\nStandard Deviation:", sd(data$children_count, na.rm = TRUE), "\n")
cat("Total children across all counties:", sum(data$children_count, na.rm = TRUE), "\n")

if ("placement_count" %in% names(data)) {
  cat("\nPlacements per county:\n")
  print(summary(data$placement_count))
}

# ---- 2. Distribution Histogram ---------------------------------------------
dir.create("outputs/stats", recursive = TRUE, showWarnings = FALSE)

png("outputs/stats/histogram_children_count.png", width = 800, height = 500)
ggplot(data, aes(x = children_count)) +
  geom_histogram(bins = 15, fill = "#6366f1", color = "white", alpha = 0.9) +
  labs(
    title = "Distribution of Total Children Placed per County",
    x = "Total Children Placed",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  )
dev.off()
cat("\n✅ Saved histogram → outputs/stats/histogram_children_count.png\n")

# ---- 3. Boxplot by top maltreatment categories -----------------------------
if ("pct_physical_abuse" %in% names(data)) {
  png("outputs/stats/boxplot_maltreatment.png", width = 900, height = 500)

  malt_cols <- grep("^pct_", names(data), value = TRUE)
  malt_cols <- malt_cols[grepl("abuse|neglect|violence", malt_cols)]

  if (length(malt_cols) > 0) {
    malt_long <- stack(data[, malt_cols, drop = FALSE])
    names(malt_long) <- c("Rate", "Type")
    malt_long$Type <- tools::toTitleCase(gsub("_", " ", gsub("pct_", "", malt_long$Type)))
    malt_long$Rate <- malt_long$Rate * 100

    print(
      ggplot(malt_long, aes(x = reorder(Type, Rate, FUN = median), y = Rate)) +
        geom_boxplot(fill = "#f43f5e", alpha = 0.7) +
        coord_flip() +
        labs(title = "Maltreatment Prevalence Rates by County", x = "", y = "Prevalence Rate (%)") +
        theme_minimal(base_size = 13) +
        theme(plot.title = element_text(face = "bold"))
    )
  }
  dev.off()
  cat("✅ Saved boxplot → outputs/stats/boxplot_maltreatment.png\n")
}

# ---- 4. Linear Regression --------------------------------------------------
cat("\n=== LINEAR REGRESSION: children_count ~ maltreatment factors ===\n")

predictors <- c(
  "pct_physical_abuse", "pct_physical_neglect",
  "pct_domestic_violence", "pct_drug_abuse_parent"
)
predictors <- predictors[predictors %in% names(data)]

if (length(predictors) > 0) {
  formula_str <- paste("children_count ~", paste(predictors, collapse = " + "))
  model <- lm(as.formula(formula_str), data = data)
  print(summary(model))
} else {
  cat("(Skipped — predictor columns not found)\n")
}

# ---- 5. Correlation Matrix -------------------------------------------------
numeric_cols <- data[, sapply(data, is.numeric), drop = FALSE]
numeric_cols <- numeric_cols[, colSums(!is.na(numeric_cols)) > 2, drop = FALSE]

if (ncol(numeric_cols) >= 3) {
  # Map internal names to professional Titles
  cnames <- names(numeric_cols)
  cnames <- gsub("^pct_fl_race_", "Race ", cnames)
  cnames <- gsub("^pct_", "", cnames)
  cnames <- gsub("_", " ", cnames)
  cnames <- tools::toTitleCase(cnames)

  # Special mapping
  cnames[names(numeric_cols) == "children_count"] <- "Total Children"
  cnames[names(numeric_cols) == "placement_count"] <- "Total Placements"
  cnames[names(numeric_cols) == "avg_placement_duration"] <- "Avg Placement Duration"
  cnames[names(numeric_cols) == "avg_age_at_removal"] <- "Avg Removal Age"
  names(numeric_cols) <- cnames

  cor_matrix <- cor(numeric_cols, use = "pairwise.complete.obs")

  png("outputs/stats/correlation_matrix.png", width = 900, height = 800)
  corrplot(cor_matrix,
    method = "color",
    type = "upper",
    tl.cex = 0.65,
    tl.col = "black",
    title = "Correlation Matrix — County-Level Patterns",
    mar = c(0, 0, 2, 0)
  )
  dev.off()
  cat("\n✅ Saved correlation matrix → outputs/stats/correlation_matrix.png\n")
}

# ---- 6. Export full report to text file ------------------------------------
sink("outputs/stats/r_analysis_output.txt")
cat("================================================================\n")
cat("  STATISTICAL REPORT — Child Placement by Florida County\n")
cat("  Generated:", format(Sys.time()), "\n")
cat("================================================================\n\n")

cat("--- Descriptive Statistics (children_count) ---\n")
print(summary(data$children_count))
cat("\nSD:", sd(data$children_count, na.rm = TRUE), "\n")

if (length(predictors) > 0) {
  cat("\n--- Regression Model ---\n")
  print(summary(model))
}

if (ncol(numeric_cols) >= 3) {
  cat("\n--- Correlation Matrix ---\n")
  print(round(cor_matrix, 3))
}

cat("\n--- Top 10 Counties by Children Count ---\n")
top10 <- head(data[order(-data$children_count), c("COUNTY_NAME", "children_count")], 10)
print(top10, row.names = FALSE)

sink()
cat("\n✅ Saved full report → outputs/stats/r_analysis_output.txt\n")
cat("\n🎉 Step 5 complete!\n")
