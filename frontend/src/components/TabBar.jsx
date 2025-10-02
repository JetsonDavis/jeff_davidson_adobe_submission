import { X, Plus } from 'lucide-react';
import { useState } from 'react';

export default function TabBar({ tabs, activeTab, onTabChange, onTabClose, onTabAdd, onTabRename }) {
  const [editingTab, setEditingTab] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleDoubleClick = (tab) => {
    setEditingTab(tab.id);
    setEditValue(tab.name);
  };

  const handleEditComplete = () => {
    if (editValue.trim() && editingTab) {
      onTabRename(editingTab, editValue.trim());
    }
    setEditingTab(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleEditComplete();
    } else if (e.key === 'Escape') {
      setEditingTab(null);
    }
  };

  return (
    <div className="bg-gray-100 border-b border-gray-300 px-2 py-1">
      <div className="flex items-center gap-1 flex-wrap">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            className={`
              group flex items-center gap-2 px-4 py-2 rounded-t-lg cursor-pointer
              transition-colors min-w-[180px] max-w-[240px]
              ${activeTab === tab.id 
                ? 'bg-white border-t-2 border-l-2 border-r-2 border-blue-500' 
                : 'bg-gray-200 hover:bg-gray-300'}
            `}
            onClick={() => onTabChange(tab.id)}
            onDoubleClick={() => handleDoubleClick(tab)}
          >
            {editingTab === tab.id ? (
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onBlur={handleEditComplete}
                onKeyDown={handleKeyDown}
                onClick={(e) => e.stopPropagation()}
                className="flex-1 px-1 py-0 text-sm font-medium border border-blue-500 rounded outline-none"
                autoFocus
              />
            ) : (
              <span className="flex-1 truncate text-sm font-medium">
                {tab.name}
              </span>
            )}
            {tabs.length > 1 && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onTabClose(tab.id);
                }}
                className="opacity-0 group-hover:opacity-100 hover:bg-gray-300 rounded p-1 transition-opacity"
              >
                <X size={14} />
              </button>
            )}
          </div>
        ))}
        <button
          onClick={onTabAdd}
          className="p-2 hover:bg-gray-200 rounded transition-colors"
          title="New Campaign"
        >
          <Plus size={18} />
        </button>
      </div>
    </div>
  );
}
