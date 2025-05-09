#!/bin/bash

set -e

APP_NAME="dockit"

echo "🔨 Building binary..."
pyinstaller --onedir --clean --noconfirm --name "$APP_NAME" \
  --add-data "services:services" \
  --add-data "templates:templates" \
  app.py

echo "📦 Zipping build directory..."
cd dist
zip -r "${APP_NAME}.zip" "$APP_NAME"
cd ..

echo "✅ Build complete: dist/${APP_NAME}.zip"
