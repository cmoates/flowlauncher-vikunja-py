#!/bin/bash
# Vendor dependencies locally for testing
# This mimics what the release workflow does

echo "Installing vendored dependencies locally..."
mkdir -p lib

# Install from requirements.txt, excluding dev/test packages
pip install \
  requests>=2.28.0 \
  pyflowlauncher>=0.10.0 \
  python-dateutil>=2.8.2 \
  --target ./lib \
  --upgrade

# Clean up cache
find ./lib -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ./lib -name "*.pyc" -delete 2>/dev/null || true

echo "✓ Dependencies vendored in ./lib"
echo "✓ Note: lib/ is ignored by git (see .gitignore)"
