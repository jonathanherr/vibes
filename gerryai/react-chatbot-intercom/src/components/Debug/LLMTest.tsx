import React, { useState } from 'react';
import { LLMService } from '../../services/llmService';

const LLMTest: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

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
        model: 'gemini-pro',
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
      maxHeight: '300px',
      overflow: 'auto'
    }}>
      <h4>LLM Test</h4>
      <button onClick={testGemini} disabled={loading}>
        {loading ? 'Testing...' : 'Test Gemini API'}
      </button>
      {result && (
        <div style={{ 
          marginTop: '10px', 
          padding: '10px', 
          background: result.startsWith('ERROR') ? '#ffe6e6' : '#e6ffe6',
          border: `1px solid ${result.startsWith('ERROR') ? '#ffcccc' : '#ccffcc'}`,
          borderRadius: '4px',
          whiteSpace: 'pre-wrap'
        }}>
          {result}
        </div>
      )}
    </div>
  );
};

export default LLMTest;
