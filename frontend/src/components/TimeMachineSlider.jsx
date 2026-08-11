import { useState, useEffect } from 'react';
import { fetchTimeMachine } from '../services/api';
import { Play, Pause, Film, Clock, Sparkles, Ghost, TrendingUp, TrendingDown, Store, Radio } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function TimeMachineSlider() {
  const [frames, setFrames] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showGhost, setShowGhost] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimeMachine()
      .then((data) => {
        setFrames(data.frames || []);
        if (data.frames?.length) setCurrentIndex(data.frames.length - 1); // Start at latest
      })
      .catch((e) => console.error('Time machine timeline error:', e))
      .finally(() => setLoading(false));
  }, []);

  // Automatic playback scrubbing
  useEffect(() => {
    let interval = null;
    if (isPlaying && frames.length > 0) {
      interval = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % frames.length);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, frames]);

  if (loading || !frames.length) return null;

  const currentFrame = frames[currentIndex];
  const ghostFrame = currentFrame?.ghost_kpis;

  return (
    <div className="bg-gradient-to-r from-charcoal-900 via-charcoal-800 to-charcoal-900 text-white rounded-2xl p-5 shadow-xl border border-charcoal-700 space-y-4 my-4">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-charcoal-700/60 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center">
            <Film size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold tracking-tight">The Time Machine</h3>
              <span className="text-2xs bg-amber-500/20 text-amber-300 font-mono px-2 py-0.5 rounded border border-amber-500/30">
                Interactive Causality Engine
              </span>
            </div>
            <p className="text-2xs text-gray-400">Scrub timeline frames to observe historical MoM causality in real-time</p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowGhost(!showGhost)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-2xs font-semibold transition-all border ${
              showGhost
                ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                : 'bg-charcoal-800 text-gray-400 border-charcoal-700 hover:text-gray-200'
            }`}
          >
            <Ghost size={13} />
            Ghost Comparison {showGhost ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-2xs font-bold bg-amber-500 hover:bg-amber-600 text-charcoal-950 transition-colors shadow-sm"
          >
            {isPlaying ? <Pause size={13} /> : <Play size={13} />}
            {isPlaying ? 'Pause Scrub' : 'Play Timeline'}
          </button>
        </div>
      </div>

      {/* Filmstrip Timeline Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-2xs font-mono text-gray-400 px-1">
          <span>Scrub Date: <strong className="text-amber-400">{currentFrame.label}</strong></span>
          <span>Frame {currentIndex + 1} of {frames.length}</span>
        </div>

        {/* Filmstrip Frame Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-none">
          {frames.map((frame, idx) => {
            const isActive = idx === currentIndex;
            return (
              <button
                key={frame.id}
                onClick={() => setCurrentIndex(idx)}
                className={`flex-1 min-w-[100px] py-2 px-3 rounded-xl text-left border transition-all duration-200 relative overflow-hidden cursor-pointer ${
                  isActive
                    ? 'bg-amber-500/20 border-amber-400 text-white shadow-lg ring-1 ring-amber-400/50'
                    : 'bg-charcoal-800/80 border-charcoal-700/80 text-gray-400 hover:bg-charcoal-700 hover:text-gray-200'
                }`}
              >
                <p className="text-2xs font-bold font-mono tracking-wider uppercase">{frame.month}</p>
                <p className="text-xs font-semibold text-white mt-0.5">₹{(frame.kpis.revenue / 100000).toFixed(1)}L</p>
                {isActive && <div className="absolute top-0 left-0 right-0 h-0.5 bg-amber-400" />}
              </button>
            );
          })}
        </div>

        {/* Range Slider Track */}
        <input
          type="range"
          min={0}
          max={frames.length - 1}
          value={currentIndex}
          onChange={(e) => setCurrentIndex(Number(e.target.value))}
          className="w-full h-1.5 bg-charcoal-700 rounded-lg appearance-none cursor-pointer accent-amber-400"
        />
      </div>

      {/* Dynamic Snapshot Data Grid */}
      <div className="grid grid-cols-4 gap-4 pt-2">
        {/* KPI 1: Revenue */}
        <div className="bg-charcoal-800/90 rounded-xl p-3.5 border border-charcoal-700 relative">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Revenue</p>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-extrabold text-white">₹{(currentFrame.kpis.revenue / 100000).toFixed(2)}L</span>
            {currentFrame.kpis.rev_change !== 0 && (
              <span className={`text-2xs font-bold flex items-center ${currentFrame.kpis.rev_change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {currentFrame.kpis.rev_change >= 0 ? '+' : ''}{currentFrame.kpis.rev_change}%
              </span>
            )}
          </div>
          {/* Ghost comparison line */}
          {showGhost && ghostFrame && (
            <p className="text-2xs text-purple-300 font-mono mt-1 pt-1 border-t border-charcoal-700/60 flex items-center gap-1">
              <Ghost size={10} /> Prev: ₹{(ghostFrame.revenue / 100000).toFixed(2)}L
            </p>
          )}
        </div>

        {/* KPI 2: Orders */}
        <div className="bg-charcoal-800/90 rounded-xl p-3.5 border border-charcoal-700 relative">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">Orders</p>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-extrabold text-white">{currentFrame.kpis.orders.toLocaleString()}</span>
            {currentFrame.kpis.orders_change !== 0 && (
              <span className={`text-2xs font-bold flex items-center ${currentFrame.kpis.orders_change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {currentFrame.kpis.orders_change >= 0 ? '+' : ''}{currentFrame.kpis.orders_change}%
              </span>
            )}
          </div>
          {showGhost && ghostFrame && (
            <p className="text-2xs text-purple-300 font-mono mt-1 pt-1 border-t border-charcoal-700/60 flex items-center gap-1">
              <Ghost size={10} /> Prev: {ghostFrame.orders.toLocaleString()}
            </p>
          )}
        </div>

        {/* KPI 3: AOV */}
        <div className="bg-charcoal-800/90 rounded-xl p-3.5 border border-charcoal-700">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider">AOV</p>
          <p className="text-xl font-extrabold text-white mt-1">₹{currentFrame.kpis.aov.toFixed(0)}</p>
          {showGhost && ghostFrame && (
            <p className="text-2xs text-purple-300 font-mono mt-1 pt-1 border-t border-charcoal-700/60 flex items-center gap-1">
              <Ghost size={10} /> Prev: ₹{ghostFrame.aov.toFixed(0)}
            </p>
          )}
        </div>

        {/* Top Store frame */}
        <div className="bg-charcoal-800/90 rounded-xl p-3.5 border border-charcoal-700">
          <p className="text-2xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1">
            <Store size={11} className="text-amber-400" /> Top Store
          </p>
          {currentFrame.top_stores?.[0] ? (
            <div>
              <p className="text-xs font-bold text-amber-300 truncate mt-1">{currentFrame.top_stores[0].STORE_NAME}</p>
              <p className="text-2xs text-gray-400">₹{(currentFrame.top_stores[0].revenue / 100000).toFixed(2)}L</p>
            </div>
          ) : (
            <p className="text-2xs text-gray-400">N/A</p>
          )}
        </div>
      </div>

      {/* Dynamic AI Insight Box */}
      <div className="bg-charcoal-800/60 rounded-xl p-3.5 border border-charcoal-700/80 flex items-start gap-2.5">
        <Sparkles size={16} className="text-amber-400 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-2xs font-bold uppercase tracking-wider text-amber-400">Causal AI Insight ({currentFrame.label})</p>
          <p className="text-xs text-gray-200 mt-0.5 leading-relaxed">{currentFrame.insight}</p>
        </div>
      </div>
    </div>
  );
}
