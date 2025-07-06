import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
from tqdm import tqdm


# 1. Load Cleaned Data
df = pd.read_csv("filtered_complaints.csv")

# 2. Initialize Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", "!", "?", " ", ""]
)

# 3. Initialize Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 4. Initialize ChromaDB Client (Persistent)
chroma_client = chromadb.PersistentClient(path="/content/drive/MyDrive/Data Science/Week-6/vector_store/chroma")

collection = chroma_client.get_or_create_collection(name="credi_complaints")

# 5. Chunk, Embed, and Add to ChromaDB
chunk_id = 0
for i, row in tqdm(df.iterrows(), total=len(df)):
    complaint_id = str(row['complaint_id'])
    product = row['product']
    chunks = text_splitter.split_text(row['cleaned_narrative'])

    if not chunks:
        continue

    embeddings = model.encode(chunks)

    for j, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[emb.tolist()],
            ids=[f"{complaint_id}_{j}"],
            metadatas=[{
                "complaint_id": complaint_id,
                "product": product
            }]
        )
        chunk_id += 1
        

print(f"Total Chunks Indexed: {chunk_id}")
# No explicit persist needed for PersistentClient
print("ChromaDB persisted successfully to 'vector_store/chroma'")