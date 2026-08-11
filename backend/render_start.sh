#!/usr/bin/env bash
set -e

echo "=== Starting Render Production Boot Script for GitLab Documentation Helper ==="

# Determine Ollama service URL & Model
OLLAMA_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
MODEL_NAME="${OLLAMA_MODEL_NAME:-llama3.2:1b}"

echo "Target Ollama URL: ${OLLAMA_URL}"
echo "Target Ollama Model: ${MODEL_NAME}"

# If running against local daemon on Render Linux container, ensure Ollama binary & service are running
if [[ "${OLLAMA_URL}" == *"127.0.0.1"* || "${OLLAMA_URL}" == *"localhost"* ]]; then
    if ! command -v ollama &> /dev/null; then
        echo "Installing Ollama CLI in Render Linux container..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Ollama CLI is already installed."
    fi

    echo "Starting Ollama daemon in background..."
    ollama serve &
    OLLAMA_PID=$!

    echo "Waiting for Ollama daemon readiness..."
    MAX_WAIT=30
    WAIT_COUNT=0
    until curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1 || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        echo "Waiting for Ollama... (${WAIT_COUNT}s)"
    done

    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo "WARNING: Ollama daemon did not respond within ${MAX_WAIT}s. Proceeding..."
    else
        echo "Ollama daemon is ONLINE!"
        echo "Ensuring model '${MODEL_NAME}' is available..."
        ollama pull "${MODEL_NAME}" || echo "Ollama model pull completed or already loaded."
    fi
fi

# Launch FastAPI Backend Server
echo "Starting FastAPI Backend Server on port ${PORT:-8000}..."
exec python backend/run.py
