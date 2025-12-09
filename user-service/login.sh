#!/bin/bash

# Configuration
# Based on your screenshot
URL="http://localhost:8000/api/v1/auth/login"

echo "--- Logging in ---"
echo "Target: $URL"

curl -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "donor@example.com",
           "password": "password123"
         }' \
     -w "\n\nHTTP Status Code: %{http_code}\n"