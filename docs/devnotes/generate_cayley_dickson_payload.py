import json

# Define the pattern (e₂ − e₁₃) × (e₆ + e₉) at 32D
# Operand 1: e₂ - e₁₃
operand1_coeffs = [0] * 32
operand1_coeffs[2] = 1  # e₂
operand1_coeffs[13] = -1 # -e₁₃

# Operand 2: e₆ + e₉
operand2_coeffs = [0] * 32
operand2_coeffs[6] = 1  # e₆
operand2_coeffs[9] = 1  # e₉

# Construct the compute_high_dimensional payload for Cayley-Dickson
cayley_dickson_payload = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "compute_high_dimensional",
        "arguments": {
            "framework": "cayley-dickson",
            "operation": "is_zero_divisor",
            "dimension": 32,
            "operands": [operand1_coeffs, operand2_coeffs]
        }
    }
}

# Save the payload to a file
with open("C:\\Users\\chave\\PROJECTS\\cailculator-mcp\\cayley_dickson_zero_divisor_check.json", 'w') as f:
    json.dump(cayley_dickson_payload, f, indent=2)

print("Successfully created cayley_dickson_zero_divisor_check.json")
