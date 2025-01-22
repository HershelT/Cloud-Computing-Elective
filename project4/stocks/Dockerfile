FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# The port on which the application will run
ENV PORT=8000
# The command to run the application
CMD ["python", "app.py"]