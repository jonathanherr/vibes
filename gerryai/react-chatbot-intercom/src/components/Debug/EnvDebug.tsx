import React from 'react';

const EnvDebug: React.FC = () => {
  const geminiApiKey = process.env.REACT_APP_GEMINI_API_KEY;
  const vllmBaseUrl = process.env.REACT_APP_VLLM_BASE_URL;

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '1px solid #ccc', 
      padding: '10px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <h4>Environment Debug</h4>
      <p><strong>Gemini API Key:</strong> {geminiApiKey ? `${geminiApiKey.substring(0, 10)}...` : 'NOT SET'}</p>
      <p><strong>vLLM Base URL:</strong> {vllmBaseUrl || 'NOT SET'}</p>
    </div>
  );
};

export default EnvDebug;
