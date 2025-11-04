# 💡 Jira Feature Overlap Detector (J-FOD) POC

## Project Overview

This Proof of Concept (POC) utilizes a **local, small Large Language Model (LLM)** for **Semantic Similarity Analysis** to proactively detect overlapping or duplicate features across multiple development teams from a Jira Excel export.

Instead of relying on keyword matching, J-FOD understands the _meaning_ of Jira summaries, grouping tickets that describe similar work (e.g., "Update user profile" and "Allow customers to edit personal info").

The core output is a report that flags **Cross-Team Overlaps**, helping Product Managers and Scrum Masters identify and consolidate redundant efforts.

## Key Technology

| Component                | Role               | Notes                                                                                                                                                         |
| :----------------------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Language**             | Python             | Standard for data science and NLP tasks.                                                                                                                      |
| **Data Source**          | `jira_data.xlsx`   | Simple input file mimicking a Jira export.                                                                                                                    |
| **Embedding Model**      | `all-MiniLM-L6-v2` | A small, fast, and high-performing Sentence Transformer model. Runs **entirely locally** (no API keys required).                                              |
| **Clustering Algorithm** | **DBSCAN**         | Groups the resulting semantic vectors. Excellent for this task as it automatically discovers the number of clusters and identifies outliers (unique tickets). |

## 🚀 Setup and Execution

### Prerequisites

1.  **Python** (3.8+) installed.
2.  **`jira_data.xlsx`** file created in the project root (see data structure below).

### Installation

Install the required Python libraries using `pip`:

```bash
pip install pandas openpyxl sentence-transformers scikit-learn
```
