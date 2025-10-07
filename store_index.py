# store_index.py - Enhanced PDF to Vector Store Pipeline
from dotenv import load_dotenv
import os
import time
import logging
from src.helper import load_pdf_file, filter_to_minimal_docs, text_split, download_hugging_face_embeddings
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main pipeline for creating vector store from PDF documents"""

    print("=" * 60)
    print("🏥 MEDIBOT AI - MEDICAL KNOWLEDGE BASE BUILDER")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Validate environment variables
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not found in environment variables!")
        logger.info("Please add PINECONE_API_KEY to your .env file")
        return

    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

    # Optional: Set OpenAI key if you have it (not required for HuggingFace embeddings)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        logger.info("OpenAI API key found and set")

    try:
        # Step 1: Validate data directory
        data_dir = 'data/'
        if not os.path.exists(data_dir):
            logger.error(f"Data directory '{data_dir}' not found!")
            logger.info("Please create a 'data/' folder and add your PDF files")
            return

        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        if not pdf_files:
            logger.error(f"No PDF files found in '{data_dir}'")
            logger.info("Please add PDF files to the 'data/' folder")
            return

        logger.info(f"Found {len(pdf_files)} PDF file(s): {pdf_files}")

        # Step 2: Process PDF documents
        print("\n📚 STEP 1: Loading PDF Documents...")
        extracted_data = load_pdf_file(data=data_dir)

        if not extracted_data:
            logger.error("No documents were extracted from PDFs")
            return

        print(f"✓ Loaded {len(extracted_data)} document pages")

        # Step 3: Filter documents
        print("\n🔧 STEP 2: Filtering Documents...")
        filter_data = filter_to_minimal_docs(extracted_data)
        print(f"✓ Filtered {len(filter_data)} documents")

        # Step 4: Split into chunks
        print("\n✂️ STEP 3: Splitting Text into Chunks...")
        text_chunks = text_split(filter_data)

        if not text_chunks:
            logger.error("No text chunks were created")
            return

        print(f"✓ Created {len(text_chunks)} text chunks")

        # Step 5: Initialize embeddings
        print("\n🤖 STEP 4: Initializing Embeddings...")
        embeddings = download_hugging_face_embeddings()
        print("✓ HuggingFace embeddings ready")

        # Step 6: Setup Pinecone
        print("\n🌲 STEP 5: Connecting to Pinecone...")
        pc = Pinecone(api_key=PINECONE_API_KEY)

        index_name = "medical-chatbot"

        # Check if index exists
        existing_indexes = pc.list_indexes()
        index_exists = any(idx.name == index_name for idx in existing_indexes)

        if not index_exists:
            print(f"📝 Creating new index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=384,  # all-MiniLM-L6-v2 dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

            # Wait for index to be ready
            print("⏳ Waiting for index to be ready...")
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)

            print("✓ Index created and ready")
        else:
            print(f"✓ Using existing index: {index_name}")

        # Step 7: Create vector store
        print("\n💾 STEP 6: Creating Vector Store...")
        print("⏳ This may take a few minutes depending on document size...")

        docsearch = PineconeVectorStore.from_documents(
            documents=text_chunks,
            index_name=index_name,
            embedding=embeddings,
        )

        # Step 8: Verify the upload
        print("\n✅ STEP 7: Verifying Upload...")
        index = pc.Index(index_name)
        stats = index.describe_index_stats()

        print(f"✓ Vector store created successfully!")
        print(f"✓ Total vectors in index: {stats['total_vector_count']}")
        print(f"✓ Index dimension: {stats['dimension']}")

        # Test query
        print("\n🔍 STEP 8: Testing Query...")
        test_query = "What is diabetes?"
        test_results = docsearch.similarity_search(test_query, k=3)

        print(f"✓ Test query successful!")
        print(f"✓ Found {len(test_results)} relevant documents")

        print("\n" + "=" * 60)
        print("🎉 SUCCESS: Medical Knowledge Base Ready!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   • PDF files processed: {len(pdf_files)}")
        print(f"   • Document pages: {len(extracted_data)}")
        print(f"   • Text chunks: {len(text_chunks)}")
        print(f"   • Vectors in database: {stats['total_vector_count']}")
        print(f"   • Index name: {index_name}")
        print("\n🚀 You can now run 'python app.py' to start MediBot!")

    except Exception as e:
        logger.error(f"Error in pipeline: {e}")
        logger.info("Please check your API keys and network connection")
        raise


if __name__ == "__main__":
    main()
