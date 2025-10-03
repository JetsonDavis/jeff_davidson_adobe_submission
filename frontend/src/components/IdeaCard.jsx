import { useState } from 'react';
import { RefreshCw, Play, Trash2, Loader2 } from 'lucide-react';

export default function IdeaCard({ idea, onRegenerate, onGenerateCreative, onDelete }) {
  const [loading, setLoading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [generatingCreatives, setGeneratingCreatives] = useState(false);
  const [creativePlaceholders, setCreativePlaceholders] = useState([]);
  
  console.log('IdeaCard render - regenerating:', regenerating, 'loading:', loading, 'generatingCreatives:', generatingCreatives, 'placeholders:', creativePlaceholders.length);

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
      setRegenerating(false);
    }
  };

  const handleGenerateCreative = async () => {
    console.log('=== GENERATE CREATIVE CLICKED ===');
    console.log('Idea ID:', idea.id);
    
    setLoading(true);
    setGeneratingCreatives(true);
    
    // Create placeholders for 3 creatives immediately
    const placeholders = [
      { aspect_ratio: '16:9', loading: true },
      { aspect_ratio: '9:16', loading: true },
      { aspect_ratio: '1:1', loading: true }
    ];
    setCreativePlaceholders(placeholders);
    console.log('✅ Placeholders set:', placeholders);
    console.log('✅ generatingCreatives set to true');
    
    const creatives = [];
    
    try {
      console.log('📤 Starting streaming request for creatives...');
      const response = await fetch(`http://localhost:8002/ideas/${idea.id}/generate-creative`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('✅ === STREAM COMPLETE ===');
          setLoading(false);
          setGeneratingCreatives(false);
          setCreativePlaceholders([]);
          break;
        }
        
        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages (separated by \n\n)
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || ''; // Keep incomplete message in buffer
        
        for (const message of messages) {
          if (!message.trim()) continue;
          
          // Parse SSE format: "event: type\ndata: json"
          const lines = message.split('\n');
          let eventType = 'message';
          let eventData = '';
          
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.substring(7).trim();
            } else if (line.startsWith('data: ')) {
              eventData = line.substring(6).trim();
            }
          }
          
          if (!eventData) continue;
          
          try {
            const data = JSON.parse(eventData);
            
            if (eventType === 'progress') {
              console.log(`⏳ Progress: Generating ${data.aspect_ratio} (${data.current}/${data.total})...`);
            } else if (eventType === 'creative') {
              console.log(`✅ Creative received: ${data.aspect_ratio} - ${data.file_path}`);
              creatives.push(data);
              
              // Update placeholder with actual creative
              setCreativePlaceholders(prev => 
                prev.map(p => 
                  p.aspect_ratio === data.aspect_ratio 
                    ? { ...data, loading: false }
                    : p
                )
              );
              
              // Display creative immediately as it arrives
              console.log('📤 Calling onGenerateCreative with new creative...');
              onGenerateCreative([data]);
            } else if (eventType === 'error') {
              console.error(`❌ Error generating ${data.aspect_ratio}:`, data.error);
            } else if (eventType === 'complete') {
              console.log(`✅ Generation complete: ${data.total} creatives`);
            }
          } catch (parseError) {
            console.error('❌ Failed to parse SSE data:', eventData, parseError);
          }
        }
      }
      
    } catch (err) {
      console.error('❌ Failed to generate creative:', err);
      console.error('❌ Error details:', err.message);
      alert(`Failed to generate all creatives: ${err.message}`);
      setLoading(false);
      setGeneratingCreatives(false);
      setCreativePlaceholders([]);
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
        <>
          <p className={`mb-4 ${hasError ? 'text-red-700' : 'text-gray-700'}`}>{idea.content}</p>
          
          {/* Creative placeholders grid */}
          {(() => {
            console.log('Checking grid render:', { generatingCreatives, placeholderCount: creativePlaceholders.length });
            return generatingCreatives && creativePlaceholders.length > 0;
          })() && (
            <div className="mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-2">Generating Creatives:</p>
              <div className="grid grid-cols-3 gap-4">
                {creativePlaceholders.map((placeholder, index) => (
                  <div key={index} className="border rounded-lg p-3 bg-gray-50">
                    <div className="text-xs font-semibold text-purple-800 bg-purple-100 px-2 py-1 rounded mb-2 inline-block">
                      {placeholder.aspect_ratio}
                    </div>
                    {placeholder.loading ? (
                      <div className="bg-gray-200 rounded mb-2 h-32 flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                      </div>
                    ) : (
                      <div className="bg-gray-200 rounded mb-2 h-32 overflow-hidden flex items-center justify-center">
                        <img
                          src={`http://localhost:8002/${placeholder.file_path}?t=${Date.now()}`}
                          alt={`Creative ${placeholder.aspect_ratio}`}
                          className={`${
                            placeholder.aspect_ratio === '16:9' ? 'w-full h-auto' :
                            placeholder.aspect_ratio === '9:16' ? 'h-full w-auto' :
                            'h-full w-auto'
                          }`}
                          crossOrigin="anonymous"
                        />
                      </div>
                    )}
                    <p className="text-xs text-gray-600 text-center">
                      {placeholder.loading ? 'Generating...' : '✓ Ready'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
      
      {!isLoading && !generatingCreatives && (
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
