from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Paths
DATA_PATH = "data"
FAISS_PATH = "faiss_index"

# Embeddings
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# Load text files
txt_loader = DirectoryLoader(
    DATA_PATH,
    glob="**/*.txt",
    loader_cls=TextLoader
)

raw_documents = txt_loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# --- Create FAISS vector store ---
# FAISS does NOT use IDs, but we can include metadata if needed

# Build index
vector_store = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings_model
)

# Save locally (will generate two files: index.faiss + index.pkl)
vector_store.save_local(FAISS_PATH)

print("FAISS vector store created and saved to:", FAISS_PATH)
