#!/bin/bash

echo "🔧 Testing Gemini Image Proxy Setup"
echo "=================================="
echo

# Check if the backend proxy example exists
if [ -d "backend-proxy-example" ]; then
    echo "✅ Backend proxy example found"
    
    # Check if dependencies are installed
    if [ -f "backend-proxy-example/node_modules/.package-lock.json" ]; then
        echo "✅ Dependencies appear to be installed"
    else
        echo "⚠️  Dependencies not installed. Run: cd backend-proxy-example && npm install"
    fi
    
    # Check if .env file exists
    if [ -f "backend-proxy-example/.env" ]; then
        echo "✅ Environment file found"
        
        # Check if API key is configured (basic check)
        if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" backend-proxy-example/.env; then
            echo "⚠️  Please configure your Gemini API key in backend-proxy-example/.env"
        else
            echo "✅ Gemini API key appears to be configured"
        fi
    else
        echo "⚠️  Environment file not found. Copy backend-proxy-example/.env.example to .env"
    fi
    
    # Check if proxy server is running
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:3001/health" | grep -q "200"; then
        echo "✅ Proxy server is running on port 3001"
        
        # Test the image generation endpoint (with a simple prompt)
        echo "🧪 Testing image generation endpoint..."
        
        response=$(curl -s -X POST http://localhost:3001/api/generate-image \
            -H "Content-Type: application/json" \
            -d '{"prompt": "test"}' \
            --max-time 10 \
            --write-out "HTTPSTATUS:%{http_code}")
            
        http_code=$(echo $response | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
        body=$(echo $response | sed "s/HTTPSTATUS:[0-9]*//g")
        
        if [ "$http_code" = "200" ]; then
            echo "✅ Image generation endpoint is working!"
        elif [ "$http_code" = "500" ]; then
            echo "❌ Image generation failed - check API key configuration"
        else
            echo "⚠️  Image generation endpoint returned HTTP $http_code"
        fi
    else
        echo "❌ Proxy server is not running on port 3001"
        echo "   Start it with: cd backend-proxy-example && npm start"
    fi
    
else
    echo "❌ Backend proxy example not found"
fi

echo
echo "📖 For setup instructions, see:"
echo "   - IMAGE_GENERATION_SETUP.md"
echo "   - backend-proxy-example/README.md"
echo
echo "🌐 React app should be running at: http://localhost:3000"
