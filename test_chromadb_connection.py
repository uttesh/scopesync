import chromadb

# --- Configuration ---
COLLECTION_NAME = "jira_backlog_v1"
TEAM_METADATA_KEY = 'TEAM' # Key used in the metadata dictionary
DESCRIPTION_METADATA_KEY = 'DESCRIPTION'
# ---------------------

def test_connection_and_retrieve_all_records():
    """
    Connects to the local ChromaDB client, retrieves all records from the 
    jira_backlog_v1 collection, and prints them in a readable format.
    """
    print("--- Starting ChromaDB Connection Test ---")
    
    try:
        # 1. Initialize the ChromaDB Client (uses default storage location)
        #client = chromadb.Client()
        client = chromadb.PersistentClient(path="./chroma_data") 
        print("Connected to persistent ChromaDB client successfully.")
        
        # 2. Get the existing collection
        # Note: If the collection doesn't exist, this will raise an error unless
        # you use get_or_create_collection(), but we expect it to exist here.
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' loaded. Total count: {collection.count()} records.")
        except Exception as e:
            print(f"Error: Could not find or load collection '{COLLECTION_NAME}'.")
            print("Please ensure you have run poc_scopesync_chromadb.py first to index the data.")
            print(f"Details: {e}")
            return
            
        # 3. Retrieve all records from the collection
        # We only retrieve IDs, Documents (summaries), and Metadatas (team/description)
        all_records = collection.get(
            include=['documents', 'metadatas'] 
        )
        
        # 4. Print the records in a human-readable format
        print("\n--- Retrieved Records Sample ---")
        
        # Check if any records were returned
        if not all_records['ids']:
            print("The collection is empty.")
            return

        for i, jira_id in enumerate(all_records['ids']):
            summary = all_records['documents'][i]
            metadata = all_records['metadatas'][i]
            team = metadata.get(TEAM_METADATA_KEY, 'N/A')
            description_snippet = metadata.get(DESCRIPTION_METADATA_KEY, 'N/A')
            
            # Simple formatting for clarity
            print(f"\nID: {jira_id}")
            print(f"  Team: {team}")
            print(f"  Summary: {summary}")
            print(f"  Context Snippet: {description_snippet[:75]}...")
        
        print(f"\n--- Successfully retrieved and displayed {len(all_records['ids'])} records. ---")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred during connection or retrieval: {e}")
        
if __name__ == "__main__":
    test_connection_and_retrieve_all_records()