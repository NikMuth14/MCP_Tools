# Simple client to test the weather server using requests only (no sseclient dependency)
import requests
import json
import time

def main():
    try:
        # First, get the list of available tools
        print("Checking available tools...")
        response = requests.get("http://localhost:8000/mcp/v1/tools")
        print("Available tools response status:", response.status_code)
        if response.status_code == 200:
            print("Available tools:", json.dumps(response.json(), indent=2))
        else:
            print("Error getting tools:", response.text)
        
        # Call the get_weather tool
        print("\nRequesting weather for New York...")
        weather_request = {
            "tool": "get_weather",
            "parameters": {"location": "New York"},
            "id": "123"
        }
        
        response = requests.post(
            "http://localhost:8000/mcp/v1/tools/invoke",
            json=weather_request
        )
        
        print("Weather invoke response status:", response.status_code)
        print("Weather result:", response.text)
        
        # Listen for SSE events using requests.get with stream=True
        print("\nListening for SSE events (press Ctrl+C to stop)...")
        try:
            sse_response = requests.get("http://localhost:8000/mcp/v1/events", stream=True)
            for line in sse_response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        event_data = decoded_line[5:].strip()
                        try:
                            event_json = json.loads(event_data)
                            print(f"Received event: {json.dumps(event_json, indent=2)}")
                        except json.JSONDecodeError:
                            print(f"Received non-JSON event: {event_data}")
        except KeyboardInterrupt:
            print("Stopped listening for events")
        except Exception as e:
            print(f"Error listening for events: {e}")
            
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
