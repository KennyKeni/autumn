FROM python:3.13-slim

# Install system dependencies for PostgreSQL compilation
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache --no-dev

# Copy the entire source code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "8000", "--host", "0.0.0.0"]