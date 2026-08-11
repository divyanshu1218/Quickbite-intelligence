import { useEffect, useState } from 'react';
import { fetchOverview } from '../services/api';
import TimeMachineSlider from '../components/TimeMachineSlider';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

function formatCurrency(val) {
  if (val >= 100000) return `₹${(val / 100000).toFixed(2)}L`;
  if (val >= 1000) return `₹${(val / 1000).toFixed(1)}K`;
  return `₹${val.toFixed(0)}`;
}

function KpiCard({ label, value, change, prefix = '' }) {
  const isPositive = change >= 0;
  return (
    <div className="bg-white rounded-xl border border-gray-200 px-5 py-4">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-2xl font-semibold text-charcoal-900">{prefix}{value}</p>
      {change !== undefined && (
        <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${isPositive ? 'text-emerald-600' : 'text-red-500'}`}>
          {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {isPositive ? '+' : ''}{change}% vs prev period
        </div>
      )}
    </div>
  );
}

export default function OverviewView({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOverview()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading overview...</div>;
  if (error) return <div className="text-red-500 p-4">Error: {error}</div>;
  if (!data) return null;

  const { kpis, monthly_revenue_trend, store_health, attention_required, performance_signals, period } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900">Business Overview</h1>
        <p className="text-sm text-gray-400 mt-0.5">{period?.label || 'Last 3 months'} · QuickBite Intelligence</p>
      </div>

      {/* The Time Machine Slider Feature */}
      <TimeMachineSlider />


      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KpiCard label="Revenue" value={formatCurrency(kpis.revenue)} change={kpis.revenue_change_pct} />
        <KpiCard label="Orders" value={kpis.orders.toLocaleString()} change={undefined} />
        <KpiCard label="AOV" value={`₹${kpis.aov.toFixed(2)}`} change={undefined} />
        <KpiCard label="Revenue Change" value={`${kpis.revenue_change_pct}%`} change={kpis.revenue_change_pct} />
      </div>

      {/* Revenue Trend Area Chart with Gradient */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-charcoal-900 mb-1">Monthly Revenue Momentum</h2>
        <p className="text-2xs text-gray-400 mb-4">Network-wide monthly sales volume trajectory</p>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={monthly_revenue_trend}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#d97706" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#d97706" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} tickFormatter={(v) => `₹${(v/100000).toFixed(1)}L`} />
            <Tooltip formatter={(v) => [`₹${v.toLocaleString()}`, 'Revenue']} />
            <Area type="monotone" dataKey="revenue" stroke="#d97706" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRevenue)" dot={{ r: 4, fill: '#d97706' }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Store Health + Attention Required */}
      <div className="grid grid-cols-2 gap-4">
        {/* Store Health */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-charcoal-900 mb-4">Store Health</h2>
          <div className="flex items-center justify-around text-center">
            <div>
              <p className="text-3xl font-bold text-red-500">{store_health.declining}</p>
              <p className="text-xs text-gray-400 mt-1">Declining</p>
            </div>
            <div className="w-px h-10 bg-gray-100" />
            <div>
              <p className="text-3xl font-bold text-gray-400">{store_health.stable}</p>
              <p className="text-xs text-gray-400 mt-1">Stable</p>
            </div>
            <div className="w-px h-10 bg-gray-100" />
            <div>
              <p className="text-3xl font-bold text-emerald-500">{store_health.growing}</p>
              <p className="text-xs text-gray-400 mt-1">Growing</p>
            </div>
          </div>
          {store_health.declining_list?.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-100 space-y-1.5">
              {store_health.declining_list.slice(0, 3).map((s) => (
                <div key={s.store_id} className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">{s.store_name}</span>
                  <span className="text-red-500 font-medium">{s.pct_decline}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Attention Required */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-charcoal-900 mb-4">Attention Required</h2>
          <div className="space-y-3">
            {attention_required?.map((alert, idx) => (
              <div key={idx} className="flex items-start gap-2.5">
                <AlertTriangle size={14} className={`mt-0.5 flex-shrink-0 ${alert.type === 'error' ? 'text-red-500' : alert.type === 'warning' ? 'text-amber-500' : 'text-blue-400'}`} />
                <div>
                  <p className="text-xs font-medium text-charcoal-800">{alert.message}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{alert.details}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance Signals */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-charcoal-900 mb-4">Performance Signals</h2>
        <div className="grid grid-cols-4 gap-4">
          {performance_signals?.map((signal, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50">
              <span className="text-xs text-gray-600">{signal.metric}</span>
              <span className={`text-xs font-semibold flex items-center gap-1 ${signal.status === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
                {signal.status === 'up' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {signal.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Intelligence CTA */}
      <div
        onClick={() => onNavigate('intelligence')}
        className="bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:border-brand-300 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center">
            <Activity size={16} className="text-brand-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-charcoal-900">Ask QuickBite Intelligence</p>
            <p className="text-xs text-gray-400">Ask about stores, revenue, products or performance...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
