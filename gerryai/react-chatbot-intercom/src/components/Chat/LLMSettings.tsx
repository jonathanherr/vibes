import React, { useState, useEffect, useCallback } from 'react';
import { useLLM } from '../../hooks/useLLM';
import { ChatSettings } from '../../types';

const LLMSettings: React.FC = () => {
  const {
    settings,
    switchLLM,
    updateGeminiConfig,
    updateVLLMConfig,
    updateImageGenConfig,
    currentProvider,
    isConfigured,
    fetchGeminiModels
  } = useLLM();

  const [showSettings, setShowSettings] = useState(false);
  const [localSettings, setLocalSettings] = useState<ChatSettings>(settings);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>(['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']);
  const [loadingModels, setLoadingModels] = useState(false);

  // Update local settings when global settings change
  useEffect(() => {
    setLocalSettings(settings);
    setHasUnsavedChanges(false);
  }, [settings]);

  // Function to load available models
  const loadAvailableModels = useCallback(async () => {
    if (localSettings.selectedLLM === 'gemini' && localSettings.geminiConfig.apiKey) {
      setLoadingModels(true);
      try {
        const models = await fetchGeminiModels();
        setAvailableModels(models);
      } catch (error) {
        console.error('Failed to load models:', error);
        // Keep default models on error
      } finally {
        setLoadingModels(false);
      }
    }
  }, [localSettings.selectedLLM, localSettings.geminiConfig.apiKey, fetchGeminiModels]);

  // Load models when API key changes or provider switches to Gemini
  useEffect(() => {
    if (localSettings.selectedLLM === 'gemini' && localSettings.geminiConfig.apiKey) {
      loadAvailableModels();
    }
  }, [localSettings.selectedLLM, localSettings.geminiConfig.apiKey, loadAvailableModels]);

  // Helper functions to update local settings
  const handleProviderSwitch = (provider: 'gemini' | 'vllm') => {
    setLocalSettings(prev => ({
      ...prev,
      selectedLLM: provider
    }));
    setHasUnsavedChanges(true);
  };

  const handleGeminiConfigUpdate = (config: Partial<ChatSettings['geminiConfig']>) => {
    setLocalSettings(prev => ({
      ...prev,
      geminiConfig: { ...prev.geminiConfig, ...config }
    }));
    setHasUnsavedChanges(true);
  };

  const handleVLLMConfigUpdate = (config: Partial<ChatSettings['vllmConfig']>) => {
    setLocalSettings(prev => ({
      ...prev,
      vllmConfig: { ...prev.vllmConfig, ...config }
    }));
    setHasUnsavedChanges(true);
  };

  const handleImageGenConfigUpdate = (config: Partial<ChatSettings['imageGenConfig']>) => {
    setLocalSettings(prev => ({
      ...prev,
      imageGenConfig: { ...prev.imageGenConfig, ...config }
    }));
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    // Apply all changes to global settings
    switchLLM(localSettings.selectedLLM);
    updateGeminiConfig(localSettings.geminiConfig);
    updateVLLMConfig(localSettings.vllmConfig);
    updateImageGenConfig(localSettings.imageGenConfig);
    setHasUnsavedChanges(false);
  };

  const handleCancel = () => {
    // Reset local settings to global settings
    setLocalSettings(settings);
    setHasUnsavedChanges(false);
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      const confirmClose = window.confirm('You have unsaved changes. Close without saving?');
      if (!confirmClose) return;
      handleCancel();
    }
    setShowSettings(false);
  };

  return (
    <div className="llm-settings">
      <button 
        onClick={() => setShowSettings(!showSettings)}
        className="settings-toggle"
      >
        ⚙️ LLM Settings ({currentProvider}) {hasUnsavedChanges && '*'}
      </button>

      {showSettings && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3>LLM Configuration</h3>
            <button onClick={handleClose} className="close-button">×</button>
          </div>
          
          <div className="provider-selector">
            <h4>Choose LLM Provider</h4>
            <div className="provider-options">
              <label className={`provider-option ${localSettings.selectedLLM === 'gemini' ? 'active' : ''}`}>
                <input
                  type="radio"
                  value="gemini"
                  checked={localSettings.selectedLLM === 'gemini'}
                  onChange={() => handleProviderSwitch('gemini')}
                />
                <span>Google Gemini</span>
              </label>
              <label className={`provider-option ${localSettings.selectedLLM === 'vllm' ? 'active' : ''}`}>
                <input
                  type="radio"
                  value="vllm"
                  checked={localSettings.selectedLLM === 'vllm'}
                  onChange={() => handleProviderSwitch('vllm')}
                />
                <span>vLLM Server</span>
              </label>
            </div>
          </div>

          {localSettings.selectedLLM === 'gemini' && (
            <div className="gemini-config">
              <h4>Gemini Configuration</h4>
              <div className="config-field">
                <label>API Key:</label>
                <input
                  type="password"
                  value={localSettings.geminiConfig.apiKey}
                  onChange={(e) => handleGeminiConfigUpdate({ apiKey: e.target.value })}
                  placeholder="Enter your Gemini API key"
                />
              </div>
              <div className="config-field">
                <label>Model:</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <select
                    value={localSettings.geminiConfig.model}
                    onChange={(e) => handleGeminiConfigUpdate({ model: e.target.value })}
                    disabled={loadingModels}
                  >
                    {availableModels.map(model => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={loadAvailableModels}
                    disabled={loadingModels || !localSettings.geminiConfig.apiKey}
                    style={{
                      padding: '4px 8px',
                      fontSize: '12px',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      background: '#f9f9f9',
                      cursor: 'pointer'
                    }}
                  >
                    {loadingModels ? '⟳' : '🔄'} Refresh
                  </button>
                </div>
                {loadingModels && <div style={{ fontSize: '12px', color: '#666' }}>Loading models...</div>}
              </div>
              <div className="config-field">
                <label>Temperature: {localSettings.geminiConfig.temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localSettings.geminiConfig.temperature}
                  onChange={(e) => handleGeminiConfigUpdate({ temperature: parseFloat(e.target.value) })}
                />
              </div>
              <div className="config-field">
                <label>Proxy Base URL (Optional):</label>
                <input
                  type="text"
                  value={localSettings.geminiConfig.proxyBaseUrl || ''}
                  onChange={(e) => handleGeminiConfigUpdate({ proxyBaseUrl: e.target.value })}
                  placeholder="http://localhost:3001/api"
                />
                <small>If you have a backend proxy running, enter its base URL here to bypass CORS and rate limits.</small>
              </div>
            </div>
          )}

          {localSettings.selectedLLM === 'vllm' && (
            <div className="vllm-config">
              <h4>vLLM Configuration</h4>
              <div className="config-field">
                <label>Base URL:</label>
                <input
                  type="text"
                  value={localSettings.vllmConfig.baseUrl}
                  onChange={(e) => handleVLLMConfigUpdate({ baseUrl: e.target.value })}
                  placeholder="http://localhost:8000"
                />
              </div>
              <div className="config-field">
                <label>Model:</label>
                <input
                  type="text"
                  value={localSettings.vllmConfig.model}
                  onChange={(e) => handleVLLMConfigUpdate({ model: e.target.value })}
                  placeholder="llama-2-7b-chat"
                />
              </div>
              <div className="config-field">
                <label>Temperature: {localSettings.vllmConfig.temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localSettings.vllmConfig.temperature}
                  onChange={(e) => handleVLLMConfigUpdate({ temperature: parseFloat(e.target.value) })}
                />
              </div>
              <div className="config-field">
                <label>Max Tokens:</label>
                <input
                  type="number"
                  value={localSettings.vllmConfig.maxTokens}
                  onChange={(e) => handleVLLMConfigUpdate({ maxTokens: parseInt(e.target.value) })}
                  min="100"
                  max="4000"
                />
              </div>
            </div>
          )}

          {/* Image Generation Configuration */}
          <div className="image-gen-config">
            <h4>🎨 Image Generation</h4>
            <div className="config-field">
              <label>Provider:</label>
              <select
                value={localSettings.imageGenConfig.provider}
                onChange={(e) => handleImageGenConfigUpdate({ provider: e.target.value as 'gemini' | 'vllm' })}
              >
                <option value="gemini">Gemini (2.0 Flash)</option>
                <option value="vllm">vLLM Server</option>
              </select>
            </div>
            
            {localSettings.imageGenConfig.provider === 'gemini' && (
              <>
                <div className="config-field">
                  <label>Model:</label>
                  <select
                    value={localSettings.imageGenConfig.model}
                    onChange={(e) => handleImageGenConfigUpdate({ model: e.target.value })}
                  >
                    <option value="gemini-2.0-flash-preview-image-generation">Gemini 2.0 Flash Image Generation</option>
                    <option value="imagen-3.0-generate-002">Imagen 3 (SDK Only)</option>
                  </select>
                </div>
                <div className="config-field">
                  <label>Size:</label>
                  <select
                    value={`${localSettings.imageGenConfig.width}x${localSettings.imageGenConfig.height}`}
                    onChange={(e) => {
                      const [width, height] = e.target.value.split('x').map(Number);
                      handleImageGenConfigUpdate({ width, height });
                    }}
                  >
                    <option value="512x512">512x512 (Square)</option>
                    <option value="768x768">768x768 (Square)</option>
                    <option value="1024x1024">1024x1024 (Square)</option>
                    <option value="1024x768">1024x768 (Landscape)</option>
                    <option value="768x1024">768x1024 (Portrait)</option>
                  </select>
                </div>
                <div className="config-field">
                  <label>Backend Proxy URL (Optional):</label>
                  <input
                    type="text"
                    value={localSettings.imageGenConfig.proxyUrl || ''}
                    onChange={(e) => handleImageGenConfigUpdate({ proxyUrl: e.target.value })}
                    placeholder="http://localhost:3001/api/generate-image"
                  />
                  <small>If you have a backend proxy running, enter its URL here to enable real image generation.</small>
                </div>
                <div className="config-info">
                  <small>ℹ️ Note: Gemini 2.0 Flash supports image generation via REST API with a backend proxy.</small>
                  <br />
                  <small>⚠️ Imagen 3 requires SDK integration and is not available via REST API.</small>
                  <br />
                  <small>💡 For production: Use backend proxy URL above or vLLM option below.</small>
                </div>
              </>
            )}

            {localSettings.imageGenConfig.provider === 'vllm' && (
              <>
                <div className="config-field">
                  <label>Base URL:</label>
                  <input
                    type="text"
                    value={localSettings.imageGenConfig.baseUrl || ''}
                    onChange={(e) => handleImageGenConfigUpdate({ baseUrl: e.target.value })}
                    placeholder="http://localhost:8001"
                  />
                </div>
                <div className="config-field">
                  <label>Model:</label>
                  <input
                    type="text"
                    value={localSettings.imageGenConfig.model}
                    onChange={(e) => handleImageGenConfigUpdate({ model: e.target.value })}
                    placeholder="flux-1-schnell"
                  />
                </div>
                <div className="config-field">
                  <label>Steps: {localSettings.imageGenConfig.steps}</label>
                  <input
                    type="range"
                    min="10"
                    max="50"
                    step="1"
                    value={localSettings.imageGenConfig.steps}
                    onChange={(e) => handleImageGenConfigUpdate({ steps: parseInt(e.target.value) })}
                  />
                </div>
                <div className="config-field">
                  <label>Size:</label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <input
                      type="number"
                      value={localSettings.imageGenConfig.width}
                      onChange={(e) => handleImageGenConfigUpdate({ width: parseInt(e.target.value) })}
                      placeholder="512"
                      style={{ width: '80px' }}
                    />
                    <span>×</span>
                    <input
                      type="number"
                      value={localSettings.imageGenConfig.height}
                      onChange={(e) => handleImageGenConfigUpdate({ height: parseInt(e.target.value) })}
                      placeholder="512"
                      style={{ width: '80px' }}
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="config-status">
            {isConfigured() ? (
              <span className="status-ok">✅ Currently Configured</span>
            ) : (
              <span className="status-error">❌ Configuration Required</span>
            )}
          </div>

          <div className="settings-actions">
            <button 
              onClick={handleCancel} 
              disabled={!hasUnsavedChanges}
              className="cancel-button"
            >
              Cancel
            </button>
            <button 
              onClick={handleSave} 
              disabled={!hasUnsavedChanges}
              className="save-button"
            >
              Save & Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMSettings;