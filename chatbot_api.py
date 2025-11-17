from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Configuration
CHROMA_PATH = "chroma_db"

# Embeddings + LLM
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(temperature=0.5, model="gemini-2.5-flash")

# Connect to Chroma
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# Set up the vectorstore to be the retriever
num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})

# FastAPI app
app = FastAPI()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(payload: Query):
    question = payload.question

    # retrieve the relevant chunks based on the question asked
    docs = retriever.invoke(question)

    # add all the chunks to 'knowledge'
    knowledge = ""

    for doc in docs:
        knowledge += doc.page_content+"\n\n"

    rag_prompt = f"""
    You are an assistent which answers questions based on knowledge which is provided to you.
    While answering, you don't use your internal knowledge, 
    but solely the information in the "The knowledge" section.
    You don't mention anything to the user about the povided knowledge.

    The Question: {question}

    The Knowledge: {knowledge}
    """

    # LLM answer (non-streaming for API)
    response = llm.invoke(rag_prompt)
    return {"answer": response.content}
