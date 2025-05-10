#!/bin/bash

set -e

APP_NAME="dockit"

echo "🔨 Building..."
cd "$(dirname "$0")"  # Ensure we're in the code directory
pyinstaller --onedir --clean --noconfirm --name "$APP_NAME" \
  --add-data "services:services" \
  --add-data "templates:templates" \
  app.py

echo "📦 Zipping binary output folder..."
cd dist
zip -r "${APP_NAME}.zip" "${APP_NAME}/"
cd ..

echo "Ready to release: dist/${APP_NAME}.zip"