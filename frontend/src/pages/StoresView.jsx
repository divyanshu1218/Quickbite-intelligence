import { useState, useEffect } from 'react';
import { fetchComparison } from '../services/api';
import { Store, TrendingDown, TrendingUp, AlertTriangle } from 'lucide-react';

export default function StoresView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComparison(null, 3)
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading store health...</div>;
  if (!data) return null;

  const { stores } = data;
  const declining = stores.filter((s) => s.growth_rate < -5);
  const growing = stores.filter((s) => s.growth_rate >= 2);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900">Store Management & Health</h1>
        <p className="text-xs text-gray-400 mt-0.5">50 Active Stores Across 5 Metropolitan Clusters</p>
      </div>

      {/* Declining Stores Focus Card */}
      {declining.length > 0 && (
        <div className="bg-amber-50/50 border border-amber-200 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm">
            <AlertTriangle size={16} className="text-amber-600" />
            <span>Stores Requiring Operational Intervention ({declining.length})</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {declining.map((s) => (
              <div key={s.store_id} className="bg-white p-3 rounded-lg border border-amber-200 shadow-2xs">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-xs text-charcoal-900">{s.store_name}</span>
                  <span className="text-2xs font-bold text-red-500">{s.growth_rate}%</span>
                </div>
                <p className="text-2xs text-gray-400 mt-1">{s.city} · {s.store_format}</p>
                <p className="text-xs font-semibold text-charcoal-800 mt-2">Revenue: ₹{(s.revenue / 100000).toFixed(2)}L</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Stores List */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-charcoal-900">All Stores Directory</h2>
        </div>
        <div className="grid grid-cols-2 gap-4 p-5">
          {stores.map((s) => (
            <div key={s.store_id} className="bg-gray-50 hover:bg-white p-4 rounded-xl border border-gray-200 hover:border-brand-300 transition-all space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-charcoal-900">{s.store_name}</h3>
                  <p className="text-2xs text-gray-400">{s.store_id} · {s.city} · {s.store_format}</p>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${s.growth_rate >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-500'}`}>
                  {s.growth_rate >= 0 ? '+' : ''}{s.growth_rate}%
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200/60 text-xs">
                <div>
                  <p className="text-2xs text-gray-400">Revenue</p>
                  <p className="font-semibold text-charcoal-900">₹{(s.revenue / 100000).toFixed(2)}L</p>
                </div>
                <div>
                  <p className="text-2xs text-gray-400">Orders</p>
                  <p className="font-semibold text-charcoal-900">{s.orders.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-2xs text-gray-400">AOV</p>
                  <p className="font-semibold text-charcoal-900">₹{s.aov.toFixed(0)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
