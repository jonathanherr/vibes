#!/bin/bash

echo "🧪 Testing Gemini AI Proxy Server"
echo "================================"
echo

# Check if the proxy server is running
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:3001/health" | grep -q "200"; then
    echo "✅ Proxy server is running on port 3001"
    
    # Get health status
    echo "📊 Server Status:"
    curl -s "http://localhost:3001/health" | python3 -m json.tool 2>/dev/null || echo "Could not parse health response"
    echo
    
    # Test text generation endpoint (with timeout)
    echo "🤖 Testing text generation endpoint..."
    
    response=$(curl -s -X POST http://localhost:3001/api/generate-text \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Say hello in a friendly way"}' \
        --max-time 15 \
        --write-out "HTTPSTATUS:%{http_code}")
        
    http_code=$(echo $response | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo $response | sed "s/HTTPSTATUS:[0-9]*//g")
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Text generation endpoint is working!"
        echo "Response preview: $(echo $body | cut -c1-100)..."
    elif [ "$http_code" = "500" ]; then
        echo "❌ Text generation failed - check API key configuration"
        echo "Error: $body"
    else
        echo "⚠️  Text generation endpoint returned HTTP $http_code"
        echo "Response: $body"
    fi
    
    echo
    
    # Test image generation endpoint (with timeout)
    echo "🎨 Testing image generation endpoint..."
    
    response=$(curl -s -X POST http://localhost:3001/api/generate-image \
        -H "Content-Type: application/json" \
        -d '{"prompt": "A simple test image"}' \
        --max-time 20 \
        --write-out "HTTPSTATUS:%{http_code}")
        
    http_code=$(echo $response | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo $response | sed "s/HTTPSTATUS:[0-9]*//g")
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Image generation endpoint is working!"
        echo "Response preview: $(echo $body | cut -c1-100)..."
    elif [ "$http_code" = "500" ]; then
        echo "❌ Image generation failed - check API key configuration"
        echo "Error: $body"
    else
        echo "⚠️  Image generation endpoint returned HTTP $http_code"
        echo "Response: $body"
    fi
    
else
    echo "❌ Proxy server is not running on port 3001"
    echo "   Start it with: cd backend-proxy-example && npm start"
    echo "   Or install dependencies first: cd backend-proxy-example && npm install"
fi

echo
echo "📖 For complete setup instructions, see:"
echo "   - backend-proxy-example/README.md"
echo "   - IMAGE_GENERATION_SETUP.md"
