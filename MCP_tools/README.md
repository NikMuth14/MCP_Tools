# Weather Server and Client

This repository contains a simple weather server and client implementation using Server-Sent Events (SSE) for communication.

## Overview

The application consists of two main components:

1. **Server (`server.py`)**: A FastMCP-based server that provides a weather tool endpoint.
2. **Client (`client.py`)**: A client that connects to the server and requests weather information.

## Requirements

- Python 3.8+
- Virtual environment (recommended)

## Installation

### Setting up the environment

1. Create a virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source .venv/bin/activate
     ```

3. Install the required packages:
   ```
   pip install mcp langchain-mcp-adapters langgraph langchain-openai
   ```

## Running the Application

### Start the Server

1. Make sure your virtual environment is activated.
2. Run the server:
   ```
   python server.py
   ```
   The server will start on `http://0.0.0.0:8000`.

   **Example Server Output:**
   ```
   INFO:     Started server process [32952]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

### Run the Client

1. In a separate terminal, activate the virtual environment.
2. Run the client:
   ```
   python client.py
   ```
   The client will connect to the server and request weather information for New York City.

   **Example Client Output:**
   ```
   {'messages': [HumanMessage(content='what is the weather in nyc?', additional_kwargs={})]}
   ```

## Code Structure

### Server (`server.py`)

The server provides a simple weather tool that returns a fixed message for any location.

```python
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"
```

### Client (`client.py`)

The client uses `langchain-mcp-adapters` to connect to the server and invoke the weather tool.

## Troubleshooting

- If you encounter a "ModuleNotFoundError", make sure you've installed all the required packages in your active virtual environment.
- If the server fails to start due to port conflicts, you may need to modify the port in both the server and client code.
- Make sure to run the server before running the client.

## Alternative Client

An alternative client implementation (`client_no_sseclient.py`) is provided that uses only the `requests` library without requiring the `sseclient` package.

**Example Alternative Client Output:**
```
Checking available tools...
Available tools response status: 404
Error getting tools: Not Found

Requesting weather for New York...
Weather invoke response status: 404
Weather result: Not Found

Listening for SSE events (press Ctrl+C to stop)...
```

## Expected Output When Everything Works Correctly

When the server and client are properly configured and running, you should see the following output:

**Server:**
```
INFO:     Started server process [32952]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:55151 - "GET /mcp/v1/tools HTTP/1.1" 200 OK
INFO:     127.0.0.1:55162 - "POST /mcp/v1/tools/invoke HTTP/1.1" 200 OK
```

**Client:**
```
Weather for New York: It's always sunny in New York
```
