FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for numpy and psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# The port on which the application will run
ENV PORT=8080
# Expose the port
EXPOSE 8080

# The command to run the application
CMD ["python", "app.py"]