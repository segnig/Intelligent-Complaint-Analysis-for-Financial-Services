import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os

# Set up environment variables for Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)

# 1. Initialize Vector DB and Embedding Model
chroma_client = chromadb.PersistentClient(path="/content/drive/MyDrive/Data Science/Week-6/vector_store/chroma")
collection = chroma_client.get_or_create_collection(name="credi_complaints")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Gemini-Optimized Prompt Template
TEMPLATE = """You are a financial analyst assistant for CrediTrust. Answer the user's question about customer complaints using ONLY the context provided below.

Important Instructions:
1. Be concise and professional
2. If the answer isn't in the context, say "I don't have sufficient information"
3. Never invent details
4. Reference complaint IDs when available

Context:
{context}

Question: {question}

Answer:"""

# 3. Retrieve Context Chunks
def retrieve_context(question, k=5):
    question_embedding = embedding_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=k
    )
    return results["documents"][0], results["metadatas"][0]

def query_gemini(prompt, model_name="gemini-2.5-flash"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=512,
                top_p=0.95,
                top_k=40
            ),
            safety_settings=[
                {"category": "HATE", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUAL", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS", "threshold": "BLOCK_NONE"}
            ]
        )
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

# RAG Pipeline with Gemini
def generate_answer(question):
    context_chunks, metadatas = retrieve_context(question)
    context_text = "\n\n".join([
        f"Complaint ID: {meta['complaint_id']}\n{text}"
        for text, meta in zip(context_chunks, metadatas)
    ])

    prompt = TEMPLATE.format(context=context_text, question=question)
    print("Prompt:", prompt)
    answer = query_gemini(prompt)
    return answer.strip(), context_chunks, metadatas

# Example usage
if __name__ == "__main__":
    sample_question = "Why are customers complaining about BNPL services?"
    answer, sources, metadata = generate_answer(sample_question)
    print("\nQuestion:", sample_question)
    print("\nAnswer:\n", answer)
    print("\nSources:")
    for i, (source, meta) in enumerate(zip(sources, metadata)):
        print(f"\nSource {i+1} (ID: {meta['complaint_id']}):")
        print(source[:200] + "..." if len(source) > 200 else source)