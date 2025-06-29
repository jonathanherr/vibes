import React, { useState } from 'react';
import { LLMService } from '../../services/llmService';
import { ImageGenService } from '../../services/imageGenService';

const LLMTest: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [imageResult, setImageResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);

  const testGemini = async () => {
    setLoading(true);
    setResult('');
    
    try {
      const apiKey = process.env.REACT_APP_GEMINI_API_KEY;
      console.log('Testing with API key:', apiKey ? `${apiKey.substring(0, 10)}...` : 'none');
      
      if (!apiKey) {
        setResult('ERROR: No API key found in environment variables');
        return;
      }

      const config = {
        provider: 'gemini' as const,
        apiKey,
        model: 'gemini-1.5-flash',
        temperature: 0.7
      };

      const service = new LLMService(config);
      const response = await service.generateResponse('Hello, please respond with a simple greeting.');
      
      setResult(`SUCCESS: ${response.text}`);
    } catch (error) {
      console.error('Test error:', error);
      setResult(`ERROR: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const testImageGeneration = async () => {
    setImageLoading(true);
    setImageResult('');
    
    try {
      const apiKey = process.env.REACT_APP_GEMINI_API_KEY;
      
      if (!apiKey) {
        setImageResult('ERROR: No API key found in environment variables');
        return;
      }

      const config = {
        provider: 'gemini' as const,
        apiKey,
        model: 'imagen-3.0-generate-001',
        width: 512,
        height: 512
      };

      const service = new ImageGenService(config);
      const imageUrl = await service.generateImage('A cute cat sitting on a sunny windowsill');
      
      setImageResult(imageUrl);
    } catch (error) {
      console.error('Image generation test error:', error);
      setImageResult(`ERROR: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setImageLoading(false);
    }
  };

  return (
    <div style={{ 
      position: 'fixed', 
      bottom: '10px', 
      right: '10px', 
      background: 'white', 
      border: '1px solid #ccc', 
      padding: '15px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '400px',
      maxHeight: '400px',
      overflow: 'auto'
    }}>
      <h4>LLM & Image Test</h4>
      
      <div style={{ marginBottom: '15px' }}>
        <button onClick={testGemini} disabled={loading}>
          {loading ? 'Testing...' : 'Test Gemini Text'}
        </button>
        {result && (
          <div style={{ 
            marginTop: '10px', 
            padding: '10px', 
            background: result.startsWith('ERROR') ? '#ffe6e6' : '#e6ffe6',
            border: `1px solid ${result.startsWith('ERROR') ? '#ffcccc' : '#ccffcc'}`,
            borderRadius: '4px',
            whiteSpace: 'pre-wrap',
            maxHeight: '100px',
            overflow: 'auto'
          }}>
            {result}
          </div>
        )}
      </div>

      <div>
        <button onClick={testImageGeneration} disabled={imageLoading}>
          {imageLoading ? 'Generating...' : 'Test Gemini Imagen'}
        </button>
        {imageResult && (
          <div style={{ 
            marginTop: '10px', 
            padding: '10px', 
            background: imageResult.startsWith('ERROR') ? '#ffe6e6' : '#e6ffe6',
            border: `1px solid ${imageResult.startsWith('ERROR') ? '#ffcccc' : '#ccffcc'}`,
            borderRadius: '4px'
          }}>
            {imageResult.startsWith('ERROR') ? (
              imageResult
            ) : imageResult.startsWith('data:image') ? (
              <img 
                src={imageResult} 
                alt="Generated test content" 
                style={{ maxWidth: '200px', maxHeight: '200px' }}
              />
            ) : (
              'Image generated successfully'
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LLMTest;
