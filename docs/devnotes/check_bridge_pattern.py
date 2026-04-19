import json
import requests

# Define the pattern (e₂ − e₁₃) × (e₆ + e₉) at 32D
# Operand 1: e₂ - e₁₃
operand1_coeffs = [0] * 32
operand1_coeffs[2] = 1  # e₂
operand1_coeffs[13] = -1 # -e₁₃

# Operand 2: e₆ + e₉
operand2_coeffs = [0] * 32
operand2_coeffs[6] = 1  # e₆
operand2_coeffs[9] = 1  # e₉

# Base URL for MCP server
message_url = "http://localhost:8080/message"
headers = {'Content-Type': 'application/json'}

# --- Step 1: Calculate Product for Cayley-Dickson ---
multiply_cd_payload = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "compute_high_dimensional",
        "arguments": {
            "framework": "cayley-dickson",
            "operation": "multiply",
            "dimension": 32,
            "operands": [operand1_coeffs, operand2_coeffs]
        }
    }
}

response = requests.post(message_url, headers=headers, data=json.dumps(multiply_cd_payload))
response.raise_for_status()
multiply_cd_result = response.json()

# Extract the product coefficients
product_cd_str = multiply_cd_result['result']['content'][0]['text']
product_cd_object = json.loads(product_cd_str)
product_cd_coeffs = product_cd_object['result']

print(f"Cayley-Dickson Product: {product_cd_coeffs}")

# --- Step 2: Check Norm for Cayley-Dickson ---
check_norm_cd_payload = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "compute_high_dimensional",
        "arguments": {
            "framework": "cayley-dickson",
            "operation": "norm",
            "dimension": 32,
            "operands": [product_cd_coeffs]
        }
    }
}

response = requests.post(message_url, headers=headers, data=json.dumps(check_norm_cd_payload))
response.raise_for_status()
check_norm_cd_result = response.json()

check_norm_cd_str = check_norm_cd_result['result']['content'][0]['text']
check_norm_cd_object = json.loads(check_norm_cd_str)

print(f"Full Cayley-Dickson Norm Check Object: {check_norm_cd_object}")

norm_cd = check_norm_cd_object['norm'] # Corrected key

print(f"Norm (Cayley-Dickson): {norm_cd}")
is_zero_divisor_cd = abs(norm_cd) < 1e-10
print(f"Is Zero Divisor (Cayley-Dickson): {is_zero_divisor_cd}")

# --- Step 3: Calculate Product for Clifford ---
multiply_clifford_payload = {
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
        "name": "compute_high_dimensional",
        "arguments": {
            "framework": "clifford",
            "operation": "multiply",
            "dimension": 32,
            "operands": [operand1_coeffs, operand2_coeffs]
        }
    }
}

response = requests.post(message_url, headers=headers, data=json.dumps(multiply_clifford_payload))
response.raise_for_status()
multiply_clifford_result = response.json()

# Extract the product coefficients
product_clifford_str = multiply_clifford_result['result']['content'][0]['text']
product_clifford_object = json.loads(product_clifford_str)
product_clifford_coeffs = product_clifford_object['result']

print(f"Clifford Product: {product_clifford_coeffs}")

# --- Step 4: Check Norm for Clifford ---
check_norm_clifford_payload = {
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
        "name": "compute_high_dimensional",
        "arguments": {
            "framework": "clifford",
            "operation": "norm",
            "dimension": 32,
            "operands": [product_clifford_coeffs]
        }
    }
}

response = requests.post(message_url, headers=headers, data=json.dumps(check_norm_clifford_payload))
response.raise_for_status()
check_norm_clifford_result = response.json()

check_norm_clifford_str = check_norm_clifford_result['result']['content'][0]['text']
check_norm_clifford_object = json.loads(check_norm_clifford_str)

print(f"Full Clifford Norm Check Object: {check_norm_clifford_object}")

norm_clifford = check_norm_clifford_object['norm'] # Corrected key

print(f"Norm (Clifford): {norm_clifford}")
is_zero_divisor_clifford = abs(norm_clifford) < 1e-10
print(f"Is Zero Divisor (Clifford): {is_zero_divisor_clifford}")

# --- Step 5: Compare results ---
if is_zero_divisor_cd and is_zero_divisor_clifford:
    print("\nBridge Pattern Found: (e₂ − e₁₃) × (e₆ + e₉) is a zero divisor in BOTH Cayley-Dickson and Clifford at 32D!")
else:
    print("\nPattern is NOT a bridge pattern for (e₂ − e₁₃) × (e₆ + e₉) at 32D.")
