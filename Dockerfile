FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Environment
ENV PYTHONUNBUFFERED=1
ENV ANTHROPIC_API_KEY=""
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run
CMD ["python", "src/main.py"]