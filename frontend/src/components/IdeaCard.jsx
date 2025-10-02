import { useState } from 'react';
import { RefreshCw, Play, Trash2, Loader2 } from 'lucide-react';

export default function IdeaCard({ idea, onRegenerate, onGenerateCreative, onDelete }) {
  const [loading, setLoading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  
  console.log('IdeaCard render - regenerating:', regenerating, 'loading:', loading);

  const handleDelete = async () => {
    if (!confirm('Delete this idea?')) return;
    
    try {
      const response = await fetch(`http://localhost:8002/ideas/${idea.id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        onDelete(idea.id);
      }
    } catch (err) {
      console.error('Failed to delete idea:', err);
    }
  };

  const handleRegenerate = async () => {
    console.log('Setting regenerating to true');
    setRegenerating(true);
    
    // Ensure minimum 3 seconds of spinner visibility
    const minDelay = new Promise(resolve => setTimeout(resolve, 3000));
    
    try {
      const response = await fetch(`http://localhost:8002/ideas/${idea.id}/regenerate`, {
        method: 'POST',
      });
      const updatedIdea = await response.json();
      
      // Wait for both the API call and minimum delay
      await minDelay;
      
      onRegenerate(updatedIdea);
    } catch (err) {
      console.error('Failed to regenerate:', err);
      await minDelay; // Still wait even on error
      alert('Failed to generate new idea');
    } finally {
      setRegenerating(false);
    }
  };

  const handleGenerateCreative = async () => {
    console.log('🎨 === GENERATE CREATIVE START ===');
    console.log('Idea ID:', idea.id);
    console.log('Idea Content:', idea.content);
    setLoading(true);
    
    // Ensure minimum 2 seconds of spinner visibility
    const minDelay = new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      console.log('📡 Making API request to generate creatives...');
      const response = await fetch(`http://localhost:8002/ideas/${idea.id}/generate-creative`, {
        method: 'POST',
      });
      
      console.log('📊 Response status:', response.status);
      console.log('📊 Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API Error Response:', errorText);
        throw new Error(`API returned ${response.status}: ${errorText}`);
      }
      
      const creatives = await response.json(); // Now returns array of 3 creatives
      console.log('✅ Generated creatives count:', creatives.length);
      console.log('✅ Generated creatives:', creatives);
      creatives.forEach((c, i) => {
        console.log(`  Creative ${i + 1}: ${c.aspect_ratio} - ${c.file_path}`);
      });
      
      // Wait for both the API call and minimum delay
      await minDelay;
      
      console.log('📤 Calling onGenerateCreative callback...');
      onGenerateCreative(creatives);
      console.log('✅ === GENERATE CREATIVE COMPLETE ===');
    } catch (err) {
      console.error('❌ Failed to generate creative:', err);
      console.error('❌ Error details:', err.message);
      await minDelay; // Still wait even on error
      alert(`Failed to generate creatives: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Check if this is a loading placeholder
  const isLoading = idea.content === null && idea.isPlaceholder;
  const hasError = idea.hasError;

  return (
    <div className={`border rounded-lg p-4 shadow-sm ${
      isLoading ? 'bg-gray-50' : hasError ? 'bg-red-50' : 'bg-white'
    }`}>
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2">
            {idea.region}
          </span>
          <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
            {idea.demographic}
          </span>
        </div>
        {!isLoading && <span className="text-xs text-gray-500">v{idea.generation_count}</span>}
      </div>
      
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-8 mb-4">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-2" />
          <p className="text-sm text-gray-500">Generating idea...</p>
        </div>
      ) : (
        <p className={`mb-4 ${hasError ? 'text-red-700' : 'text-gray-700'}`}>{idea.content}</p>
      )}
      
      {!isLoading && (
        <div className="flex gap-2">
          <button
            onClick={handleRegenerate}
            disabled={regenerating || loading || hasError}
            className="flex items-center gap-1 px-3 py-2 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={regenerating ? 'w-4 h-4 animate-spin' : 'w-4 h-4'} />
            Regenerate
          </button>
          <button
            onClick={handleGenerateCreative}
            disabled={loading || regenerating || hasError}
            className="flex items-center gap-1 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Generate Creative
          </button>
          <button
            onClick={handleDelete}
            disabled={hasError}
            className="flex items-center gap-1 px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 ml-auto disabled:opacity-50"
            title="Delete idea"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
