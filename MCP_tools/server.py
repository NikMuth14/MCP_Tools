import fitz  # PyMuPDF for PDF processing
import os
from openai import OpenAI  # Updated OpenAI import
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
# Set OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    spec = ServerlessSpec(cloud="aws", region="us-east-1")
    INDEX_NAME = "rag-chatbot"

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        pc.create_index(name=INDEX_NAME, dimension=1536, metric="cosine", spec=spec)

    index = pc.Index(INDEX_NAME)
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    # Create a fallback if Pinecone fails
    index = None

# FastMCP instance for our RAG server
mcp = FastMCP("RAGChatbot")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n".join([page.get_text() for page in doc])
        return text if text.strip() else "No text extracted from the PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

def split_text_into_chunks(text: str, chunk_size: int = 500):
    """Splits text into smaller chunks."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def get_embedding(text: str):
    """Generates embedding using OpenAI's text-embedding-ada-002 model."""
    try:
        response = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002")
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a dummy embedding if the API call fails
        return [0.0] * 1536

def store_embeddings(chunks):
    """Stores text chunks as embeddings in Pinecone."""
    if index is None:
        print("Pinecone index not available. Cannot store embeddings.")
        return
    
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        vectors.append((str(i), embedding, {"text": chunk}))
    try:
        index.upsert(vectors)
    except Exception as e:
        print(f"Error storing embeddings: {e}")

def retrieve_relevant_chunk(user_query: str) -> str:
    """Retrieves the most relevant chunk from Pinecone based on a user query."""
    if index is None:
        return "Knowledge base not available."
    
    try:
        query_embedding = get_embedding(user_query)
        results = index.query(vector=query_embedding, top_k=1, include_metadata=True)
        if results and results.matches:
            return results.matches[0].metadata["text"]
        return "No relevant data found."
    except Exception as e:
        print(f"Error retrieving relevant chunk: {e}")
        return "Error retrieving information from knowledge base."

@mcp.tool()
async def ingest_pdf(pdf_path: str) -> str:
    """
    Ingests a PDF file by extracting text, splitting it into chunks,
    and storing embeddings in Pinecone.
    """
    text = extract_text_from_pdf(pdf_path)
    if text.startswith("Error"):
        return text
    chunks = split_text_into_chunks(text)
    store_embeddings(chunks)
    return f"PDF ingested successfully with {len(chunks)} chunks stored."

@mcp.tool()
async def query_chatbot(user_query: str) -> str:
    """
    Processes a user query by retrieving a relevant chunk from Pinecone
    and generating a response with GPT-4o.
    """
    try:
        relevant_chunk = retrieve_relevant_chunk(user_query)
        context = f"Knowledge Base: {relevant_chunk}\nUser Query: {user_query}"
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # Add system message if needed
                {"role": "user", "content": context}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying chatbot: {e}")
        return f"I encountered an error while processing your query: {str(e)[:100]}..."

if __name__ == "__main__":
    # Start the FastMCP server using Server-Sent Events transport
    mcp.run(transport="sse")
