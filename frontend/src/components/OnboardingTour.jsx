import { useState, useEffect } from 'react';
import {
  Sparkles, ArrowRight, ArrowLeft, Check, X, Compass,
  TrendingUp, Sliders, Clock, Search, BarChart2, Lightbulb
} from 'lucide-react';

const TOUR_STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to QuickBite Intelligence',
    subtitle: 'Executive QSR Decision-Support Engine',
    description: 'QuickBite Intelligence delivers evidence-first analytics by combining deterministic DuckDB calculations with stateful multi-agent AI reasoning. Let\'s take a 45-second tour of your workspace!',
    icon: Sparkles,
    badge: 'Overview',
    highlight: 'Welcome',
    accentColor: 'from-amber-500 to-orange-500'
  },
  {
    id: 'kpis',
    title: 'Sticky Executive Trend Tracker',
    subtitle: 'Real-Time KPI Momentum',
    description: 'Pinned right at the top of your dashboard, the Trend Tracker displays Net Revenue (₹33.57L), Order Volume, AOV (₹681), and Active Stores with live sparklines and period-over-period change badges.',
    icon: TrendingUp,
    badge: 'Step 2 of 6',
    highlight: 'Header Metrics',
    accentColor: 'from-blue-500 to-indigo-500'
  },
  {
    id: 'filters',
    title: 'Multi-Dimension Filter Engine',
    subtitle: 'Instant Dimensional Slice & Dice',
    description: 'Filter performance across Cities (Mumbai, Delhi, Pune, etc.), Channels (Swiggy, Zomato, Dine-In), Store Formats (Food Court, High Street), and Date Ranges with 1-click active breadcrumb resets.',
    icon: Sliders,
    badge: 'Step 3 of 6',
    highlight: 'Filter Panel',
    accentColor: 'from-emerald-500 to-teal-500'
  },
  {
    id: 'time-machine',
    title: 'The Time Machine Causality Slider',
    subtitle: 'Temporal Scrubbing & Ghost Overlays',
    description: 'Scrub through monthly historical frames to compare ghost overlays against baseline periods, observe MoM revenue velocity, and inspect auto-synthesized AI causality summaries.',
    icon: Clock,
    badge: 'Step 4 of 6',
    highlight: 'Overview Page',
    accentColor: 'from-purple-500 to-pink-500'
  },
  {
    id: 'spotlight',
    title: 'Google Gemini AI Spotlight (⌘K / Ctrl+K)',
    subtitle: 'Floating AI Command Bar',
    description: 'Look at the bottom-right corner! Hover over the sparkling badge or press ⌘K to unwrap the Gemini Spotlight AI bar. Ask open-ended business questions like "How to increase revenue?" for instant data-backed action plans.',
    icon: Search,
    badge: 'Step 5 of 6',
    highlight: 'Bottom-Right FAB',
    accentColor: 'from-amber-500 to-yellow-500'
  },
  {
    id: 'deep-dive',
    title: 'Specialized Analytics & Interventions',
    subtitle: 'Stores, Products, Channels & Recommendations',
    description: 'Explore side-by-side store comparisons (Performance Score Index 0-100), product mix donut charts, channel dual-axis revenue vs AOV splits, and prioritized interventional recommendations.',
    icon: BarChart2,
    badge: 'Step 6 of 6',
    highlight: 'Navigation Sidebar',
    accentColor: 'from-amber-600 to-orange-600'
  }
];

export default function OnboardingTour({ isOpen, onClose }) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const step = TOUR_STEPS[currentStep];
  const IconComponent = step.icon;
  const isFirst = currentStep === 0;
  const isLast = currentStep === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      handleComplete();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirst) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem('quickbite_tour_completed', 'true');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
      <div className="relative w-full max-w-lg bg-[#121214] text-white rounded-2xl border border-gray-800 shadow-2xl shadow-amber-950/40 overflow-hidden font-sans">
        
        {/* Header Progress Line */}
        <div className="w-full bg-gray-800 h-1">
          <div
            className="bg-gradient-to-r from-amber-500 to-orange-500 h-1 transition-all duration-500 ease-out"
            style={{ width: `${((currentStep + 1) / TOUR_STEPS.length) * 100}%` }}
          />
        </div>

        {/* Close Button */}
        <button
          onClick={handleComplete}
          className="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white rounded-full hover:bg-gray-800/80 transition-colors cursor-pointer"
        >
          <X size={18} />
        </button>

        {/* Step Body */}
        <div className="p-6 sm:p-8 space-y-6">
          
          {/* Top Badge & Icon */}
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${step.accentColor} flex items-center justify-center shadow-lg shadow-amber-500/20`}>
              <IconComponent size={24} className="text-white animate-pulse" />
            </div>
            <div>
              <span className="text-3xs uppercase tracking-wider font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold">
                {step.badge}
              </span>
              <h2 className="text-lg font-bold text-white mt-1 leading-tight">{step.title}</h2>
            </div>
          </div>

          {/* Subtitle & Description */}
          <div className="space-y-2 bg-gray-900/60 p-4 rounded-xl border border-gray-800/80">
            <h3 className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
              <Lightbulb size={14} />
              <span>{step.subtitle}</span>
            </h3>
            <p className="text-xs text-gray-300 leading-relaxed font-normal">
              {step.description}
            </p>
          </div>

          {/* Visual Step Indicator Dots */}
          <div className="flex items-center justify-center gap-1.5 pt-2">
            {TOUR_STEPS.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentStep(idx)}
                className={`h-2 rounded-full transition-all duration-300 cursor-pointer ${
                  idx === currentStep
                    ? 'w-6 bg-gradient-to-r from-amber-500 to-orange-500'
                    : 'w-2 bg-gray-700 hover:bg-gray-600'
                }`}
              />
            ))}
          </div>

          {/* Footer Action Buttons */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-800/80">
            <button
              onClick={handleComplete}
              className="text-xs text-gray-400 hover:text-gray-200 transition-colors font-medium cursor-pointer"
            >
              Skip Tour
            </button>

            <div className="flex items-center gap-2">
              {!isFirst && (
                <button
                  onClick={handlePrev}
                  className="px-4 py-2 rounded-full bg-gray-800 hover:bg-gray-700 text-xs font-semibold text-gray-200 transition-all flex items-center gap-1 cursor-pointer"
                >
                  <ArrowLeft size={14} />
                  <span>Back</span>
                </button>
              )}

              <button
                onClick={handleNext}
                className="px-5 py-2 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white text-xs font-semibold shadow-md shadow-amber-500/20 transition-all flex items-center gap-1.5 cursor-pointer hover:scale-105 active:scale-95"
              >
                <span>{isLast ? 'Explore Platform' : 'Next Step'}</span>
                {isLast ? <Check size={14} /> : <ArrowRight size={14} />}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
