import { useState } from 'react';
import { Settings } from 'lucide-react';
import TabBar from '../components/TabBar';
import CampaignTab from '../components/CampaignTab';
import SettingsModal from '../components/SettingsModal';

export default function Dashboard() {
  const [tabs, setTabs] = useState([
    { id: 1, name: 'Campaign 1' }
  ]);
  const [activeTab, setActiveTab] = useState(1);
  const [nextTabId, setNextTabId] = useState(2);
  const [showSettings, setShowSettings] = useState(false);

  const handleTabAdd = () => {
    const newTab = {
      id: nextTabId,
      name: `Campaign ${nextTabId}`
    };
    setTabs([...tabs, newTab]);
    setActiveTab(nextTabId);
    setNextTabId(nextTabId + 1);
  };

  const handleTabClose = (tabId) => {
    if (tabs.length === 1) return; // Don't close last tab
    
    const newTabs = tabs.filter(tab => tab.id !== tabId);
    setTabs(newTabs);
    
    // If closing active tab, switch to another
    if (activeTab === tabId) {
      setActiveTab(newTabs[newTabs.length - 1].id);
    }
  };

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  const handleTabRename = (tabId, newName) => {
    setTabs(tabs.map(tab => 
      tab.id === tabId ? { ...tab, name: newName } : tab
    ));
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm flex-shrink-0">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Social Media Marketing Dashboard</h1>
            <p className="text-gray-600 mt-1">Create, manage, and deploy multi-regional social media campaigns</p>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings size={28} />
          </button>
        </div>
      </header>

      {/* Tab Bar */}
      <TabBar 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTabChange}
        onTabClose={handleTabClose}
        onTabAdd={handleTabAdd}
        onTabRename={handleTabRename}
      />

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`h-full ${activeTab === tab.id ? 'block' : 'hidden'}`}
          >
            <CampaignTab tabId={tab.id} />
          </div>
        ))}
      </div>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </div>
  );
}
