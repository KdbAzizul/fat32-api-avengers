#!/bin/bash

# Target URL
URL="http://localhost:8000/api/v1/auth/register"

echo "--- Registering New User ---"
echo "Target: $URL"

curl -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "donor@example.com",
           "password": "password123",
           "full_name": "John Doe",  
           "role": "DONOR"
         }' \
     -w "\n\nHTTP Status Code: %{http_code}\n"