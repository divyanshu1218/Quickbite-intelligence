import { BarChart3, LayoutDashboard, Store, ShoppingBag, Radio, Lightbulb } from 'lucide-react';

const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'performance', label: 'Performance', icon: BarChart3 },
  { id: 'stores', label: 'Stores', icon: Store },
  { id: 'products', label: 'Products', icon: ShoppingBag },
  { id: 'channels', label: 'Channels', icon: Radio },
  { id: 'intelligence', label: 'Intelligence', icon: Lightbulb },
];

export default function Sidebar({ activeView, onNavigate }) {
  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0">
      {/* Brand */}
      <div className="px-5 pt-6 pb-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">Q</span>
          </div>
          <div>
            <div className="text-sm font-semibold text-charcoal-900 tracking-tight leading-none">QUICKBITE</div>
            <div className="text-xs text-gray-400 tracking-widest">Intelligence</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                ${isActive
                  ? 'bg-brand-50 text-brand-700 border border-brand-200'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700 border border-transparent'
                }`}
            >
              <Icon size={16} strokeWidth={isActive ? 2 : 1.5} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-gray-100">
        <p className="text-xs text-gray-400">Aug 2025 – Jul 2026</p>
        <p className="text-xs text-gray-300">50 stores · 20,000 orders</p>
      </div>
    </aside>
  );
}
