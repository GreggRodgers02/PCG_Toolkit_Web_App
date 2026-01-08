# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13.5


# Stage 1: Build the React Frontend
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the frontend source code
COPY frontend/ .

# Build the frontend assets
RUN npm run build


# Stage 2: Build the Python Backend
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the built frontend assets from the previous stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
# Note: removed --reload for production stability. valid for 'docker compose up' usage.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
