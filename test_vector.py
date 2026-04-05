import warnings
warnings.filterwarnings("ignore")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "visa_vector_store"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

country = "germany"
visa_type = "student visa"
query = "What are the financial requirements?"

print("Running similarity search...")
results = vectorstore.similarity_search(
    query,
    k=3,
    filter={
        "country": country,
        "visa_type": visa_type
    }
)

if not results:
    print("No matches found.")
else:
    for i, doc in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Country: {doc.metadata.get('country')}")
        print(f"  Visa Type: {doc.metadata.get('visa_type')}")
        print(f"  Source: {doc.metadata.get('official_source')}")
        print(f"  Content: {doc.page_content}")
        print()
