FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt . 
# Copies requirements.txt from your project folder (the build context) into the container's current directory (/app, because of WORKDIR).
RUN pip install --no-cache-dir -r requirements.txt

# copy all code from main.py and src folder into the container's current directory (/app)
COPY main.py .
COPY src ./src
CMD ["python", "main.py"]