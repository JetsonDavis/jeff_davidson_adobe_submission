import { useState, useEffect } from 'react';
import { Upload, FileText } from 'lucide-react';

export default function BriefUpload({ onBriefCreated, onSubmitRef, onValidityChange }) {
  const [contentType, setContentType] = useState('text');
  const [content, setContent] = useState('');
  const [file, setFile] = useState(null);
  const [brand, setBrand] = useState('');
  const [productName, setProductName] = useState('');
  const [campaignMessage, setCampaignMessage] = useState('');
  const [selectedRegions, setSelectedRegions] = useState('');
  const [selectedDemographics, setSelectedDemographics] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('campaign_message', campaignMessage);
      formData.append('regions', selectedRegions);
      formData.append('demographics', selectedDemographics);

      // Add brand and product name fields
      if (brand) {
        formData.append('brand', brand);
      }
      if (productName) {
        formData.append('product_name', productName);
      }

      if (file) {
        formData.append('file', file);
      } else {
        formData.append('content', content);
      }

      const response = await fetch('http://localhost:8002/briefs', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create brief');
      }

      const brief = await response.json();
      onBriefCreated(brief);
    } catch (err) {
      setError(err.message);
      throw err; // Re-throw to allow parent to handle
    } finally {
      setLoading(false);
    }
  };

  // Expose submit handler to parent and track validity
  useEffect(() => {
    const valid = campaignMessage.trim() !== '' && 
                 selectedRegions.trim() !== '' && 
                 selectedDemographics.trim() !== '';
    
    console.log('Brief validation:', { campaignMessage, selectedRegions, selectedDemographics, valid });
    
    if (onSubmitRef) {
      onSubmitRef.current = {
        submit: handleSubmit,
        isLoading: () => loading
      };
    }
    
    // Notify parent of validity change
    if (onValidityChange) {
      onValidityChange(valid);
    }
  }, [campaignMessage, selectedRegions, selectedDemographics, loading, onSubmitRef, onValidityChange]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Upload Product Brief</h2>

      {/* Brand and Product Name inputs */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">Brand Name</label>
          <input
            type="text"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="e.g., Adidas"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Product Name</label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="e.g., Moonwalkers"
          />
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Brief Content</label>
          <div className="flex gap-4">
            <textarea
              className="flex-1 border rounded p-2"
              rows="4"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Type brief content here..."
              disabled={file !== null}
            />
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded p-4 w-48">
              <Upload className="w-8 h-8 text-gray-400 mb-2" />
              <label className="cursor-pointer text-blue-600 hover:text-blue-700 text-sm text-center">
                <span>or upload brief as text, markdown, or json file</span>
                <input
                  type="file"
                  className="hidden"
                  accept=".txt,.pdf,.docx"
                  onChange={(e) => setFile(e.target.files[0])}
                />
              </label>
              {file && (
                <div className="mt-2 text-sm text-gray-600 flex items-center gap-1">
                  <FileText className="w-4 h-4" />
                  {file.name}
                </div>
              )}
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Campaign Message</label>
          <input
            type="text"
            className="w-full border rounded p-2"
            value={campaignMessage}
            onChange={(e) => setCampaignMessage(e.target.value)}
            placeholder="e.g., Summer Sale - 20% Off!"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Target Regions (JSON)</label>
          <input
            type="text"
            className="w-full border rounded p-2"
            value={selectedRegions}
            onChange={(e) => setSelectedRegions(e.target.value)}
            placeholder='["US", "EU", "APAC"]'
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Demographics (JSON)</label>
          <input
            type="text"
            className="w-full border rounded p-2"
            value={selectedDemographics}
            onChange={(e) => setSelectedDemographics(e.target.value)}
            placeholder='["Young Professionals (25-35)", "Athletes (18-45)", "Tech Enthusiasts"]'
            required
          />
        </div>

      </div>
    </div>
  );
}
