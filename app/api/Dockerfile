
FROM python:3.9-slim

# Set working directory
WORKDIR /app/api

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8765

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765"]