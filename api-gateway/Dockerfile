# FIX: Use Python 3.10 to ensure compatibility with grpcio/alembic
FROM python:3.10-slim

WORKDIR /app

# FIX: Install gcc and g++ (C++ compiler) for compiling grpcio/asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# FIX: Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Keep your original command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]