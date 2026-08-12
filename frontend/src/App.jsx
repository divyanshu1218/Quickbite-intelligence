import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TrendTracker from './components/TrendTracker';
import FilterPanel from './components/FilterPanel';
import SpotlightBar from './components/SpotlightBar';
import OnboardingTour from './components/OnboardingTour';
import OverviewView from './pages/OverviewView';
import PerformanceView from './pages/PerformanceView';
import StoresView from './pages/StoresView';
import ProductsView from './pages/ProductsView';
import ChannelsView from './pages/ChannelsView';
import IntelligenceView from './pages/IntelligenceView';
import { fetchOverview } from './services/api';

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [overviewData, setOverviewData] = useState(null);
  const [activeFilters, setActiveFilters] = useState({});
  const [activeQuery, setActiveQuery] = useState('');
  const [isTourOpen, setIsTourOpen] = useState(false);

  useEffect(() => {
    fetchOverview()
      .then(setOverviewData)
      .catch((err) => console.error('Failed to load overview for trend tracker:', err));

    // Auto-open Onboarding Tour for First-Time Users if not completed before
    const hasSeenTour = localStorage.getItem('quickbite_tour_completed');
    if (!hasSeenTour) {
      setIsTourOpen(true);
    }
  }, []);

  const handleResetFilters = () => {
    setActiveFilters({});
  };

  const handleSpotlightSearch = (query) => {
    setActiveQuery(query);
    setActiveView('intelligence');
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa] text-charcoal-900 flex font-sans relative">
      {/* Fixed Sidebar */}
      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        onOpenTour={() => setIsTourOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-56 flex flex-col min-h-screen">
        {/* Sticky Live Trend Tracker Header */}
        <TrendTracker overviewData={overviewData} />

        {/* Dynamic Filter & Drill-Down Bar */}
        <FilterPanel
          activeFilters={activeFilters}
          onFilterChange={setActiveFilters}
          onReset={handleResetFilters}
        />

        {/* Main View Container */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {activeView === 'overview' && <OverviewView onNavigate={setActiveView} />}
          {activeView === 'performance' && <PerformanceView />}
          {activeView === 'stores' && <StoresView />}
          {activeView === 'products' && <ProductsView />}
          {activeView === 'channels' && <ChannelsView />}
          {activeView === 'intelligence' && <IntelligenceView initialQuery={activeQuery} />}
        </main>
      </div>

      {/* Floating Bottom-Right Google Gemini AI Spotlight Action Button */}
      <SpotlightBar
        onSearch={handleSpotlightSearch}
        placeholder="Ask QuickBite AI (e.g. 'How to increase revenue?')..."
      />

      {/* Guided First-Time User Experience (FTUE) Product Tour Modal */}
      <OnboardingTour
        isOpen={isTourOpen}
        onClose={() => setIsTourOpen(false)}
      />
    </div>
  );
}
