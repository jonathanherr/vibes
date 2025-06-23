import React, { useState, useEffect } from 'react';
import { useLLM } from '../../hooks/useLLM';
import { ChatSettings } from '../../types';

const LLMSettings: React.FC = () => {
  const {
    settings,
    switchLLM,
    updateGeminiConfig,
    updateVLLMConfig,
    currentProvider,
    isConfigured
  } = useLLM();

  const [showSettings, setShowSettings] = useState(false);
  const [localSettings, setLocalSettings] = useState<ChatSettings>(settings);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Update local settings when global settings change
  useEffect(() => {
    setLocalSettings(settings);
    setHasUnsavedChanges(false);
  }, [settings]);

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

  const handleSave = () => {
    // Apply all changes to global settings
    switchLLM(localSettings.selectedLLM);
    updateGeminiConfig(localSettings.geminiConfig);
    updateVLLMConfig(localSettings.vllmConfig);
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
                <select
                  value={localSettings.geminiConfig.model}
                  onChange={(e) => handleGeminiConfigUpdate({ model: e.target.value })}
                >
                  <option value="gemini-pro">gemini-pro</option>
                  <option value="gemini-pro-vision">gemini-pro-vision</option>
                </select>
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