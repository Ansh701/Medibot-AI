from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

#Extract Data From the PDF File
def load_pdf_file(data):
    """Load PDF files from directory"""
    try:
        loader = DirectoryLoader(data,
                                glob="*.pdf",
                                loader_cls=PyPDFLoader)

        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents from {data}")
        return documents
    except Exception as e:
        logger.error(f"❌ Error loading PDF files: {e}")
        return []

def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Given a list of Document objects, return a new list of Document objects
    containing only 'source' in metadata and the original page_content.
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    logger.info(f"Filtered {len(minimal_docs)} documents")
    return minimal_docs

#Split the Data into Text Chunks
def text_split(extracted_data):
    """Split documents into chunks"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(extracted_data)
        logger.info(f"Created {len(text_chunks)} text chunks")
        return text_chunks
    except Exception as e:
        logger.error(f"❌ Error splitting text: {e}")
        return []

#Download the Embeddings from HuggingFace 
def download_hugging_face_embeddings():
    """Download and initialize HuggingFace embeddings"""
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')  #this model returns 384 dimensions
        logger.info("HuggingFace embeddings initialized successfully")
        return embeddings
    except Exception as e:
        logger.error(f"❌ Error initializing embeddings: {e}")
        raise e
