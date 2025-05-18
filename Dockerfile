FROM python:3.10-slim

# 1. Run everything from root
WORKDIR /

# 2. Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

# 3. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the Flask app into /
COPY service.py .

# 5. (Optional) Ensure / is on Python’s import path (usually implicit)
ENV PYTHONPATH=/

# 6. Launch Gunicorn from /, pointing at module:callable
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "service:app"]
