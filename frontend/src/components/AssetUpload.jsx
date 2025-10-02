import { useState } from 'react';
import { Upload } from 'lucide-react';

export default function AssetUpload({ assetType, onAssetUploaded }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`http://localhost:8002/assets/${assetType}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload asset');
      }

      const asset = await response.json();
      onAssetUploaded(asset);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
      <label className="cursor-pointer">
        <span className="text-blue-600 hover:text-blue-700 font-medium">
          Upload {assetType === 'brand' ? 'Brand' : 'Product'} Asset
        </span>
        <input
          type="file"
          accept="image/jpeg,image/png"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>
      <p className="text-sm text-gray-500 mt-2">JPG or PNG, max 10MB</p>
      
      {uploading && <p className="text-blue-600 mt-2">Uploading...</p>}
      {error && <p className="text-red-600 mt-2 text-sm">{error}</p>}
    </div>
  );
}
