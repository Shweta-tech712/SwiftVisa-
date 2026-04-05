from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "visa_vector_store"

def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


if __name__ == "__main__":
    print("Loading vector store...\n")
    vectorstore = load_vector_store()

    # Simulated structured user input (must match metadata case/format in vector store)
    country = "germany"
    visa_type = "student visa"

    query = "What are the financial requirements?"
    print(f"Query: {query}")
    print(f"Filter: Country = {country}, Visa Type = {visa_type}\n")

    results = vectorstore.similarity_search(
        query,
        k=3,
        filter={
            "country": country,
            "visa_type": visa_type
        }
    )

    if not results:
        print("No matching documents found.")
    else:
        for i, doc in enumerate(results):
            print(f"\nResult {i+1}")
            print("Country:", doc.metadata.get("country"))
            print("Visa Type:", doc.metadata.get("visa_type"))
            print("Source:", doc.metadata.get("official_source"))
            print("Content:\n", doc.page_content)
            print("-" * 60)
