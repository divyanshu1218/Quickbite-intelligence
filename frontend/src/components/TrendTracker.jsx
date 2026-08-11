import { useState } from 'react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Store, DollarSign, ShoppingCart, Award } from 'lucide-react';

function formatNumber(val, isCurrency = false) {
  if (isCurrency) {
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)}L`;
    if (val >= 1000) return `₹${(val / 1000).toFixed(1)}K`;
    return `₹${val.toFixed(0)}`;
  }
  return val >= 1000 ? `${(val / 1000).toFixed(1)}K` : val.toString();
}

export default function TrendTracker({ overviewData }) {
  const [selectedMetric, setSelectedMetric] = useState(null);

  if (!overviewData) return null;

  const { kpis, monthly_revenue_trend, store_health } = overviewData;

  const sparklineData = monthly_revenue_trend?.map((m) => ({
    revenue: m.revenue,
    orders: m.orders,
    aov: m.aov,
  })) || [];

  const metrics = [
    {
      id: 'revenue',
      label: 'Total Revenue',
      value: kpis.revenue,
      change: kpis.revenue_change_pct,
      isCurrency: true,
      dataKey: 'revenue',
      color: '#d97706',
      icon: DollarSign,
    },
    {
      id: 'orders',
      label: 'Total Orders',
      value: kpis.orders,
      change: -12.3, // MoM drop
      isCurrency: false,
      dataKey: 'orders',
      color: '#2563eb',
      icon: ShoppingCart,
    },
    {
      id: 'aov',
      label: 'Average Order Value',
      value: kpis.aov,
      change: 1.2,
      isCurrency: true,
      dataKey: 'aov',
      color: '#059669',
      icon: Award,
    },
    {
      id: 'stores',
      label: 'Active Stores',
      value: (store_health?.declining || 0) + (store_health?.stable || 0) + (store_health?.growing || 0) || 50,
      change: 0,
      isCurrency: false,
      dataKey: 'revenue',
      color: '#7c3aed',
      icon: Store,
    },
  ];

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 sticky top-0 z-20 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        {metrics.map((m) => {
          const isPos = m.change >= 0;
          return (
            <div
              key={m.id}
              onClick={() => setSelectedMetric(m)}
              className="flex-1 bg-gray-50 hover:bg-brand-50/40 rounded-xl px-4 py-2.5 cursor-pointer border border-transparent hover:border-brand-200 transition-all duration-150 flex items-center justify-between gap-3"
            >
              <div>
                <p className="text-2xs font-medium text-gray-400 uppercase tracking-wider">{m.label}</p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-base font-bold text-charcoal-900">
                    {formatNumber(m.value, m.isCurrency)}
                  </span>
                  {m.change !== 0 && (
                    <span className={`text-2xs font-semibold flex items-center gap-0.5 ${isPos ? 'text-emerald-600' : 'text-red-500'}`}>
                      {isPos ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                      {isPos ? '+' : ''}{m.change}%
                    </span>
                  )}
                </div>
              </div>

              {/* Sparkline */}
              <div className="w-16 h-8">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sparklineData}>
                    <defs>
                      <linearGradient id={`grad-${m.id}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={m.color} stopOpacity={0.3} />
                        <stop offset="100%" stopColor={m.color} stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone"
                      dataKey={m.dataKey}
                      stroke={m.color}
                      strokeWidth={1.5}
                      fill={`url(#grad-${m.id})`}
                      isAnimationActive={true}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal on Click */}
      {selectedMetric && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4" onClick={() => setSelectedMetric(null)}>
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-gray-200 space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-charcoal-900">{selectedMetric.label} Detail</h3>
              <button onClick={() => setSelectedMetric(null)} className="text-gray-400 hover:text-gray-600 text-sm font-medium">Close</button>
            </div>
            <div className="py-2">
              <p className="text-3xl font-bold text-charcoal-900">{formatNumber(selectedMetric.value, selectedMetric.isCurrency)}</p>
              <p className="text-xs text-gray-500 mt-1">Period-over-period change: <span className={selectedMetric.change >= 0 ? 'text-emerald-600 font-semibold' : 'text-red-500 font-semibold'}>{selectedMetric.change}%</span></p>
            </div>
            <div className="h-40 bg-gray-50 rounded-xl p-3">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sparklineData}>
                  <Area type="monotone" dataKey={selectedMetric.dataKey} stroke={selectedMetric.color} fill={selectedMetric.color} fillOpacity={0.15} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
