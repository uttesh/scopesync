# 🚀 ScopeSync: Real-Time Feature Overlap Detector (Vector Database Architecture)

## Project Overview

This is the **production-ready architecture** for **ScopeSync**. It moves beyond batch processing (like DBSCAN clustering) to use a **Vector Database (VD)** for real-time, on-the-fly semantic overlap detection. This is crucial for large organizations with continuously updating Jira backlogs.

The system still uses a **local LLM** (`all-MiniLM-L6-v2`) to convert Jira summaries into high-dimensional vectors, but instead of clustering them, it indexes them in the VD. When a new ticket is created, ScopeSync runs a **semantic search** against the entire backlog to instantly find the most similar existing features across all teams.

## Key Technology Upgrades

| Component             | POC Architecture (DBSCAN)                               | Real-Time Architecture (VD)                                        |
| :-------------------- | :------------------------------------------------------ | :----------------------------------------------------------------- |
| **Indexing/Storage**  | Pandas DataFrame (in memory)                            | **ChromaDB** (Vector Database)                                     |
| **Search Mechanism**  | **DBSCAN Clustering** (Batch)                           | **Approximate Nearest Neighbors (ANN)** Search                     |
| **Overlap Detection** | Finds _all_ overlaps by grouping _all_ tickets at once. | Finds overlaps **relative to one single new ticket** in real-time. |
| **Scalability**       | Limited (slow re-clustering on updates).                | Highly scalable (vectors are added incrementally).                 |
| **Real-Time Use**     | No. Requires a full re-run.                             | **Yes.** Executes a fast query upon new ticket creation.           |

## 🛠️ Setup and Execution

### Prerequisites

1.  Python (3.8+) installed.
2.  `jira_data.xlsx` file available for initial indexing.

### Installation

Install the required Python libraries, including **ChromaDB**:

```bash
pip install pandas openpyxl sentence-transformers chromadb
```
