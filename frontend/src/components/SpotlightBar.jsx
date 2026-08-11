import { useState, useEffect, useRef } from 'react';
import { Sparkles, ArrowRight, Command, X } from 'lucide-react';

export default function SpotlightBar({ onSearch, placeholder, initialValue = '' }) {
  const [query, setQuery] = useState(initialValue);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);
  const hoverTimerRef = useRef(null);

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  // Handle Mouse Enter: expand bar & cancel any collapse timer
  const handleMouseEnter = () => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
    }
    setIsExpanded(true);
  };

  // Handle Mouse Leave: start 3-second auto-wrap timer (unless user is typing/focused)
  const handleMouseLeave = () => {
    if (isFocused || query.trim()) return; // Keep open while typing or if text exists
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    hoverTimerRef.current = setTimeout(() => {
      setIsExpanded(false);
    }, 3000);
  };

  // Global Ctrl+K / Cmd+K shortcut listener to expand & focus Spotlight
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsExpanded(true);
        setTimeout(() => inputRef.current?.focus(), 250);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    };
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (query.trim() && onSearch) {
      onSearch(query.trim());
      setIsExpanded(false);
      setIsFocused(false);
    }
  };

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="fixed bottom-6 right-6 z-50 font-sans"
    >
      <form
        onSubmit={handleSubmit}
        onClick={() => {
          if (!isExpanded) {
            setIsExpanded(true);
            setTimeout(() => inputRef.current?.focus(), 250);
          }
        }}
        className={`relative flex items-center bg-[#121214] text-white border transition-all duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] overflow-hidden shadow-2xl backdrop-blur-xl cursor-pointer ${
          isExpanded
            ? 'w-[90vw] sm:w-[560px] h-[52px] rounded-full p-2 pl-3.5 pr-2 border-amber-500/70 shadow-amber-950/50 ring-2 ring-amber-500/20'
            : 'w-[195px] h-[46px] rounded-full p-2 pl-3 pr-3 border-amber-500/40 hover:border-amber-500 shadow-amber-950/30 hover:scale-[1.03] active:scale-95'
        }`}
      >
        {/* Gemini Sparkling Icon — Slow luxury rotation: counter-clockwise (left) on unwrap, clockwise (right) on wrap */}
        <div
          className={`w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-md shadow-amber-500/30 transition-transform duration-1000 ease-[cubic-bezier(0.22,1,0.36,1)] ${
            isExpanded ? '-rotate-[360deg] scale-105' : 'rotate-0 scale-100'
          }`}
        >
          <Sparkles size={16} className="text-white animate-pulse" />
        </div>

        {/* Collapsed View Badge Label (Slow fade out when expanded) */}
        <div
          className={`flex items-center justify-between flex-1 pl-2.5 transition-all duration-500 ease-in-out ${
            isExpanded ? 'opacity-0 w-0 max-w-0 overflow-hidden pointer-events-none' : 'opacity-100 w-auto'
          }`}
        >
          <span className="text-xs font-semibold text-gray-200 whitespace-nowrap">Ask QuickBite AI</span>
          <div className="flex items-center gap-0.5 text-3xs text-amber-400/90 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20 font-mono">
            <Command size={9} />
            <span>K</span>
          </div>
        </div>

        {/* Expanded View Input Field & Action Button (Slow elegant fade in) */}
        <div
          className={`flex items-center gap-2 flex-1 pl-2 transition-all duration-500 delay-150 ease-out ${
            isExpanded ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none hidden'
          }`}
        >
          <input
            ref={inputRef}
            type="text"
            value={query}
            onFocus={() => setIsFocused(true)}
            onBlur={() => {
              setIsFocused(false);
              handleMouseLeave();
            }}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder || "Ask QuickBite AI (e.g. 'How to increase revenue?')..."}
            className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-400 focus:outline-none font-sans font-medium"
          />

          {query.trim() && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setQuery('');
              }}
              className="text-gray-400 hover:text-white p-1 transition-colors"
            >
              <X size={14} />
            </button>
          )}

          {/* Gemini-style Action Button Pill */}
          <button
            type="submit"
            className="bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white text-xs font-semibold px-4 py-2 rounded-full flex items-center gap-1.5 shadow-md shadow-amber-500/20 transition-all duration-300 cursor-pointer hover:scale-105 active:scale-95 flex-shrink-0"
          >
            <span>Analyze</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </form>
    </div>
  );
}
