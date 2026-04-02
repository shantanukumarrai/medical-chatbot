"""
Vector Store Utility
====================
Handles everything related to Pinecone:
- Initializing the Pinecone client
- Loading and chunking PDF/text documents
- Creating embeddings and storing them
- Retrieving a retriever for RAG queries
"""

import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import time


# ─────────────────────────────────────────────
# 1. Initialize Pinecone Client
# ─────────────────────────────────────────────
def get_pinecone_client():
    """
    Creates and returns a Pinecone client using the API key from .env
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc


# ─────────────────────────────────────────────
# 2. Create or Connect to an Index
# ─────────────────────────────────────────────
def create_or_connect_index(pc, index_name: str, dimension: int = 1536):
    """
    Creates a new Pinecone index if it doesn't exist, or connects to an existing one.

    Args:
        pc: Pinecone client
        index_name: Name of the index (set in .env)
        dimension: Embedding dimension — 1536 for OpenAI text-embedding-ada-002
    """
    existing_indexes = [i.name for i in pc.list_indexes()]

    if index_name not in existing_indexes:
        print(f"📦 Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",  # Cosine similarity is best for text embeddings
            spec=ServerlessSpec(
                cloud="aws",
                region=os.getenv("PINECONE_ENV", "us-east-1")
            )
        )
        # Wait for the index to be ready
        while not pc.describe_index(index_name).status["ready"]:
            print("⏳ Waiting for index to be ready...")
            time.sleep(2)
        print(f"✅ Index '{index_name}' is ready!")
    else:
        print(f"✅ Connected to existing index: {index_name}")

    return pc.Index(index_name)


# ─────────────────────────────────────────────
# 3. Load Documents from the /data folder
# ─────────────────────────────────────────────
def load_documents(data_path: str = "data/"):
    """
    Loads PDF and .txt files from the data directory.
    Add your medical PDFs (textbooks, guidelines, FAQs) to /backend/data/

    Returns:
        List of LangChain Document objects
    """
    documents = []

    # Load PDFs
    if os.path.exists(data_path):
        pdf_loader = DirectoryLoader(
            data_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        documents.extend(pdf_loader.load())

        # Load .txt files too
        txt_loader = DirectoryLoader(
            data_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True
        )
        documents.extend(txt_loader.load())

    if not documents:
        print("⚠️  No documents found in /data. Add PDF/TXT medical files.")
    else:
        print(f"📄 Loaded {len(documents)} document pages.")

    return documents


# ─────────────────────────────────────────────
# 4. Split Documents into Chunks
# ─────────────────────────────────────────────
def split_documents(documents):
    """
    Splits large documents into smaller overlapping chunks.
    Overlap ensures context isn't lost at chunk boundaries.

    Returns:
        List of smaller Document chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Each chunk = ~500 characters
        chunk_overlap=50,     # 50 chars overlap between chunks
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️  Split into {len(chunks)} chunks.")
    return chunks


# ─────────────────────────────────────────────
# 5. Create Embeddings Model
# ─────────────────────────────────────────────
def get_embeddings():
    """
   Returns HuggingFace Embeddings model (FREE).
    This converts text into 384-dimensional vectors.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ─────────────────────────────────────────────
# 6. Ingest Documents into Pinecone
# ─────────────────────────────────────────────
def ingest_documents():
    """
    Full pipeline: Load → Split → Embed → Store in Pinecone
    Run this ONCE to populate your vector database.
    Then it's ready for retrieval.
    """
    index_name = os.getenv("PINECONE_INDEX_NAME", "medical-chatbot")

    # Step 1: Load documents
    documents = load_documents("data/")
    if not documents:
        raise ValueError("No documents found. Add PDFs to /backend/data/")

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # Step 3: Get embeddings model
    embeddings = get_embeddings()

    # Step 4: Connect to Pinecone
    pc = get_pinecone_client()
    create_or_connect_index(pc, index_name)

    # Step 5: Upload chunks to Pinecone
    print("⬆️  Uploading embeddings to Pinecone...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name
    )
    print("✅ Documents successfully ingested into Pinecone!")
    return vectorstore


# ─────────────────────────────────────────────
# 7. Load Existing Vector Store (for querying)
# ─────────────────────────────────────────────
def get_vectorstore():
    """
    Connects to an EXISTING Pinecone index (already populated).
    Used at app startup — no re-ingestion needed.

    Returns:
        PineconeVectorStore object
    """
    index_name = os.getenv("PINECONE_INDEX_NAME", "medical-chatbot")
    embeddings = get_embeddings()

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
    return vectorstore


# ─────────────────────────────────────────────
# 8. Get Retriever
# ─────────────────────────────────────────────
def get_retriever(k: int = 4):
    """
    Returns a retriever that finds the top-k most relevant chunks
    for a given query. Used inside LangChain chains.

    Args:
        k: Number of document chunks to retrieve per query
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    return retriever
