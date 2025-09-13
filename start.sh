#!/bin/bash

# Initialize vector store if it doesn't exist
if [ ! -d "chroma_langchain_db" ] || [ ! -f "chroma_langchain_db/chroma.sqlite3" ]; then
    echo "Initializing vector store..."
    python -c "from rag.embedding import initialize_vector_store; initialize_vector_store()"
fi

# Start the application
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
