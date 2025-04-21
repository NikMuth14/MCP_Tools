import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    async with MultiServerMCPClient({
        "ragchatbot": {  # Must match the server name registered in FastMCP
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    }) as client:
        # Get the tools exposed by the server
        tools = client.get_tools()
        print("Tools type:", type(tools))
        print("Tools content:", tools)
        
        # Access tools directly if they're in a list
        if isinstance(tools, list):
            # Find the tools by name in the list
            ingest_pdf = next((tool for tool in tools if tool.name == "ingest_pdf"), None)
            query_chatbot = next((tool for tool in tools if tool.name == "query_chatbot"), None)
            
            if not ingest_pdf or not query_chatbot:
                print("Warning: Could not find required tools. Available tools:", [t.name for t in tools if hasattr(t, 'name')])
        else:
            # Try the original approach if tools is a dictionary
            ragchatbot_tools = tools.get("ragchatbot", {})
            ingest_pdf = ragchatbot_tools.get("ingest_pdf")
            query_chatbot = ragchatbot_tools.get("query_chatbot")

        # Optionally ingest a PDF for knowledge base creation
        pdf_path = "Knowledge_Base_1.pdf"
        if pdf_path and ingest_pdf:
            print("Ingesting PDF...")
            try:
                # Use .ainvoke() method for async tools
                ingest_result = await ingest_pdf.ainvoke({"pdf_path": pdf_path})
                print("Ingest result:", ingest_result)
            except Exception as e:
                print(f"Error ingesting PDF: {e}")
        else:
            print("Skipping PDF ingestion.")

        # Chat loop
        if query_chatbot:
            print("Chatbot is ready! Type 'exit' to quit.")
            while True:
                user_query = input("You: ").strip()
                if user_query.lower() == "exit":
                    print("Goodbye!")
                    break

                # Get response from the chatbot tool
                try:
                    # Use .ainvoke() method for async tools
                    response = await query_chatbot.ainvoke({"user_query": user_query})
                    print("Bot:", response)
                except Exception as e:
                    print(f"Error getting response: {e}")
        else:
            print("Chatbot tools not available. Please check server configuration.")

if __name__ == "__main__":
    asyncio.run(main())
