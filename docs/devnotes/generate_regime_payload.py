import json
import requests

# Define file paths
regime_detection_payload_path = "C:\\Users\\chave\\PROJECTS\\cailculator-mcp\\regime_detection.json"

# 1. Make HTTP POST request to load_market_data
load_market_data_url = "http://localhost:8080/message"
load_market_data_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "load_market_data",
        "arguments": {
            "file_path": "C:\\Users\\chave\\PROJECTS\\cailculator-mcp\\bitcoin_historical_full.csv"
        }
    }
}

headers = {'Content-Type': 'application/json'}
response = requests.post(load_market_data_url, headers=headers, data=json.dumps(load_market_data_payload))
response.raise_for_status()  # Raise an exception for HTTP errors

load_data_response = response.json()

# Extract the inner JSON string (the actual tool result)
market_data_str = load_data_response['result']['content'][0]['text']

# Parse the inner JSON to get the market data object
market_data_object = json.loads(market_data_str)

# Extract the 'data' field from the market data object
ohclv_data = market_data_object['data']

# Construct the regime_detection payload
regime_detection_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "regime_detection",
        "arguments": {
            "data": ohclv_data,
            "show_methodology": True,
            "fast_mode": False # Changed to False
        }
    }
}

# Save the regime_detection payload to a file
with open(regime_detection_payload_path, 'w') as f:
    json.dump(regime_detection_payload, f, indent=2)

print(f"Successfully created {regime_detection_payload_path}")
