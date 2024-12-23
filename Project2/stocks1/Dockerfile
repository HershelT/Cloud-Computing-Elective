FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# The name of the collection in the MongoDB database
ENV COLLECTION_NAME=stocks1
# The port on which the application will run
ENV PORT=8000
CMD ["python", "app.py"]