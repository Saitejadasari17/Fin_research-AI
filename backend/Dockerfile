FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing bytecode and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=.

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose default port
EXPOSE 8000

# Start server using dynamic PORT env var or default 8000
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
