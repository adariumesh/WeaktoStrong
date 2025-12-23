#!/bin/bash

# Build script for Web Sandbox Docker image
# Creates a secure, lightweight container for testing web development challenges

set -e

echo "🚀 Building Web Sandbox Docker image..."

# Set image name and tag
IMAGE_NAME="weak-to-strong/web-sandbox"
TAG=${1:-"latest"}

echo "📦 Building image: ${IMAGE_NAME}:${TAG}"

# Build the Docker image
docker build \
  --tag "${IMAGE_NAME}:${TAG}" \
  --file Dockerfile \
  --progress=plain \
  .

# Get image size
IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${TAG}" --format "table {{.Size}}" | tail -n +2)

echo "✅ Build complete!"
echo "📊 Image size: ${IMAGE_SIZE}"

# Test the image
echo "🧪 Testing the image..."
docker run --rm "${IMAGE_NAME}:${TAG}" node --version

# Optional: Run a quick test
if [ "$2" = "--test" ]; then
  echo "🔍 Running validation test..."
  
  # Create a simple test HTML file
  cat > test.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            color: #333; 
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Page</h1>
        <p>This is a test page for validation.</p>
    </div>
</body>
</html>
EOF

  # Test the container
  docker run --rm -v "$(pwd)/test.html:/sandbox/user-code/index.html:ro" \
    "${IMAGE_NAME}:${TAG}" \
    node test-runner.js /sandbox/user-code/index.html
  
  # Clean up
  rm test.html
  
  echo "✅ Test completed successfully!"
fi

echo "🎉 Web Sandbox image ready: ${IMAGE_NAME}:${TAG}"