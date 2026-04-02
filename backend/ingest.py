"""
Document Ingestion Script
===========================
Run this script ONCE to:
1. Load your medical PDFs/TXTs from /backend/data/
2. Split them into chunks
3. Create embeddings
4. Upload everything to Pinecone

Usage:
    cd backend
    python ingest.py

After running this, your Pinecone index is populated and ready.
You only need to run this again if you add new documents.
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST before any other imports

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.vector_store import ingest_documents


def main():
    print("=" * 50)
    print("🏥 Medical Chatbot - Document Ingestion")
    print("=" * 50)

    # Verify environment variables
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please create a .env file. See .env.example for reference.")
        sys.exit(1)

    print(f"📌 Pinecone Index: {os.getenv('PINECONE_INDEX_NAME')}")
    print(f"🤖 OpenAI Embeddings: text-embedding-ada-002")
    print()

    # Run ingestion
    try:
        vectorstore = ingest_documents()
        print()
        print("=" * 50)
        print("✅ Ingestion complete! Your chatbot is ready.")
        print("   Run: python app.py   to start the API server")
        print("=" * 50)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo add documents:")
        print("  1. Create a folder: backend/data/")
        print("  2. Add medical PDF files to it")
        print("  3. Run this script again")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
