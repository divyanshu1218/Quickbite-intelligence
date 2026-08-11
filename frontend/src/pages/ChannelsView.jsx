import { useState, useEffect } from 'react';
import { fetchChannels, submitQuestion } from '../services/api';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid
} from 'recharts';

const CHANNEL_COLORS = {
  'Swiggy': '#f59e0b',
  'Zomato': '#ef4444',
  'Dine-In': '#3b82f6',
  'Takeaway': '#10b981'
};

const DEFAULT_COLORS = ['#f59e0b', '#ef4444', '#3b82f6', '#10b981', '#8b5cf6'];

export default function ChannelsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try fast direct GET endpoint first; fallback to NL-chat query if needed
    fetchChannels()
      .then(setData)
      .catch(() => {
        submitQuestion('Revenue and AOV by channel.')
          .then(setData);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading channel metrics...</div>;

  const chartData = data?.chart?.data || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900">Channel Performance & Mix</h1>
        <p className="text-xs text-gray-400 mt-0.5">Swiggy vs Zomato vs Dine-In vs Takeaway Distribution</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Donut Chart: Revenue Share Distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-1">Revenue Share Distribution</h2>
          <p className="text-xs text-gray-600 mb-4 font-medium">Proportion of total network revenue by sales channel</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey="revenue"
                nameKey="channel"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(1)}%)`}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CHANNEL_COLORS[entry.channel] || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', color: '#111827' }}
                itemStyle={{ color: '#111827', fontWeight: '600' }}
                labelStyle={{ color: '#111827', fontWeight: '700' }}
                formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']}
              />
              <Legend wrapperStyle={{ color: '#111827', fontWeight: 600 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Dual Axis Composed Chart: Revenue (Bar) vs AOV (Line) */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-1">Revenue vs AOV (Dual-Axis)</h2>
          <p className="text-xs text-gray-600 mb-4 font-medium">Comparing sales volume against average ticket size</p>
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="channel" tick={{ fontSize: 11, fill: '#111827', fontWeight: 600 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#111827', fontWeight: 600 }} tickFormatter={(v) => `₹${(v/100000).toFixed(1)}L`} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#111827', fontWeight: 600 }} tickFormatter={(v) => `₹${v}`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', color: '#111827' }}
                itemStyle={{ color: '#111827', fontWeight: '600' }}
                labelStyle={{ color: '#111827', fontWeight: '700' }}
                formatter={(value, name) => [name === 'AOV' ? `₹${value.toFixed(0)}` : `₹${value.toLocaleString()}`, name]}
              />
              <Legend wrapperStyle={{ color: '#111827', fontWeight: 600 }} />
              <Bar yAxisId="left" dataKey="revenue" fill="#d97706" name="Revenue" radius={[4, 4, 0, 0]} />
              <Line yAxisId="right" type="monotone" dataKey="aov" stroke="#2563eb" strokeWidth={3} name="AOV" dot={{ r: 5 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {data?.evidence && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-charcoal-900 mb-3">Verified Channel Metrics</h2>
          <div className="grid grid-cols-4 gap-4">
            {data.evidence.map((ev, i) => (
              <div key={i} className="bg-gray-50 p-3.5 rounded-lg border border-gray-100">
                <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">{ev.label}</p>
                <p className="text-sm font-bold text-charcoal-900 mt-1">{ev.value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
