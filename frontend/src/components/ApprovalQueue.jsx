import { Trash2, RefreshCw, Save } from 'lucide-react';
import { useState } from 'react';
import CreativeCard from './CreativeCard';

export default function ApprovalQueue({ creatives, onCreativeUpdate }) {
  const [deleting, setDeleting] = useState(null);
  const [regenerating, setRegenerating] = useState(null);
  const [diskActive, setDiskActive] = useState(new Set()); // Track which rows have disk active
  const [generating, setGenerating] = useState(null);

  if (creatives.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No creatives yet. Generate ideas and create creatives to see them here.
      </div>
    );
  }

  // Group creatives by idea_id AND generation_count to give each batch its own row
  const groupedCreatives = creatives.reduce((acc, creative) => {
    const ideaId = creative.idea_id;
    const generationCount = creative.generation_count || 1;
    if (!ideaId) {
      console.warn('Creative missing idea_id:', creative);
      return acc;
    }
    // Create a unique key for each generation batch
    const groupKey = `${ideaId}_gen${generationCount}`;
    if (!acc[groupKey]) {
      acc[groupKey] = {
        ideaId: ideaId,
        generationCount: generationCount,
        creatives: []
      };
    }
    acc[groupKey].creatives.push(creative);
    return acc;
  }, {});

  // Check if we have any grouped creatives
  const hasGroupedCreatives = Object.keys(groupedCreatives).length > 0;
  
  if (!hasGroupedCreatives) {
    console.warn('No creatives could be grouped by idea_id', creatives);
    return (
      <div className="text-center py-12 text-gray-500">
        Unable to display creatives. Check console for details.
      </div>
    );
  }

  const handleRegenerateRow = async (ideaId) => {
    setRegenerating(ideaId);
    
    // Ensure minimum 3 seconds of spinner visibility
    const minDelay = new Promise(resolve => setTimeout(resolve, 3000));
    
    try {
      // Regenerate all creatives for this idea
      const response = await fetch(`http://localhost:8002/ideas/${ideaId}/generate-creative`, {
        method: 'POST',
      });
      
      if (response.ok) {
        await minDelay;
        onCreativeUpdate();
      } else {
        await minDelay;
        alert('Failed to regenerate creatives');
      }
    } catch (err) {
      console.error('Failed to regenerate creatives:', err);
      await minDelay;
      alert('Error regenerating creatives');
    } finally {
      setRegenerating(null);
    }
  };

  const handleDiskClick = async (ideaId) => {
    const newDiskActive = new Set(diskActive);
    
    if (diskActive.has(ideaId)) {
      // Second click - just toggle off, make ReGen visible again
      newDiskActive.delete(ideaId);
      setDiskActive(newDiskActive);
    } else {
      // First click - activate disk, hide ReGen, and generate new row with creatives
      newDiskActive.add(ideaId);
      setDiskActive(newDiskActive);
      setGenerating(ideaId);
      
      // Ensure minimum 3 seconds of spinner visibility
      const minDelay = new Promise(resolve => setTimeout(resolve, 3000));
      
      try {
        // Step 1: Duplicate the idea to create a new row
        const duplicateResponse = await fetch(`http://localhost:8002/ideas/${ideaId}/duplicate`, {
          method: 'POST',
        });
        
        if (!duplicateResponse.ok) {
          await minDelay;
          alert('Failed to duplicate idea');
          setGenerating(null);
          return;
        }
        
        const newIdea = await duplicateResponse.json();
        
        // Step 2: Generate creatives for the new duplicate idea
        const generateResponse = await fetch(`http://localhost:8002/ideas/${newIdea.id}/generate-creative`, {
          method: 'POST',
        });
        
        if (generateResponse.ok) {
          await minDelay;
          onCreativeUpdate();
        } else {
          await minDelay;
          alert('Failed to generate new creatives');
        }
      } catch (err) {
        console.error('Failed to create duplicate row:', err);
        await minDelay;
        alert('Error creating duplicate row');
      } finally {
        setGenerating(null);
      }
    }
  };

  const handleDeleteRow = async (groupKey) => {
    if (!confirm('Delete this set of creatives (all 3 aspect ratios)?')) {
      return;
    }

    setDeleting(groupKey);
    try {
      // Get the creatives for this specific group
      const group = groupedCreatives[groupKey];
      if (!group || !group.creatives) {
        alert('Invalid group');
        return;
      }

      // Delete each creative in this batch individually
      const deletePromises = group.creatives.map(creative =>
        fetch(`http://localhost:8002/creatives/${creative.id}`, {
          method: 'DELETE',
        })
      );

      const responses = await Promise.all(deletePromises);
      const allSuccessful = responses.every(r => r.ok);
      
      if (allSuccessful) {
        // Trigger update to refresh the list
        onCreativeUpdate();
      } else {
        alert('Failed to delete some creatives');
      }
    } catch (err) {
      console.error('Failed to delete creatives:', err);
      alert('Error deleting creatives');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="space-y-6">
      {Object.entries(groupedCreatives).map(([groupKey, group]) => {
        const { ideaId, generationCount, creatives: ideaCreatives } = group;
        const firstCreative = ideaCreatives[0];
        return (
          <div key={groupKey} className="relative">
            {/* Brief info header */}
            {(firstCreative.brand || firstCreative.product_name) && (
              <div className="mb-3 p-3 bg-gray-50 rounded-lg border">
                <div className="flex gap-4 text-sm text-gray-600">
                  {firstCreative.brand && (
                    <div>
                      <span className="font-medium">Brand:</span> {firstCreative.brand}
                    </div>
                  )}
                  {firstCreative.product_name && (
                    <div>
                      <span className="font-medium">Product:</span> {firstCreative.product_name}
                    </div>
                  )}
                  {generationCount > 1 && (
                    <div>
                      <span className="font-medium">Generation:</span> {generationCount}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="flex items-center gap-4">
              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {ideaCreatives.map((creative) => (
                  <CreativeCard
                    key={creative.id}
                    creative={creative}
                    onUpdate={onCreativeUpdate}
                  />
                ))}
              </div>
              <div className="flex flex-col gap-2 -mt-20">
                {!diskActive.has(groupKey) && (
                  <button
                    onClick={() => handleRegenerateRow(ideaId)}
                    disabled={regenerating === ideaId || deleting === groupKey || generating === ideaId}
                    className="flex-shrink-0 p-2 text-blue-600 hover:bg-blue-50 rounded disabled:opacity-50 transition-colors"
                    title="Regenerate all creatives for this idea"
                  >
                    <RefreshCw className={`w-5 h-5 ${regenerating === ideaId ? 'animate-spin' : ''}`} />
                  </button>
                )}
                <button
                  onClick={() => handleDiskClick(ideaId)}
                  disabled={regenerating === ideaId || deleting === groupKey || generating === ideaId}
                  className={`flex-shrink-0 p-2 rounded disabled:opacity-50 transition-colors ${
                    diskActive.has(groupKey)
                      ? 'bg-purple-600 text-white hover:bg-purple-700'
                      : 'text-purple-600 hover:bg-purple-50'
                  }`}
                  title="Generate new creative variations"
                >
                  <Save className={`w-5 h-5 ${generating === ideaId ? 'animate-spin' : ''}`} />
                </button>
                <button
                  onClick={() => handleDeleteRow(groupKey)}
                  disabled={deleting === groupKey || regenerating === ideaId || generating === ideaId}
                  className="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded disabled:opacity-50 transition-colors"
                  title="Delete this set of creatives"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
