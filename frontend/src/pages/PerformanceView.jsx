import { useState, useEffect } from 'react';
import { fetchComparison } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { Award, ArrowUpRight, ArrowDownRight, Layers, SlidersHorizontal } from 'lucide-react';

export default function PerformanceView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchComparison(null, 3)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading multi-store comparative analysis...</div>;
  if (error) return <div className="text-red-500 p-4">Error loading performance comparison: {error}</div>;
  if (!data) return null;

  const { stores, benchmarks, period } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900">Multi-Store Comparative Analysis</h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Side-by-side performance scoring, benchmarks & gap-to-best analysis ({period.label})
        </p>
      </div>

      {/* Benchmarks Bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Avg Store Revenue</p>
          <p className="text-xl font-bold text-charcoal-900 mt-1">₹{(benchmarks.avg_revenue / 100000).toFixed(2)}L</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Avg Store Orders</p>
          <p className="text-xl font-bold text-charcoal-900 mt-1">{benchmarks.avg_orders.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Avg Store AOV</p>
          <p className="text-xl font-bold text-charcoal-900 mt-1">₹{benchmarks.avg_aov.toFixed(0)}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Avg Store Growth</p>
          <p className="text-xl font-bold text-charcoal-900 mt-1">{benchmarks.avg_growth}%</p>
        </div>
      </div>

      {/* Performance Score Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-charcoal-900 mb-4">Store Performance Score Index (0-100)</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={stores}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="store_name" tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <Tooltip />
            <Bar dataKey="performance_score" name="Performance Score" fill="#d97706" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Side-by-Side Comparison Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-charcoal-900">Side-by-Side Ranking Table</h2>
          <span className="text-2xs text-gray-400 font-medium">Sorted by composite performance score</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 border-b border-gray-100 text-gray-400 uppercase tracking-wider text-2xs font-semibold">
              <tr>
                <th className="px-5 py-3">Store</th>
                <th className="px-4 py-3">City</th>
                <th className="px-4 py-3">Format</th>
                <th className="px-4 py-3 text-right">Revenue</th>
                <th className="px-4 py-3 text-right">vs Avg</th>
                <th className="px-4 py-3 text-right">Orders</th>
                <th className="px-4 py-3 text-right">AOV</th>
                <th className="px-4 py-3 text-right">Growth</th>
                <th className="px-5 py-3 text-right">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-charcoal-800">
              {stores.map((s, idx) => {
                const isPos = s.vs_avg.revenue >= 0;
                return (
                  <tr key={s.store_id} className={`hover:bg-gray-50/80 transition-colors ${s.best_in_class ? 'bg-amber-50/40' : ''}`}>
                    <td className="px-5 py-3 font-semibold flex items-center gap-2">
                      {s.best_in_class && <Award size={14} className="text-amber-500 flex-shrink-0" />}
                      <span>{s.store_name}</span>
                      <span className="text-2xs text-gray-400 font-mono">({s.store_id})</span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{s.city}</td>
                    <td className="px-4 py-3 text-gray-500">{s.store_format}</td>
                    <td className="px-4 py-3 text-right font-semibold">₹{(s.revenue / 100000).toFixed(2)}L</td>
                    <td className={`px-4 py-3 text-right font-medium ${isPos ? 'text-emerald-600' : 'text-red-500'}`}>
                      {isPos ? '+' : ''}{s.vs_avg.revenue}%
                    </td>
                    <td className="px-4 py-3 text-right">{s.orders.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono">₹{s.aov.toFixed(0)}</td>
                    <td className={`px-4 py-3 text-right font-medium ${s.growth_rate >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                      {s.growth_rate >= 0 ? '+' : ''}{s.growth_rate}%
                    </td>
                    <td className="px-5 py-3 text-right font-bold text-brand-600 font-mono">{s.performance_score}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
