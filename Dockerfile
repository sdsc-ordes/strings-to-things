# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (adjust if you know other libs are needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (if you really need uv)
RUN pip install uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-deps .

# Copy your FastAPI app code
COPY src/ ./src/
COPY .env .env

# Expose the port FastAPI will run on
EXPOSE 7514

# Run the FastAPI app
CMD ["uvicorn", "src.strings2things.app.main:app", "--host", "0.0.0.0", "--port", "7514"]
