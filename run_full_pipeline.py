import os
import subprocess
import shutil

scripts = [
    ["python", "scripts/step1_data_cleaning.py"],
    ["python", "scripts/step2_zip_to_county.py"],
    ["python", "scripts/step3_aggregation.py"],
    ["python", "scripts/step4_gis_mapping.py"],
    [r"C:\Program Files\R\R-4.5.3\bin\Rscript.exe", "scripts/step5_statistical_analysis.R"],
    ["python", "scripts/step6_ml_classification.py"],
    ["python", "scripts/step7_powerbi_export.py"],
    ["python", "scripts/step8_ai_layer.py"]
]

for cmd in scripts:
    print(f"\n====================================")
    print(f"Running: {' '.join(cmd)}")
    print(f"====================================")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"❌ Failed at {cmd}")
        exit(1)

# Copy the generated artifacts to the interface brain directory
files = [
    # Maps
    ('choropleth_children_count.png', 'outputs/maps'),
    ('choropleth_demographics.png', 'outputs/maps'),
    ('choropleth_duration.png', 'outputs/maps'),
    ('choropleth_maltreatment.png', 'outputs/maps'),
    
    # R Stats
    ('r_analysis_output.txt', 'outputs/stats'),
    ('correlation_matrix.png', 'outputs/stats'),
    ('boxplot_maltreatment.png', 'outputs/stats'),
    
    # ML
    ('feature_importance.png', 'outputs/ml'),
    ('confusion_matrix.png', 'outputs/ml'),
    
    # PowerBI
    ('County_Stats_Dim.csv', 'outputs/powerbi'),
    
    # AI Layer
    ('ai_cluster_scatter.png', 'outputs/ai_insights'),
    ('county_ai_personas.csv', 'outputs/ai_insights')
]

dst_dir = r'C:\Users\srira\.gemini\antigravity\brain\1dcd5cdc-c711-4ec0-878d-284eefba4d62'
for f, subdir in files:
    src = os.path.join(subdir, f)
    dst = os.path.join(dst_dir, f)
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f'✅ Copied artifact: {f}')
    else:
        print(f'⚠️ Missing artifact: {f} (Checked {src})')

print("\n🎉 ALL PIPELINE STEPS COMPLETED!")
