FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY static/ ./static/

ENV PYTHONUNBUFFERED=1
ENV ANTHROPIC_API_KEY=""
ENV PORT=8000

EXPOSE 8000

CMD ["python", "src/main.py"]