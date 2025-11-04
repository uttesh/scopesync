import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np

# --- Configuration (Adjustable) ---
EXCEL_FILE = 'jira_data.xlsx'
TEXT_COLUMN = 'SUMMARY'
ID_COLUMN = 'JIRA_ID'
TEAM_COLUMN = 'TEAM'
DESCRIPTION_COLUMN = 'DESCRIPTION'
MODEL_NAME = 'all-MiniLM-L6-v2' 

# DBSCAN Hyperparameters - TUNE THESE TO FIND OVERLAPS
CLUSTER_EPS = 0.55   # Max distance (0.0 to 1.0). Use 0.55 or 0.6 for real data.
MIN_CLUSTER_SIZE = 2 # Minimum items to form a cluster.

print("--- Starting ScopeSync: Semantic Backlog Auditor ---")

# 1. Data Loading
try:
    df = pd.read_excel(EXCEL_FILE)
    texts = df[TEXT_COLUMN].tolist()
    print(f"Loaded {len(df)} Jira tickets from teams: {df[TEAM_COLUMN].nunique()}")
except FileNotFoundError:
    print(f"Error: {EXCEL_FILE} not found. Ensure it's in the same directory.")
    exit()

# 2. Generate Embeddings 
print(f"Loading local embedding model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Generating semantic embeddings (converting text to numerical vectors)...")
embeddings = model.encode(texts)

# 3. Cluster the Embeddings
print(f"Clustering embeddings using DBSCAN (eps={CLUSTER_EPS}, min_samples={MIN_CLUSTER_SIZE})...")
clustering = DBSCAN(
    eps=CLUSTER_EPS, 
    min_samples=MIN_CLUSTER_SIZE, 
    metric='cosine', 
    n_jobs=-1
)

df['CLUSTER_ID'] = clustering.fit_predict(embeddings)

# 4. Generate Human-Readable Overlap Report (Console + NEW CSV)
overlap_clusters = df[df['CLUSTER_ID'] != -1]['CLUSTER_ID'].unique()
summary_data = [] # List to hold data for the new summary CSV

if len(overlap_clusters) == 0:
    print("\n✅ ScopeSync Report: No significant semantic feature conflicts found. Backlogs appear clear.")
else:
    # Console Output (as before)
    print("\n" + "="*80)
    print("                🛑 ScopeSync: CRITICAL OVERLAP AUDIT REPORT 🛑")
    print("="*80)
    print(f"** ScopeSync found {len(overlap_clusters)} clusters of highly similar work.**")
    print("These issues are semantically redundant, posing a risk to velocity, budget, and leading to duplicate code.")
    print("-" * 80)

    for cluster_id in overlap_clusters:
        cluster_df = df[df['CLUSTER_ID'] == cluster_id].copy()
        
        # Core data points
        teams = cluster_df[TEAM_COLUMN].unique()
        jira_ids = cluster_df[ID_COLUMN].tolist()
        summaries = cluster_df[TEXT_COLUMN].tolist()
        
        is_cross_team = len(teams) > 1
        
        # Determine risk and action
        if is_cross_team:
            overlap_level = "HIGH RISK"
            action = f"COORDINATE: {', '.join(teams)} must merge or realign."
        else:
            overlap_level = "MEDIUM RISK"
            action = f"REVIEW: {', '.join(teams)} should consolidate redundant tickets."
            
        # Prepare the row for the summary CSV
        summary_data.append({
            'Cluster_ID': cluster_id,
            'Risk_Level': overlap_level,
            'Feature_Theme': cluster_df[TEXT_COLUMN].iloc[0],
            'Teams_Involved': ', '.join(teams),
            'Total_Tickets': len(cluster_df),
            'Overlapping_Jira_IDs': ', '.join(jira_ids),
            'Summary_Action': action
        })
        
        # Console Print statements (as requested, simplified)
        print(f"\n## Cluster {cluster_id} | Risk: {overlap_level}")
        print(f"**Feature Theme:** {cluster_df[TEXT_COLUMN].iloc[0]}")
        print(f"**Teams Involved:** {', '.join(teams)}")
        print(f"**Action/Risk:** {action}")
        print(f"**Overlapping Tickets:** {', '.join(jira_ids)}")
        print("-" * 35)

    # 5. Save the new Summary CSV
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('overlap_summary_report.csv', index=False)
    print("\n" + "="*80)
    print("✅ OVERLAP SUMMARY REPORT saved to **overlap_summary_report.csv** (1 row per conflict).")
    print("Raw data with individual cluster IDs saved to similarity_report_poc.csv.")

print("\n--- ScopeSync Audit Complete ---")