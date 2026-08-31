# Dockerfile
# Builds the FastAPI backend image (Application Tier).
#
# Layer order is optimised for cache efficiency:
#   1. Install Python deps from requirements.txt  (invalidated only when deps change)
#   2. Copy application source                    (invalidated on any code change)

FROM python:3.12-slim

# Set the working directory for all subsequent instructions
WORKDIR /app

# Install dependencies first — this layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
 && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source
COPY . .

# Expose the port Uvicorn listens on (matched in docker-compose.yml)
EXPOSE 8000

# Default command — can be overridden by docker-compose command: directive.
# In production the compose file prepends `alembic upgrade head &&` before this.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
