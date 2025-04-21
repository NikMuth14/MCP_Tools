# Use official Python image
FROM python:3.13.2

# Set the working directory inside the container
WORKDIR /app

# Copy necessary files to the container
COPY requirements.txt .
COPY app.py .
COPY knowledge_base.pdf .
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for OpenAI API Key
#ENV OPENAI_API_KEY="OPENAI_API_KEY"
#ENV PINECONE_API_KEY=""


# Run the chatbot script
CMD ["python", "app.py"]