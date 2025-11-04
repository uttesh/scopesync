import pandas as pd
from sentence_transformers import SentenceTransformer
# --- Vector Database Imports ---
import chromadb 
from chromadb.utils import embedding_functions 
# -----------------------------

# --- Configuration (Adjustable) ---
EXCEL_FILE = 'jira_data.xlsx'
TEXT_COLUMN = 'SUMMARY'        # Column used for semantic analysis
ID_COLUMN = 'JIRA_ID'
TEAM_COLUMN = 'TEAM'
DESCRIPTION_COLUMN = 'DESCRIPTION' # Column for context snippet
MODEL_NAME = 'all-MiniLM-L6-v2' 

# --- Similarity Threshold ---
# This defines how close (semantically) two tickets must be to count as an overlap.
# 0.45 distance is equivalent to 0.55 similarity (1 - 0.45).
MAX_DISTANCE_THRESHOLD = 0.45 
MIN_SIMILARITY_THRESHOLD = 1 - MAX_DISTANCE_THRESHOLD

# --- Simulation Data ---
NEW_TICKET_SUMMARY = "Implement the ability for customers to modify their personal details in the portal."
NEW_TICKET_ID = "PROJ-999"
NEW_TICKET_TEAM = "Team Nova"
# -----------------------------

print("--- Starting ScopeSync: Real-Time Vector Database POC ---")

# 1. Data Loading
try:
    df = pd.read_excel(EXCEL_FILE)
    print(f"Loaded {len(df)} existing Jira tickets from teams: {df[TEAM_COLUMN].nunique()}")
except FileNotFoundError:
    print(f"Error: {EXCEL_FILE} not found. Ensure it's in the same directory.")
    exit()

# 2. Setup Vector Database and Model
# Initialize ChromaDB Client (using default file storage for persistence)
#client = chromadb.Client() 
client = chromadb.PersistentClient(path="./chroma_data")
collection_name = "jira_backlog_v1"

# Define the embedding function using Sentence-Transformers (LLM)
print(f"Loading local embedding model: {MODEL_NAME}...")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

# Get or create the collection
collection = client.get_or_create_collection(
    name=collection_name, 
    embedding_function=emb_fn
)
print(f"ChromaDB collection '{collection_name}' ready.")

# 3. Indexing Data (Initial Population of the Vector Database)
print("Indexing existing Jira tickets into the Vector Database...")

# Prepare data for ChromaDB ingestion
ids = df[ID_COLUMN].astype(str).tolist()
documents = df[TEXT_COLUMN].tolist()
# Metadatas are used for filtering and retrieving context
metadatas = df[[TEAM_COLUMN, DESCRIPTION_COLUMN]].to_dict('records')

# Add all data points to the collection
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print(f"Successfully indexed {len(ids)} Jira tickets.")
print("-" * 50)

# 4. Real-Time Overlap Detection (Simulating a new ticket being created)
print(f"Simulating creation of new ticket: {NEW_TICKET_ID} (Team: {NEW_TICKET_TEAM})")
print(f"New Summary: {NEW_TICKET_SUMMARY}")

# The search query automatically gets embedded by the 'emb_fn'
results = collection.query(
    query_texts=[NEW_TICKET_SUMMARY],
    n_results=10,  # Retrieve the top 10 most similar tickets
    # We can add metadata filtering here, e.g., to exclude specific statuses
    # where={'TEAM': {'$ne': NEW_TICKET_TEAM}} # Uncomment to filter out the new ticket's own team
)

# 5. Analyze and Report the Overlap
print("\n--- ScopeSync Real-Time Overlap Audit ---")

if results['ids'] and results['distances']:
    
    overlapping_issues = []
    
    for i, jira_id in enumerate(results['ids'][0]):
        distance = results['distances'][0][i]
        
        # Apply the similarity threshold for a confirmed overlap
        if distance <= MAX_DISTANCE_THRESHOLD:
            # Retrieve the full metadata for the hit
            metadata = results['metadatas'][0][i]
            summary = results['documents'][0][i]
            
            # Format the description snippet
            description = metadata[DESCRIPTION_COLUMN]
            snippet = description.split('.')[0].strip() + '...' if pd.notna(description) else 'No Description available.'
            
            overlapping_issues.append({
                'ID': jira_id,
                'Team': metadata[TEAM_COLUMN],
                'Summary': summary,
                'Similarity': 1 - distance,
                'Context': snippet
            })

    if overlapping_issues:
        print("\n" + "="*80)
        print(f"🛑 CRITICAL OVERLAP DETECTED (Similarity >= {MIN_SIMILARITY_THRESHOLD:.2f})!")
        print(f"New Ticket **{NEW_TICKET_ID}** by **{NEW_TICKET_TEAM}** is highly similar to:")
        print("="*80)
        
        # Check for cross-team conflict in the results
        involved_teams = {issue['Team'] for issue in overlapping_issues}
        is_cross_team = NEW_TICKET_TEAM not in involved_teams or len(involved_teams) > 1
        
        if is_cross_team:
            print(f"ACTION: **Cross-Team Conflict** with {', '.join(involved_teams)}.")
        else:
            print(f"ACTION: **Internal Redundancy** within {NEW_TICKET_TEAM}.")

        print("-" * 80)
        
        for issue in overlapping_issues:
            print(f"  - **{issue['ID']}** (Team: **{issue['Team']}**)")
            print(f"    - **Similarity Score:** {issue['Similarity']:.3f}")
            print(f"    - **Existing Summary:** {issue['Summary']}")
            print(f"    - **Existing Context:** {issue['Context']}")
        
        print("-" * 80)
    else:
        print(f"\n✅ No high-similarity overlap (>{MIN_SIMILARITY_THRESHOLD:.2f}) found for {NEW_TICKET_ID} in the existing backlog.")
else:
    print("\nNo search results returned.")

print("\n--- POC Complete ---")