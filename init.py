# get environment variables
import os
EMBEDDINGS_ENDPOINT = os.getenv('EMBEDDINGS_ENDPOINT')
CHROMADB_COLLECTION = os.getenv('CHROMADB_COLLECTION')
QA_FILE = os.getenv('QA_FILE')
DB_FILE = os.getenv('DB_FILE')

# import QA (json format)
from langchain_community.document_loaders import JSONLoader

# define a function to extract metadata from each item
def metadata_func(record, metadata):
    metadata["answer"] = record.get("answer")
    return metadata

# load the documents
print(f"Loading documents...")
loader = JSONLoader(
    file_path=QA_FILE,
    jq_schema='map(.question + "\\n" + .answer) | .[]'
)
documents = loader.load()

print(f"Number of documents loaded: {len(documents)}")

# embeddings
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
embeddings = HuggingFaceEndpointEmbeddings(model=EMBEDDINGS_ENDPOINT)

print(f"Testing embeddings endpoint")

text = "Co to jest żurek?"
query_result = embeddings.embed_query(text)
print(query_result[:3])

# populate vector store with documents
import chromadb

print(f"Connecting to vector database...")

client = chromadb.PersistentClient(path=DB_FILE)
for collection in client.list_collections():
    count = collection.count()
    print(f"{collection.name}: {count}")

# delete existing collection
try:
    client.delete_collection(name=CHROMADB_COLLECTION)
    print(f"Collection {CHROMADB_COLLECTION} deleted.")
finally:
    print(f"Collection {CHROMADB_COLLECTION} does not exist.")

client.persist()
client.close

# Connect to the existing ChromaDB
from langchain_community.vectorstores import Chroma

# Create a Chroma vector store from the documents and embeddings model
# This process generates and stores the embeddings for each question.
vector_db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name=CHROMADB_COLLECTION,
    persist_directory=DB_FILE
)

# Verify number of documents in the vector database
print(f"Number of documents in the vector database: {vector_db._collection.count()}")

# Retrieve all documents from the collection
all_docs = vector_db.get(include=["metadatas", "documents","embeddings"])

# Number of documents
print(f"Number of documents retrieved: {len(all_docs['documents'])}")

# Example document:
print(f"Example document:")
print(all_docs['documents'][0])
print(all_docs['metadatas'][0])
print(all_docs['embeddings'][0])