#!/bin/bash

# Test runner script for Mergington High School API

echo "🧪 Running Mergington High School API Tests..."
echo "=============================================="

# Set the Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests with coverage
echo "📊 Running tests with coverage report..."
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v

echo ""
echo "✅ Test run complete!"
echo "📋 Coverage report generated in htmlcov/ directory"
echo "🌐 Open htmlcov/index.html to view detailed coverage report"