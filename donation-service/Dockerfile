# FIX: Use Python 3.10
FROM python:3.10-slim

WORKDIR /app

# FIX: Install compilers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# FIX: Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Keep your specific copy structure
COPY ./app ./app
# You likely need the other files too (like alembic.ini or .env), so I recommend adding this:
COPY . .

# CHANGE THIS PORT based on the service (8002 for Campaign, 8003 for Donation)
EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]