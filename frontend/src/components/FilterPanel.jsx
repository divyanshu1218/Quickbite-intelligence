import { useState } from 'react';
import { Filter, X, RotateCcw, Bookmark, ChevronRight } from 'lucide-react';

const CITIES = ['Mumbai', 'Pune', 'Bengaluru', 'Delhi', 'Hyderabad'];
const CHANNELS = ['Swiggy', 'Zomato', 'Dine-in', 'Takeaway'];
const FORMATS = ['Dine-In', 'Express', 'Food Court', 'Drive-Thru'];

export default function FilterPanel({ activeFilters, onFilterChange, onReset }) {
  const [isOpen, setIsOpen] = useState(false);
  const [savedViews, setSavedViews] = useState([
    { name: 'Pune High-Volume Stores', filters: { cities: ['Pune'], channels: ['Swiggy'] } },
    { name: 'Dine-In Performance', filters: { channels: ['Dine-in'] } },
  ]);

  const toggleFilter = (type, val) => {
    const current = activeFilters[type] || [];
    const updated = current.includes(val)
      ? current.filter((item) => item !== val)
      : [...current, val];
    onFilterChange({ ...activeFilters, [type]: updated });
  };

  const activeBreadcrumbs = [
    ...(activeFilters.cities || []).map((c) => ({ type: 'City', val: c })),
    ...(activeFilters.channels || []).map((ch) => ({ type: 'Channel', val: ch })),
    ...(activeFilters.formats || []).map((f) => ({ type: 'Format', val: f })),
  ];

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-2.5 flex items-center justify-between gap-4">
      {/* Breadcrumb Trail */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
            isOpen || activeBreadcrumbs.length > 0
              ? 'bg-brand-50 text-brand-700 border-brand-200'
              : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
          }`}
        >
          <Filter size={13} />
          Filter Data
          {activeBreadcrumbs.length > 0 && (
            <span className="w-4 h-4 rounded-full bg-brand-600 text-white text-2xs flex items-center justify-center font-bold">
              {activeBreadcrumbs.length}
            </span>
          )}
        </button>

        {/* Active Filter Pills / Breadcrumbs */}
        {activeBreadcrumbs.map((crumb, idx) => (
          <div key={idx} className="flex items-center gap-1.5">
            {idx > 0 && <ChevronRight size={12} className="text-gray-300" />}
            <span className="inline-flex items-center gap-1 bg-gray-100 border border-gray-200 text-gray-700 px-2.5 py-1 rounded-full text-xs font-medium">
              <span className="text-gray-400 text-2xs">{crumb.type}:</span> {crumb.val}
              <X
                size={11}
                className="cursor-pointer text-gray-400 hover:text-gray-600"
                onClick={() => toggleFilter(crumb.type.toLowerCase() + 's', crumb.val)}
              />
            </span>
          </div>
        ))}

        {activeBreadcrumbs.length > 0 && (
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-2xs text-gray-400 hover:text-red-500 font-medium px-2 py-1"
          >
            <RotateCcw size={11} />
            Reset all
          </button>
        )}
      </div>

      {/* Filter Drawer Toggle */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-2xl border-l border-gray-200 z-50 p-6 space-y-6 overflow-y-auto">
          <div className="flex items-center justify-between pb-4 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-charcoal-900 flex items-center gap-2">
              <Filter size={15} /> Dimension Filters
            </h3>
            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600">
              <X size={18} />
            </button>
          </div>

          {/* Saved Views */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Bookmark size={12} /> Saved Filter Views
            </p>
            <div className="space-y-1.5">
              {savedViews.map((sv, i) => (
                <button
                  key={i}
                  onClick={() => {
                    onFilterChange(sv.filters);
                    setIsOpen(false);
                  }}
                  className="w-full text-left px-3 py-1.5 rounded-lg bg-gray-50 hover:bg-brand-50 text-xs font-medium text-gray-700 hover:text-brand-700 transition-colors"
                >
                  {sv.name}
                </button>
              ))}
            </div>
          </div>

          {/* City Filter */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">City</p>
            <div className="space-y-1.5">
              {CITIES.map((city) => {
                const checked = (activeFilters.cities || []).includes(city);
                return (
                  <label key={city} className="flex items-center gap-2.5 text-xs text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleFilter('cities', city)}
                      className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                    />
                    {city}
                  </label>
                );
              })}
            </div>
          </div>

          {/* Channel Filter */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Channel</p>
            <div className="space-y-1.5">
              {CHANNELS.map((ch) => {
                const checked = (activeFilters.channels || []).includes(ch);
                return (
                  <label key={ch} className="flex items-center gap-2.5 text-xs text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleFilter('channels', ch)}
                      className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                    />
                    {ch}
                  </label>
                );
              })}
            </div>
          </div>

          {/* Store Format Filter */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Store Format</p>
            <div className="space-y-1.5">
              {FORMATS.map((fmt) => {
                const checked = (activeFilters.formats || []).includes(fmt);
                return (
                  <label key={fmt} className="flex items-center gap-2.5 text-xs text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleFilter('formats', fmt)}
                      className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                    />
                    {fmt}
                  </label>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
