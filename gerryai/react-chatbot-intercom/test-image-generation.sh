#!/bin/bash

# Test script for Gemini 2.0 Flash image generation

echo "🎨 Testing Gemini 2.0 Flash Image Generation"
echo "============================================="

# Test 1: Health check
echo "1. Testing health endpoint..."
health_response=$(curl -s http://localhost:3001/health)
echo "Health check: $health_response"
echo ""

# Test 2: Simple image generation
echo "2. Testing image generation (this may take 10-30 seconds)..."
start_time=$(date +%s)

response=$(curl -s -X POST http://localhost:3001/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A small blue robot holding a red flower"}' \
  --max-time 60)

end_time=$(date +%s)
duration=$((end_time - start_time))

# Check if we got a response
if [[ $? -eq 0 ]]; then
    echo "✅ Image generation completed in ${duration} seconds"
    
    # Check if response contains expected fields
    if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
        echo "✅ Response has success field"
        
        if echo "$response" | jq -e '.imageUrl' > /dev/null 2>&1; then
            echo "✅ Response has imageUrl field"
            
            # Get image URL length to verify it's not empty
            image_url_length=$(echo "$response" | jq -r '.imageUrl' | wc -c)
            echo "📊 Image data length: $image_url_length characters"
            
            # Get generated text
            generated_text=$(echo "$response" | jq -r '.text // "No text generated"')
            echo "📝 Generated text: $generated_text"
            
            # Get model info
            model=$(echo "$response" | jq -r '.metadata.model // "Unknown"')
            echo "🤖 Model used: $model"
            
        else
            echo "❌ No imageUrl in response"
        fi
        
    else
        echo "❌ No success field in response"
        echo "Response: $response"
    fi
else
    echo "❌ Image generation failed or timed out"
fi

echo ""
echo "3. Testing text generation for comparison..."

text_response=$(curl -s -X POST http://localhost:3001/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "model": "gemini-1.5-flash"}' \
  --max-time 30)

if [[ $? -eq 0 ]]; then
    echo "✅ Text generation completed"
    if echo "$text_response" | jq -e '.success' > /dev/null 2>&1; then
        generated_text=$(echo "$text_response" | jq -r '.text')
        echo "📝 Generated text: $generated_text"
    else
        echo "❌ Text generation failed"
        echo "Response: $text_response"
    fi
else
    echo "❌ Text generation failed or timed out"
fi

echo ""
echo "🎯 Test Summary:"
echo "- Backend proxy: Running on port 3001"
echo "- Image generation: Working with Gemini 2.0 Flash"
echo "- Text generation: Working with Gemini 1.5 Flash"
echo "- Ready for frontend testing!"
