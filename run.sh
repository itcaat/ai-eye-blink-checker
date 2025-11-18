#!/bin/bash
# Run script for AI Eye Blink Checker

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "🚀 Running with uv..."
    uv run blink-checker "$@"
# Check if venv exists
elif [ -d ".venv" ]; then
    echo "🚀 Running with venv..."
    .venv/bin/python -m blink_checker.main "$@"
# Try system Python
else
    echo "🚀 Running with system Python..."
    python3 -m blink_checker.main "$@"
fi

