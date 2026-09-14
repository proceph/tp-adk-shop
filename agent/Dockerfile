FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shop_agent/ et tests/ sont montés en volume par docker-compose :
# tu édites dans ton IDE, le conteneur voit tes changements immédiatement.

EXPOSE 8000
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000", "/app"]
