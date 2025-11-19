import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index")

# Embeddings + LLM
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(temperature=0.5, model="gemini-2.5-flash")

# Connect to FAISS
vector_store = FAISS.load_local(FAISS_PATH, embeddings_model, allow_dangerous_deserialization=True)

# Set up the vectorstore to be the retriever
num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})

def lambda_handler(event,context):
    # event["body"] is a JSON string in API Gateway (REST)    
    body = json.loads(event.get("body", "{}"))
    question = body.get("question", "")

    # retrieve the relevant chunks based on the question asked
    docs = retriever.invoke(question)

    # add all the chunks to 'knowledge'
    knowledge = ""

    for doc in docs:
        knowledge += doc.page_content+"\n\n"

    rag_prompt = f"""
    You are an assistant for WorldLink.
    Your job is to answer questions based solely on the provided knowledge.

    However, follow these special rules:

    1. If the user greets you (examples: "hi", "hello", "hey", "how are you"), 
    reply politely and naturally. Do NOT use the knowledge section.

    2. If the user asks "who are you", "what are you",
    or anything about your identity, reply with:
    "I am the WorldLink AI Assistant. I can help answer questions about WorldLink's services, policies, and general information."

    3. For all other questions, you MUST answer ONLY using the information in 'The Knowledge' and not your internal knowledge.

    4. Never mention the knowledge section to the user.

    ---

    The Question: {question}

    The Knowledge: {knowledge}
    """

    response = llm.invoke(rag_prompt)
    answer = response.content

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"answer": answer})
    }