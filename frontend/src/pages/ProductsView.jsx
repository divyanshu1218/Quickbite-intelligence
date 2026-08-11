import { useState, useEffect } from 'react';
import { fetchProducts, submitQuestion } from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
  PieChart, Pie
} from 'recharts';

const BAR_COLORS = ['#d97706', '#f59e0b', '#fbbf24', '#fcd34d', '#fef3c7'];

export default function ProductsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try fast direct GET endpoint first; fallback to NL-chat query if needed
    fetchProducts()
      .then(setData)
      .catch(() => {
        submitQuestion('Top 5 SKUs by quantity sold and revenue.')
          .then(setData);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading product mix...</div>;

  const chartData = data?.chart?.data || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900">Products & SKU Performance</h1>
        <p className="text-xs text-gray-400 mt-0.5">Top Sellers & Category Mix Analysis</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Horizontal Ranked Bar Chart (Top 5 SKUs by Revenue) */}
        <div className="col-span-2 bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-1">Top SKUs Revenue Ranking</h2>
          <p className="text-xs text-gray-600 mb-4 font-medium">Horizontal ranking by total net revenue contribution</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 40, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#111827', fontWeight: 600 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="sku_name" tick={{ fontSize: 11, fill: '#111827', fontWeight: 600 }} width={120} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', color: '#111827' }}
                itemStyle={{ color: '#111827', fontWeight: '600' }}
                labelStyle={{ color: '#111827', fontWeight: '700' }}
                formatter={(v) => [`₹${v.toLocaleString()}`, 'Net Revenue']}
              />
              <Bar dataKey="revenue" radius={[0, 4, 4, 0]} name="Revenue">
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Quantity Sold Donut Mix */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-1">Volume Breakdown</h2>
          <p className="text-xs text-gray-600 mb-4 font-medium">Units sold per top menu item</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey="quantity_sold"
                nameKey="sku_name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                innerRadius={45}
                paddingAngle={3}
                fill="#d97706"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', color: '#111827' }}
                itemStyle={{ color: '#111827', fontWeight: '600' }}
                labelStyle={{ color: '#111827', fontWeight: '700' }}
                formatter={(value) => [`${value.toLocaleString()} units`, 'Quantity Sold']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Product Breakdown Table */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-charcoal-900">Top Selling Products Breakdown</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 border-b border-gray-100 text-gray-400 uppercase tracking-wider text-2xs font-semibold">
                <tr>
                  <th className="px-5 py-3">Rank</th>
                  <th className="px-4 py-3">Product Name</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3 text-right">Units Sold</th>
                  <th className="px-5 py-3 text-right">Net Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-charcoal-800">
                {chartData.map((item, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/80 transition-colors">
                    <td className="px-5 py-3 font-semibold text-brand-600 font-mono">#{idx + 1}</td>
                    <td className="px-4 py-3 font-semibold text-charcoal-900">{item.sku_name || item.SKU_NAME}</td>
                    <td className="px-4 py-3 text-gray-500">{item.category || 'Core Menu'}</td>
                    <td className="px-4 py-3">
                      <span className={`text-2xs font-bold px-2 py-0.5 rounded ${item.veg_nonveg === 'Non-Veg' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'}`}>
                        {item.veg_nonveg || 'Veg'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono">{item.quantity_sold?.toLocaleString() || '—'}</td>
                    <td className="px-5 py-3 text-right font-bold font-mono">₹{item.revenue?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data?.insight && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-charcoal-900 mb-2">Product Summary Insight</h2>
          <p className="text-xs text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-100">{data.insight}</p>
        </div>
      )}
    </div>
  );
}
