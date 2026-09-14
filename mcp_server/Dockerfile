FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# server.py est monté en volume : édite-le dans ton IDE.
EXPOSE 9000
CMD ["python", "server.py"]
