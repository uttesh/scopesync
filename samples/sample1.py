from sentence_transformers import SentenceTransformer

# Load the pre-trained all-MiniLM-L6-v2 model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define some sample sentences
sentences = [
    "The cat sat on the mat.",
    "A feline rested on the rug.",
    "Dogs are loyal companions."
]

# Generate embeddings for the sentences
embeddings = model.encode(sentences)

# Print the embeddings for the first sentence
print(f"Embedding for '{sentences[0]}':\n{embeddings[0][:10]}...") # Display first 10 dimensions for brevity
print(f"Shape of embedding for '{sentences[0]}': {embeddings[0].shape}")

# Print the embeddings for the second sentence
print(f"\nEmbedding for '{sentences[1]}':\n{embeddings[1][:10]}...")

# Print the embeddings for the third sentence
print(f"\nEmbedding for '{sentences[2]}':\n{embeddings[2][:10]}...")