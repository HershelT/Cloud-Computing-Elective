# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=StockPortfolio.py
# ENV FLASK_RUN_PORT=8001
# Accept build argument for the API key
# ARG NINJA_API_KEY
# # Set environment variable for the API key
# ENV NINJA_API_KEY=${NINJA_API_KEY}

# Accept build argument for the port
# ARG PORT=5001
# ENV PORT=${PORT}

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001", "--debug"]
