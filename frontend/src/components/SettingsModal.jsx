import { useState, useEffect } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose }) {
  const [llmProvider, setLlmProvider] = useState('OpenAI');
  const [llmApiKey, setLlmApiKey] = useState('');
  const [imageProvider, setImageProvider] = useState('Adobe Firefly');
  const [imageApiKey, setImageApiKey] = useState('');

  // Adobe credentials
  const [adobeClientId, setAdobeClientId] = useState('');
  const [adobeClientSecret, setAdobeClientSecret] = useState('');
  const [adobeAccessToken, setAdobeAccessToken] = useState('');
  const [adobeOrgId, setAdobeOrgId] = useState('');

  const [settings, setSettings] = useState({
    instagram: { username: '', password: '' },
    tiktok: { username: '', password: '' },
    facebook: { username: '', password: '' },
    signal: { username: '', password: '' }
  });

  const [showPassword, setShowPassword] = useState({
    instagram: false,
    tiktok: false,
    facebook: false,
    signal: false
  });

  const [showApiKeys, setShowApiKeys] = useState({
    llm: false,
    image: false,
    adobeClientSecret: false,
    adobeAccessToken: false
  });

  // Fetch settings when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchSettings();
    }
  }, [isOpen]);

  const fetchSettings = async () => {
    try {
      const response = await fetch('http://localhost:8002/settings');
      const data = await response.json();
      const savedSettings = data.settings;
      
      // Load API provider settings
      if (savedSettings.llm_provider || savedSettings.use_llm) {
        const provider = savedSettings.use_llm || savedSettings.llm_provider;
        setLlmProvider(provider);
        // Load API key based on provider name
        if (savedSettings[provider]) {
          setLlmApiKey(savedSettings[provider]);
        }
      }
      
      if (savedSettings.image_provider || savedSettings.use_image_model) {
        const provider = savedSettings.use_image_model || savedSettings.image_provider;
        setImageProvider(provider);
        // Load API key based on provider name
        if (savedSettings[provider]) {
          setImageApiKey(savedSettings[provider]);
        }
      }

      // Load Adobe credentials
      if (savedSettings.adobe_client_id) setAdobeClientId(savedSettings.adobe_client_id);
      if (savedSettings.adobe_client_secret) setAdobeClientSecret(savedSettings.adobe_client_secret);
      if (savedSettings.adobe_jwt) setAdobeAccessToken(savedSettings.adobe_jwt);
      if (savedSettings.adobe_org_id) setAdobeOrgId(savedSettings.adobe_org_id);

      // Load platform credentials
      const platforms = ['instagram', 'tiktok', 'facebook', 'signal'];
      const newSettings = { ...settings };
      platforms.forEach(platform => {
        if (savedSettings[`${platform}_username`]) {
          newSettings[platform].username = savedSettings[`${platform}_username`];
        }
        if (savedSettings[`${platform}_password`]) {
          newSettings[platform].password = savedSettings[`${platform}_password`];
        }
      });
      setSettings(newSettings);
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    }
  };

  if (!isOpen) return null;

  const handleChange = (platform, field, value) => {
    setSettings({
      ...settings,
      [platform]: {
        ...settings[platform],
        [field]: value
      }
    });
  };

  const togglePasswordVisibility = (platform) => {
    setShowPassword({
      ...showPassword,
      [platform]: !showPassword[platform]
    });
  };

  const handleSave = async () => {
    try {
      const allSettings = {
        llm_provider: llmProvider,
        use_llm: llmProvider,
        image_provider: imageProvider,
        use_image_model: imageProvider,
        adobe_client_id: adobeClientId,
        adobe_client_secret: adobeClientSecret,
        adobe_jwt: adobeAccessToken,
        adobe_org_id: adobeOrgId
      };

      // Store LLM API key with provider name as key
      if (llmApiKey && llmApiKey.trim() !== '') {
        allSettings[llmProvider] = llmApiKey;
      }

      // Store Image API key with provider name as key
      if (imageApiKey && imageApiKey.trim() !== '') {
        allSettings[imageProvider] = imageApiKey;
      }

      // Add platform credentials
      Object.keys(settings).forEach(platform => {
        allSettings[`${platform}_username`] = settings[platform].username;
        allSettings[`${platform}_password`] = settings[platform].password;
      });
      
      await fetch('http://localhost:8002/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: allSettings })
      });
      
      onClose();
    } catch (err) {
      console.error('Failed to save settings:', err);
      alert('Error saving settings. Check console for details.');
    }
  };

  const platforms = [
    { key: 'instagram', name: 'Instagram' },
    { key: 'tiktok', name: 'TikTok' },
    { key: 'facebook', name: 'Facebook' },
    { key: 'signal', name: 'Signal' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center px-6 pt-6 border-b">
          <h2 className="text-2xl font-bold">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-100"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 -mt-5 space-y-0">
          {/* API Providers Section */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="text-lg font-semibold mb-4">API Providers</h3>
            
            {/* LLM Provider */}
            <div className="space-y-4 mb-4">
              <div className="grid gap-4" style={{ gridTemplateColumns: '1fr 2fr' }}>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    LLM Provider
                  </label>
                  <select
                    value={llmProvider}
                    onChange={(e) => setLlmProvider(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option>OpenAI</option>
                    <option>Anthropic</option>
                    <option>Gemini</option>
                    <option>Grok</option>
                    <option>DeepSeek</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showApiKeys.llm ? 'text' : 'password'}
                      value={llmApiKey}
                      onChange={(e) => setLlmApiKey(e.target.value)}
                      placeholder="API key"
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKeys({ ...showApiKeys, llm: !showApiKeys.llm })}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1"
                    >
                      {showApiKeys.llm ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Image Provider */}
            <div className="space-y-4">
              <div className="grid gap-4" style={{ gridTemplateColumns: '1fr 2fr' }}>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Image Provider
                  </label>
                  <select
                    value={imageProvider}
                    onChange={(e) => setImageProvider(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option>Adobe Firefly</option>
                    <option>OpenAI</option>
                    <option>DALL-E</option>
                    <option>Midjourney</option>
                    <option>Stable Diffusion</option>
                    <option>Freepik</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showApiKeys.image ? 'text' : 'password'}
                      value={imageApiKey}
                      onChange={(e) => setImageApiKey(e.target.value)}
                      placeholder="API key"
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKeys({ ...showApiKeys, image: !showApiKeys.image })}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1"
                    >
                      {showApiKeys.image ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Adobe Credentials Section */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="text-lg font-semibold mb-4">Adobe Credentials</h3>

            <div className="space-y-4">
              {/* Adobe Client ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client ID
                </label>
                <input
                  type="text"
                  value={adobeClientId}
                  onChange={(e) => setAdobeClientId(e.target.value)}
                  placeholder="Enter Adobe Client ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Adobe Client Secret */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Secret
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys.adobeClientSecret ? 'text' : 'password'}
                    value={adobeClientSecret}
                    onChange={(e) => setAdobeClientSecret(e.target.value)}
                    placeholder="Enter Adobe Client Secret"
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys({ ...showApiKeys, adobeClientSecret: !showApiKeys.adobeClientSecret })}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1"
                  >
                    {showApiKeys.adobeClientSecret ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Adobe Access Token */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Token
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys.adobeAccessToken ? 'text' : 'password'}
                    value={adobeAccessToken}
                    onChange={(e) => setAdobeAccessToken(e.target.value)}
                    placeholder="Enter Adobe Access Token"
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys({ ...showApiKeys, adobeAccessToken: !showApiKeys.adobeAccessToken })}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1"
                  >
                    {showApiKeys.adobeAccessToken ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Adobe Org ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization ID
                </label>
                <input
                  type="text"
                  value={adobeOrgId}
                  onChange={(e) => setAdobeOrgId(e.target.value)}
                  placeholder="Enter Adobe Org ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Platform Credentials Section */}
          {platforms.map(({ key, name }) => (
            <div key={key} className="border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">{name}</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    value={settings[key].username}
                    onChange={(e) => handleChange(key, 'username', e.target.value)}
                    placeholder={`Enter ${name} username`}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword[key] ? 'text' : 'password'}
                      value={settings[key].password}
                      onChange={(e) => handleChange(key, 'password', e.target.value)}
                      placeholder={`Enter ${name} password`}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility(key)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 p-1"
                    >
                      {showPassword[key] ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
