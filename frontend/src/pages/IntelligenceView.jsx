import { useState, useEffect } from 'react';
import { submitQuestion, fetchSampleQuestions, fetchRecommendations } from '../services/api';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, ComposedChart,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import { Send, CheckCircle2, ShieldCheck, ChevronDown, ChevronUp, Lightbulb, Zap, ArrowRight, Activity } from 'lucide-react';

export default function IntelligenceView({ initialQuery = '' }) {
  const [question, setQuestion] = useState(initialQuery);
  const [sampleQuestions, setSampleQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showTrace, setShowTrace] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [recsLoading, setRecsLoading] = useState(false);

  useEffect(() => {
    fetchSampleQuestions().then((data) => setSampleQuestions(data.questions || []));
  }, []);

  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      setQuestion(initialQuery);
      handleAsk(initialQuery);
    }
  }, [initialQuery]);

  const handleAsk = async (qText) => {
    const queryToSubmit = qText || question;
    if (!queryToSubmit.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setRecommendations(null);

    try {
      const data = await submitQuestion(queryToSubmit);
      setResult(data);

      // Check if store ID is present for smart recommendations
      if (data.analysis_type?.includes('store') || queryToSubmit.toLowerCase().includes('store')) {
        const storeMatch = queryToSubmit.match(/ST\d{3}/i) || data.insight?.match(/ST\d{3}/i);
        const storeId = storeMatch ? storeMatch[0].toUpperCase() : 'ST001';
        setRecsLoading(true);
        fetchRecommendations(storeId)
          .then(setRecommendations)
          .catch(() => {})
          .finally(() => setRecsLoading(false));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderChart = (chartConfig) => {
    if (!chartConfig || !chartConfig.data || chartConfig.data.length === 0) return null;
    const { type, xKey, series, data } = chartConfig;

    if (type === 'donut' || type === 'pie') {
      const COLORS = ['#f59e0b', '#ef4444', '#3b82f6', '#10b981', '#8b5cf6', '#d97706'];
      return (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={data}
              dataKey={series?.[0]?.key || 'revenue'}
              nameKey={xKey || 'name'}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
            >
              {data.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    if (type === 'horizontal-bar') {
      return (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis type="category" dataKey={xKey} tick={{ fontSize: 11, fill: '#374151' }} width={100} />
            <Tooltip />
            <Legend />
            {series.map((s, idx) => (
              <Bar key={idx} dataKey={s.key} name={s.label} fill={idx === 0 ? '#d97706' : '#2563eb'} radius={[0, 4, 4, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      );
    }

    if (type === 'composed' || type === 'diagnostic') {
      return (
        <ResponsiveContainer width="100%" height={260}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <Tooltip />
            <Legend />
            {series.map((s, idx) => (
              s.type === 'line' ? (
                <Line key={idx} yAxisId="right" type="monotone" dataKey={s.key} name={s.label} stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4 }} />
              ) : (
                <Bar key={idx} yAxisId="left" dataKey={s.key} name={s.label} fill="#d97706" radius={[4, 4, 0, 0]} />
              )
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      );
    }

    if (type === 'area') {
      return (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#d97706" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#d97706" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <Tooltip />
            <Legend />
            {series.map((s, idx) => (
              <Area key={idx} type="monotone" dataKey={s.key} name={s.label} stroke="#d97706" strokeWidth={2.5} fill="url(#chartGrad)" dot={{ r: 4 }} />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      );
    }

    if (type === 'line') {
      return (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
            <Tooltip />
            <Legend />
            {series.map((s, idx) => (
              <Line key={idx} type="monotone" dataKey={s.key} name={s.label} stroke={idx === 0 ? '#d97706' : '#2563eb'} strokeWidth={2.5} dot={{ r: 4 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );
    }

    // Default: BarChart / Grouped-Bar
    return (
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: '#9ca3af' }} />
          <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
          <Tooltip />
          <Legend />
          {series.map((s, idx) => (
            <Bar key={idx} dataKey={s.key} name={s.label} fill={idx === 0 ? '#d97706' : '#2563eb'} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-charcoal-900 flex items-center gap-2">
          <Lightbulb className="text-brand-600" size={20} />
          QuickBite Intelligence Engine
        </h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Observational analytics & deterministic DuckDB calculations with Groq reasoning
        </p>
      </div>

      {/* Query Bar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-xs">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question (e.g. 'Show revenue for last 3 months', 'Which stores are declining?')..."
            className="flex-1 text-sm bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-brand-500 focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 cursor-pointer"
          >
            {loading ? <Activity size={14} className="animate-spin" /> : <Send size={14} />}
            Analyze
          </button>
        </form>

        {/* Sample Question Chips — full question text */}
        <div className="mt-3 space-y-1.5">
          <span className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Frequently Asked Questions:</span>
          <div className="flex flex-col gap-1.5">
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuestion(q);
                  handleAsk(q);
                }}
                className="text-left text-xs bg-gray-50 hover:bg-brand-50 hover:text-brand-800 hover:border-brand-300 text-gray-600 px-3 py-2 rounded-lg border border-gray-200 transition-all cursor-pointer flex items-start gap-2 group"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-brand-100 text-brand-700 text-2xs font-bold flex items-center justify-center group-hover:bg-brand-600 group-hover:text-white transition-colors">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{q}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center space-y-3">
          <Activity size={28} className="animate-spin text-brand-600 mx-auto" />
          <p className="text-sm font-medium text-charcoal-800">Analyzing DuckDB Dataset...</p>
          <p className="text-xs text-gray-400">Executing deterministic query & verifying metrics</p>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-xs text-red-600">
          <span className="font-semibold">Query Execution Error:</span> {error}
        </div>
      )}

      {/* Report Output */}
      {result && (
        <div className="space-y-6">
          {/* Response Meta Header */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <span className="text-2xs font-bold uppercase tracking-wider text-brand-600 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                  {result.analysis_type}
                </span>
                <span className="text-xs text-gray-400 ml-2 font-medium">
                  {result.period?.label} ({result.period?.start} to {result.period?.end})
                </span>
              </div>
              <div className="flex items-center gap-2">
                {result.analysis_type?.startsWith('nl_sql') && (
                  <span className="flex items-center gap-1 text-2xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">
                    <Zap size={11} /> Fast Sub-100ms SQL Engine
                  </span>
                )}
                <span className="flex items-center gap-1 text-2xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-0.5 rounded-full font-semibold">
                  <ShieldCheck size={12} /> Verified Data
                </span>
              </div>
            </div>

            {/* Verified Insight */}
            <div>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Executive Summary</h2>
              <p className="text-sm font-medium text-charcoal-900 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
                {result.insight}
              </p>
            </div>

            {/* Direct Data Evidence */}
            {result.evidence && result.evidence.length > 0 && (
              <div>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Verified Data Evidence</h2>
                <div className="grid grid-cols-3 gap-3">
                  {result.evidence.map((ev, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                      <p className="text-2xs font-medium text-gray-400 uppercase tracking-wider">{ev.label}</p>
                      <p className="text-sm font-bold text-charcoal-900 mt-0.5">{ev.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Dynamic Recharts Visualization */}
          {result.chart && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="text-sm font-semibold text-charcoal-900 mb-4">{result.chart.title}</h2>
              {renderChart(result.chart)}
            </div>
          )}

          {/* Reasoning Basis & Drivers */}
          {result.reasoning_basis && result.reasoning_basis.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Strongest Observed Signals</h2>
              <ul className="space-y-2">
                {result.reasoning_basis.map((rb, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-charcoal-800">
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-500 mt-1.5 flex-shrink-0" />
                    <span>{rb}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Smart Recommendations Engine Output */}
          {recommendations && recommendations.recommendations?.length > 0 && (
            <div className="bg-white rounded-xl border border-brand-200 p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                <h2 className="text-sm font-semibold text-charcoal-900 flex items-center gap-2">
                  <Zap size={16} className="text-brand-600" />
                  Smart Recommendation Engine (Store {recommendations.store_id})
                </h2>
                <span className="text-2xs text-brand-700 bg-brand-50 px-2 py-0.5 rounded font-medium border border-brand-200">
                  5 Actionable Interventions
                </span>
              </div>
              <div className="space-y-3">
                {recommendations.recommendations.map((rec, idx) => (
                  <div key={idx} className="bg-gray-50 hover:bg-white rounded-lg p-3.5 border border-gray-200 hover:border-brand-300 transition-all space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-2xs font-bold uppercase tracking-wider text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                        {rec.category}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-emerald-600">{rec.estimated_impact} ({rec.impact_percent})</span>
                        <span className="text-2xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded font-medium">{rec.timeline}</span>
                      </div>
                    </div>
                    <p className="text-xs font-semibold text-charcoal-900">{rec.action}</p>
                    <p className="text-2xs text-gray-500">{rec.rationale}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Audit Trace View */}
          {result.trace && result.trace.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <button
                onClick={() => setShowTrace(!showTrace)}
                className="w-full flex items-center justify-between text-xs font-semibold text-gray-500 hover:text-gray-700 cursor-pointer"
              >
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 size={14} className="text-emerald-600" />
                  Observational Audit Trace ({result.trace.length} Execution Steps)
                </span>
                {showTrace ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>

              {showTrace && (
                <div className="mt-4 pt-3 border-t border-gray-100 font-mono text-2xs space-y-1 text-gray-600 bg-gray-50 p-3 rounded-lg">
                  {result.trace.map((step, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-gray-300">[{i + 1}]</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
