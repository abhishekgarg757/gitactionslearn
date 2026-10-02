FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached between builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Run the app when the container starts
CMD ["python", "-m", "src.app"]
