# Use Apify's Python base image
FROM apify/actor-python:3.12

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Set the entry point to run the Python script
CMD ["python3", "src/main.py"]

