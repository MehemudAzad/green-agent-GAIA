# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Multi-stage Dockerfile for Green GAIA Agent

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# Copy application code
COPY agent/ ./agent/
COPY purple_baseline/ ./purple_baseline/
COPY data/ ./data/
COPY tests/ ./tests/

# Create results directory
RUN mkdir -p /app/results

# Set random seed for reproducibility
ENV RANDOM_SEED=42

# Expose port for purple agent mock server
EXPOSE 8080

# Default command runs the evaluator
CMD ["python", "-m", "agent.evaluator", \
     "--data-dir", "/app/data/gaia", \
     "--purple-agent-url", "http://localhost:8080", \
     "--results-dir", "/app/results"]
