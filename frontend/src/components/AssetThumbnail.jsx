import { useState } from 'react';
import { X, RefreshCw } from 'lucide-react';

export default function AssetThumbnail({ asset, onDelete, onRegenerate }) {
  const [regenerating, setRegenerating] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Delete this asset?')) return;

    try {
      const response = await fetch(`http://localhost:8002/assets/${asset.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        onDelete(asset.id);
      }
    } catch (err) {
      console.error('Failed to delete asset:', err);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const response = await fetch(`http://localhost:8002/assets/${asset.id}/regenerate`, {
        method: 'POST',
      });

      if (response.ok) {
        const updatedAsset = await response.json();
        onRegenerate(updatedAsset);
      }
    } catch (err) {
      console.error('Failed to regenerate asset:', err);
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div className="relative group w-32">
      <div className="w-32 h-32 border rounded overflow-hidden">
        <img
          src={`http://localhost:8002/${asset.file_path}?t=${Date.now()}`}
          alt={asset.filename}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EImage%3C/text%3E%3C/svg%3E';
          }}
        />
        {regenerating && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <RefreshCw className="w-8 h-8 text-white animate-spin" />
          </div>
        )}
      </div>
      
      {/* Auto-generated badge */}
      {asset.auto_generated && (
        <div className="absolute top-1 left-1 bg-blue-500 text-white text-xs px-1 py-0.5 rounded">
          AI
        </div>
      )}
      
      {/* Regenerate button for auto-generated assets */}
      {asset.auto_generated && (
        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className="absolute bottom-1 left-1 bg-green-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition disabled:opacity-50"
          title="Regenerate"
        >
          <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
        </button>
      )}
      
      {/* Delete button - only show for manually uploaded assets */}
      {!asset.auto_generated && (
        <button
          onClick={handleDelete}
          className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
          title="Delete"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      
      <p className="text-xs text-gray-600 mt-1 truncate w-full" title={asset.filename}>
        {asset.filename}
      </p>
    </div>
  );
}
