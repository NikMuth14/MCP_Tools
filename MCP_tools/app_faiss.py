import openai
import fitz  # PyMuPDF for PDF processing
import faiss  # Vector search
import numpy as np
import os

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
# Set OpenAI API Key (Make sure to set this as an environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")



#openai.api_key = "<Gibberish>"


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and splits it into chunks."""
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n".join([page.get_text() for page in doc])
        return text if text.strip() else "No text extracted from the PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

def split_text_into_chunks(text, chunk_size=500):
    """Splits text into chunks of a given size."""
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def get_embedding(text):
    """Fetches the embedding of a given text using OpenAI's embedding model."""
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return np.array(response["data"][0]["embedding"], dtype=np.float32)

def build_faiss_index(chunks):
    """Creates a FAISS index and stores the embeddings of the text chunks."""
    embeddings = np.array([get_embedding(chunk) for chunk in chunks])
    index = faiss.IndexFlatL2(embeddings.shape[1])  # Create a FAISS index
    index.add(embeddings)  # Add embeddings to FAISS
    return index, embeddings

def retrieve_relevant_chunk(user_query, chunks, index):
    """Finds the most relevant chunk of text using FAISS similarity search."""
    query_embedding = get_embedding(user_query).reshape(1, -1)
    _, nearest_index = index.search(query_embedding, 1)  # Find the nearest chunk
    return chunks[nearest_index[0][0]]  # Return the most relevant chunk

def chatbot(pdf_path):
    """Runs the RAG chatbot by extracting text, embedding it, and retrieving relevant responses."""
    print("Loading and processing the PDF...")
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)  # Split into smaller parts
    index, _ = build_faiss_index(chunks)  # Create vector database

    print("RAG Chatbot is ready! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        relevant_chunk = retrieve_relevant_chunk(user_input, chunks, index)

        context = f"Knowledge Base: {relevant_chunk}\nUser Query: {user_input}"
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": context}]
        )["choices"][0]["message"]["content"]

        print("Bot:", response)

if __name__ == "__main__":
    chatbot("knowledge_base.pdf")
