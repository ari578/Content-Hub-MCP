FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY content/ content/

# Expose port
ENV PORT=8787
EXPOSE 8787

# Run the server
CMD ["python", "-m", "src.server"]
