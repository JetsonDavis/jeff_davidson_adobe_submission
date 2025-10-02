import { RefreshCw, Check, Send, ChevronDown } from 'lucide-react';
import { useState } from 'react';

export default function CreativeCard({ creative, onUpdate }) {
  const [loading, setLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('Instagram');
  const [showDropdown, setShowDropdown] = useState(false);
  const approval = creative.approval || {};
  const isUS = creative.region === 'US';

  const platforms = ['Instagram', 'TikTok', 'Facebook', 'Signal'];

  const handleRegenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8002/creatives/${creative.id}/regenerate`, {
      });
      const updated = await response.json();
      onUpdate({ ...updated, approval: { ...approval, creative_approved: false, regional_approved: false } });
    } catch (err) {
      console.error('Failed to regenerate:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveCreative = async () => {
    console.log('Approve creative clicked');
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8002/creatives/${creative.id}/approve-creative`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const updatedApproval = await response.json();
      console.log('Updated approval:', updatedApproval);
      onUpdate({ ...creative, approval: updatedApproval });
    } catch (err) {
      console.error('Failed to approve creative:', err);
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveRegional = async () => {
    console.log('Approve regional clicked');
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8002/creatives/${creative.id}/approve-regional`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const updatedApproval = await response.json();
      console.log('Updated approval:', updatedApproval);
      onUpdate({ ...creative, approval: updatedApproval });
    } catch (err) {
      console.error('Failed to approve regional:', err);
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeploy = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8002/creatives/${creative.id}/deploy`, {
        method: 'POST',
      });
      const updatedApproval = await response.json();
      onUpdate({ ...creative, approval: updatedApproval });
    } catch (err) {
      console.error('Failed to deploy:', err);
    } finally {
      setLoading(false);
    }
  };

  const canDeploy = isUS 
    ? approval.creative_approved && !approval.deployed
    : approval.creative_approved && approval.regional_approved && !approval.deployed;

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="mb-2 flex gap-2 flex-wrap">
        {creative.region && (
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-semibold">
            {creative.region}
          </span>
        )}
        {creative.demographic && (
          <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-semibold">
            {creative.demographic}
          </span>
        )}
        <span className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded font-semibold">
          {creative.aspect_ratio}
        </span>
      </div>
      <div className="bg-gray-200 rounded mb-3 overflow-hidden h-64 flex items-center justify-center">
        <img
          src={`http://localhost:8002/${creative.file_path}`}
          alt={`Creative ${creative.aspect_ratio}`}
          className={`${
            creative.aspect_ratio === '16:9' ? 'w-full h-auto' :
            creative.aspect_ratio === '9:16' ? 'h-full w-auto' :
            'h-full w-auto'
          }`}
          crossOrigin="anonymous"
          onLoad={(e) => {
            console.log('✅ Image loaded successfully:', e.target.src);
          }}
          onError={(e) => {
            console.error('❌ Image load error:', e.target.src);
            console.error('❌ Image natural width:', e.target.naturalWidth);
            console.error('❌ Image natural height:', e.target.naturalHeight);
            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EError Loading%3C/text%3E%3C/svg%3E';
          }}
        />
      </div>

      <div className="flex gap-2 mb-3 justify-between">
        <button
          onClick={handleApproveCreative}
          disabled={loading || approval.deployed}
          className={`flex-1 flex items-center justify-center gap-1 px-2 py-1 rounded text-sm ${
            approval.creative_approved
              ? 'bg-green-100 text-green-800 hover:bg-green-200'
              : 'border hover:bg-gray-50'
          } disabled:opacity-50`}
        >
          <Check className="w-4 h-4" />
          {approval.creative_approved ? 'Creative ✓' : 'Approve Creative'}
        </button>
        {!isUS && (
          <button
            onClick={handleApproveRegional}
            disabled={loading || approval.deployed}
            className={`flex-1 flex items-center justify-center gap-1 px-2 py-1 rounded text-sm ${
              approval.regional_approved
                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                : 'border hover:bg-gray-50'
            } disabled:opacity-50`}
          >
            <Check className="w-4 h-4" />
            {approval.regional_approved ? 'Regional ✓' : 'Approve Regional'}
          </button>
        )}
      </div>

      <div className="relative">
        <div className="flex">
          <button
            onClick={handleDeploy}
            disabled={loading || !canDeploy}
            className={`flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-l ${
              canDeploy
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500'
            } disabled:opacity-50`}
          >
            <Send className="w-4 h-4" />
            {approval.deployed ? 'DEPLOYED' : `Deploy to ${selectedPlatform}`}
          </button>
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            disabled={loading || !canDeploy}
            className={`px-2 border-l border-blue-700 rounded-r ${
              canDeploy
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500'
            } disabled:opacity-50`}
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
        
        {showDropdown && (
          <div className="absolute bottom-full mb-1 w-full bg-white border border-gray-300 rounded shadow-lg z-10">
            {platforms.map((platform) => (
              <button
                key={platform}
                onClick={() => {
                  setSelectedPlatform(platform);
                  setShowDropdown(false);
                }}
                className={`w-full px-4 py-2 text-left hover:bg-blue-50 ${
                  selectedPlatform === platform ? 'bg-blue-100 font-semibold' : ''
                }`}
              >
                {platform}
              </button>
            ))}
          </div>
        )}
      </div>

      {approval.deployed && (
        <div className="mt-2 bg-green-100 text-green-800 text-center py-2 rounded font-medium">
          ✓ DEPLOYED to {selectedPlatform}
        </div>
      )}
    </div>
  );
}
