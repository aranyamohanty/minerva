import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronRight, Play, Pause, Sparkles, Database, 
  Search, Sliders, Filter, Cpu, Code2, Check, AlertCircle 
} from 'lucide-react';
import { PipelineStep } from '../types';

export const ContextPipeline: React.FC = () => {
  const [activeStep, setActiveStep] = useState<string>('retrieval');
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [particles, setParticles] = useState<Array<{ id: number; progress: number; currentStep: number }>>([]);
  const [scannedCount, setScannedCount] = useState<number>(17492);
  const [relevanceScore, setRelevanceScore] = useState<number>(94.2);
  const [compressionRatio, setCompressionRatio] = useState<number>(75.42);
  const particleIdCounter = useRef(0);

  const steps: PipelineStep[] = [
    {
      id: 'prompt',
      name: 'User Prompt',
      description: 'Incoming instruction/question requiring historical project context.',
      metricLabel: 'Payload Size',
      metricValue: '182 tokens',
      telemetry: 'Received raw text string. Intent analysis: code synthesis. Extracted entities: [Minerva, MemoryNode, schema.ts]',
      status: 'complete'
    },
    {
      id: 'retrieval',
      name: 'Memory Retrieval',
      description: 'Scans the high-speed local ledger of raw experience chunks.',
      metricLabel: 'Search Boundary',
      metricValue: '17,492 nodes',
      telemetry: 'Querying SQLite hybrid indices. Partitioning cluster by timeline and tags. Recency dampener = 0.98.',
      status: 'processing'
    },
    {
      id: 'semantic',
      name: 'Semantic Search',
      description: 'Performs vector search matching underlying cognitive intent.',
      metricLabel: 'Top Candidates',
      metricValue: '248 retrieved',
      telemetry: 'Vector lookup completed. Embedding similarity threshold >= 0.76. Computed cosine distances on 384-dimensional manifold.',
      status: 'idle'
    },
    {
      id: 'ranking',
      name: 'Relevance Ranking',
      description: 'Applies domain-trained cross-encoder re-ranking for contextual fit.',
      metricLabel: 'P-Value Confidence',
      metricValue: '96.8% accuracy',
      telemetry: 'Applying re-ranking matrix. Score distribution: max 0.984, median 0.743. Filtering 129 noise documents below margin.',
      status: 'idle'
    },
    {
      id: 'mmr',
      name: 'MMR Filtering',
      description: 'Maximal Marginal Relevance filters redundancies, enhancing information diversity.',
      metricLabel: 'De-duplication',
      metricValue: '19 gold files selected',
      telemetry: 'Executing MMR diversity check (lambda = 0.75). Culled 9 overlapping historical transcripts representing the same meeting.',
      status: 'idle'
    },
    {
      id: 'compression',
      name: 'Context Compression',
      description: 'Trims fluff, syntactic filler, and boilerplate to maximize semantic density.',
      metricLabel: 'Token Saving',
      metricValue: '75.42% reduced',
      telemetry: 'Locating repetitive structures... Stripping Markdown syntax... Retaining absolute semantic anchor nodes... -12,400 tokens.',
      status: 'idle'
    },
    {
      id: 'compilation',
      name: 'Context Compilation',
      description: 'Formats and synthesizes optimized system-native schemas.',
      metricLabel: 'Template Struct',
      metricValue: '1970 dense tokens',
      telemetry: 'Framing contexts in custom XML/Markdown interface protocols. Appending system guidelines & constraints. Validation: OK.',
      status: 'idle'
    },
    {
      id: 'window',
      name: 'AI Context Window',
      description: 'Injects pristine, structured intelligence directly to LLM.',
      metricLabel: 'Optimal Density',
      metricValue: '14x faster retrieval',
      telemetry: 'Context compiled. Ready for inference in OpenAI/Claude/Gemini. Latency: 42ms. Zero cache-misses detected.',
      status: 'idle'
    },
  ];

  // Tick step if play is enabled
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setActiveStep((prev) => {
        const index = steps.findIndex((s) => s.id === prev);
        const nextIndex = (index + 1) % steps.length;
        
        // Randomly adjust metrics to simulate system working in real-time
        setScannedCount(prevCount => prevCount + Math.floor(Math.random() * 21) - 10);
        setRelevanceScore(prevScore => {
          const delta = (Math.random() * 0.4 - 0.2);
          const newScore = prevScore + delta;
          return Number(Math.max(90, Math.min(99.9, newScore)).toFixed(1));
        });
        setCompressionRatio(prevComp => {
          const delta = (Math.random() * 0.8 - 0.4);
          const newComp = prevComp + delta;
          return Number(Math.max(68, Math.min(76, newComp)).toFixed(1));
        });

        return steps[nextIndex].id;
      });
    }, 4500);

    return () => clearInterval(interval);
  }, [isPlaying, steps.length]);

  // Particle simulation flowing downstream
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      // Spawn new particle
      particleIdCounter.current += 1;
      const newParticle = { id: particleIdCounter.current };
      setParticles(prev => [...prev, newParticle].slice(-15)); // Keep max 15 particles in list
    }, 800);

    return () => clearInterval(interval);
  }, [isPlaying]);

  const activeStepObj = steps.find((s) => s.id === activeStep) || steps[0];

  const getStepIcon = (id: string, index: number) => {
    const isActive = id === activeStep;
    const baseClass = `w-10 h-10 rounded-lg flex items-center justify-center border transition-all duration-300 ${
      isActive 
        ? 'bg-[#C85A32]/10 dark:bg-[#E26838]/10 border-[#C85A32] dark:border-[#E26838] text-[#C85A32] dark:text-[#E26838] scale-110' 
        : 'bg-[#FBF9F6] dark:bg-[#181513] border-[#E6E1D8] dark:border-[#2B2622] text-[#545454] dark:text-[#A39A90] hover:border-[#C85A32] dark:hover:border-[#E26838] hover:text-[#C85A32] dark:hover:text-[#E26838]'
    }`;

    switch (id) {
       case 'prompt': return <div className={baseClass}><Code2 size={18} /></div>;
       case 'retrieval': return <div className={baseClass}><Database size={18} /></div>;
       case 'semantic': return <div className={baseClass}><Search size={18} /></div>;
       case 'ranking': return <div className={baseClass}><Sliders size={18} /></div>;
       case 'mmr': return <div className={baseClass}><Filter size={18} /></div>;
       case 'compression': return <div className={baseClass}><Cpu size={18} /></div>;
       case 'compilation': return <div className={baseClass}><Sparkles size={18} /></div>;
       case 'window': return <div className={baseClass}><Check size={18} /></div>;
       default: return <div className={baseClass}><Database size={18} /></div>;
    }
  };

  return (
    <div id="pipeline-section" className="relative bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-2xl p-6 lg:p-10 overflow-hidden paper-shadow transition-colors duration-300">
      {/* Absolute floating gradient */}
      <div className="absolute top-0 right-0 w-80 h-80 rounded-full bg-[#C85A32]/5 dark:bg-[#E26838]/5 blur-[80px] pointer-events-none" />

      {/* Control Rail */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10 pb-6 border-b border-[#E6E1D8] dark:border-[#2B2622]">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-[#C85A32] dark:bg-[#E26838]" />
            <span className="text-[10px] uppercase font-bold tracking-widest text-[#C85A32] dark:text-[#E26838] font-mono">Real-Time Core Engine</span>
          </div>
          <p className="text-sm text-[#545454] dark:text-[#A39A90]">
            Tap nodes on the pipeline to manually halt the process and inspect details.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center gap-2 px-4 py-2 bg-[#FBF9F6] dark:bg-[#181513] hover:bg-[#EDE7DF] dark:hover:bg-[#27221E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-lg text-xs font-mono tracking-wider text-[#191919] dark:text-[#FBF9F6] hover:text-[#C85A32] dark:hover:text-[#E26838] transition-all cursor-pointer"
          >
            {isPlaying ? (
              <>
                <Pause size={12} className="text-red-600" />
                <span>HALT SEQUENCE</span>
              </>
            ) : (
              <>
                <Play size={12} className="text-[#C85A32]" />
                <span>START RUN</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Metric Counters Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">MEMORIES LOADED</span>
          <span className="text-xl lg:text-2xl font-mono text-[#191919] dark:text-[#FBF9F6] font-bold leading-none tracking-tight">
            {scannedCount.toLocaleString()}
          </span>
          <span className="text-[10px] text-[#C85A32] dark:text-[#E26838] font-mono mt-1">4ms scan latency</span>
        </div>

        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">CANDIDATES FILTERED</span>
          <span className="text-xl lg:text-2xl font-mono text-[#191919] dark:text-[#FBF9F6] font-bold leading-none tracking-tight">
            248
          </span>
          <span className="text-[10px] text-slate-500 dark:text-[#A39A90] font-mono mt-1">Cosine similarity index</span>
        </div>

        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">SELECTED CONTEXTS</span>
          <span className="text-xl lg:text-2xl font-mono text-[#191919] dark:text-[#FBF9F6] font-bold leading-none tracking-tight">
            19
          </span>
          <span className="text-[10px] text-[#C85A32] dark:text-[#E26838] font-mono mt-1">100% relevant nodes</span>
        </div>

        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">RELEVANCE CONFIDENCE</span>
          <span className="text-xl lg:text-2xl font-mono text-[#C85A32] dark:text-[#E26838] font-bold leading-none tracking-tight">
            {relevanceScore}%
          </span>
          <span className="text-[10px] text-[#C85A32] dark:text-[#E26838] font-mono mt-1">Target precision reached</span>
        </div>

        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">TOKEN COMPRESSION</span>
          <span className="text-xl lg:text-2xl font-mono text-[#191919] dark:text-[#FBF9F6] font-bold leading-none tracking-tight">
            -{compressionRatio}%
          </span>
          <span className="text-[10px] text-slate-500 dark:text-[#A39A90] font-mono mt-1">Syntactic filler stripped</span>
        </div>

        <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] p-4 rounded-xl flex flex-col justify-center col-span-2 md:col-span-1 shadow-sm transition-colors duration-300">
          <span className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest mb-1">RETRIEVAL ENHANCEMENT</span>
          <span className="text-xl lg:text-2xl font-mono text-[#C85A32] dark:text-[#E26838] font-bold leading-none tracking-tight">
            14x Faster
          </span>
          <span className="text-[10px] text-[#C85A32] dark:text-[#E26838] font-mono mt-1">Local parallel caching</span>
        </div>
      </div>

      {/* Interactive Pipeline Track */}
      <div className="relative flex flex-col lg:flex-row items-center justify-between gap-6 lg:gap-3 py-8 px-4 bg-[#FBF9F6] dark:bg-[#181513] rounded-xl border border-[#E6E1D8] dark:border-[#2B2622] mb-8 overflow-hidden paper-shadow transition-colors duration-300">
        
        {/* Connection backline for desktop */}
        <div className="absolute left-10 right-10 top-1/2 -translate-y-1/2 h-[2px] bg-[#EBE5DC] dark:bg-[#2B2622] hidden lg:block z-0" />
        
        {/* Connection backline for vertical layout (mobile) */}
        <div className="absolute top-10 bottom-10 left-12 w-[2px] bg-[#EBE5DC] dark:bg-[#2B2622] lg:hidden z-0" />

        {/* Dynamic moving data packets flow visualization */}
        <div className="absolute inset-x-10 top-1/2 -translate-y-1/2 h-8 pointer-events-none hidden lg:block z-0">
          {particles.map(p => {
            return (
              <motion.div 
                key={p.id} 
                className="absolute top-1/2 -translate-y-1/2 flex items-center justify-center"
                initial={{ left: "0%", opacity: 0 }}
                animate={{ left: "100%", opacity: [0, 1, 1, 0] }}
                transition={{ duration: 2.4, ease: "linear" }}
              >
                <div className="w-[9px] h-[9px] rounded-full bg-[#C85A32] dark:bg-[#E26838] relative flex items-center justify-center">
                  <div className="absolute w-[18px] h-[18px] rounded-full border border-[#C85A32] dark:border-[#E26838] animate-ping" style={{ animationDuration: '1.5s' }} />
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Dynamic vertical particles for mobile */}
        <div className="absolute top-10 bottom-10 left-12 w-4 pointer-events-none lg:hidden z-0">
          {particles.map(p => {
            return (
              <motion.div 
                key={p.id} 
                className="absolute left-1/2 -translate-x-1/2 flex items-center justify-center"
                initial={{ top: "0%", opacity: 0 }}
                animate={{ top: "100%", opacity: [0, 1, 1, 0] }}
                transition={{ duration: 2.4, ease: "linear" }}
              >
                <div className="w-[7px] h-[7px] rounded-full bg-[#C85A32] dark:bg-[#E26838] relative flex items-center justify-center">
                  <div className="absolute w-[14px] h-[14px] rounded-full border border-[#C85A32] dark:border-[#E26838] animate-ping" style={{ animationDuration: '1.5s' }} />
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Nodes rendering */}
        {steps.map((step, index) => {
          const isActive = step.id === activeStep;
          return (
            <div 
              key={step.id} 
              id={`node-${step.id}`}
              className="relative flex items-center lg:flex-col gap-6 lg:gap-3 w-full lg:w-auto z-10 cursor-pointer group"
              onClick={() => {
                setIsPlaying(false);
                setActiveStep(step.id);
              }}
            >
              {/* Wrapper wrapper with pulsing effect if active */}
              <div className="relative">
                {getStepIcon(step.id, index)}
                {isActive && (
                  <span className="absolute -inset-1 rounded-lg border border-[#C85A32]/40 animate-ping opacity-40 pointer-events-none" style={{ animationDuration: '2s' }} />
                )}
              </div>

              {/* Step info labels */}
              <div className="flex flex-col lg:items-center text-left lg:text-center mt-1">
                <span className={`text-xs font-mono uppercase font-bold tracking-wider transition-colors duration-300 ${isActive ? 'text-[#C85A32]' : 'text-[#545454] group-hover:text-[#191919]'}`}>
                  {step.name}
                </span>
                <span className="text-[10px] font-mono text-[#8B7E74] mt-0.5">{step.metricValue}</span>
              </div>

              {/* Connecting arrows between items on desktop */}
              {index < steps.length - 1 && (
                <ChevronRight 
                  size={14} 
                  className={`hidden lg:block absolute left-[105%] top-4 text-[#DFD9CE] ${
                    steps[index].status === 'complete' ? 'text-[#C85A32]/40' : ''
                  }`} 
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Inspector Details Panel */}
      <AnimatePresence mode="wait">
        <motion.div 
          key={activeStep}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -15 }}
          transition={{ duration: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-12 gap-6 bg-[#FBF9F6] dark:bg-[#181513]/90 border border-[#E6E1D8] dark:border-[#2B2622] rounded-xl p-6 relative overflow-hidden paper-shadow-lg transition-colors duration-300"
        >
          {/* Subtle neon glowing sidebar indicator based on current section */}
          <div className="absolute left-0 top-0 bottom-0 w-[4px] bg-[#C85A32] dark:bg-[#E26838]" />

          {/* Module Description column */}
          <div className="md:col-span-4 flex flex-col justify-between">
            <div>
              <div className="text-[10px] font-mono tracking-widest text-[#C85A32] dark:text-[#E26838] uppercase mb-1 font-bold">
                INSPECTOR CORE • COMPONENT {steps.findIndex(s => s.id === activeStep) + 1} OF {steps.length}
              </div>
              <h4 className="text-xl font-serif text-[#191919] dark:text-[#FBF9F6] font-medium mb-2 flex items-center gap-2">
                {activeStepObj.name}
              </h4>
              <p className="text-sm text-[#545454] dark:text-[#A39A90] leading-relaxed">
                {activeStepObj.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-[#EBE5DC] dark:border-[#2B2622] flex gap-6">
              <div>
                <span className="block text-[10px] font-mono text-slate-500 dark:text-[#A39A90]/80 uppercase tracking-wider mb-0.5">Telemetry Label</span>
                <span className="text-xs font-mono text-[#191919] dark:text-[#FBF9F6] bg-[#F4EFEA] dark:bg-[#110F0E] px-2 py-1 rounded border border-[#E6E1D8] dark:border-[#2B2622] transition-colors">
                  {activeStepObj.metricLabel}
                </span>
              </div>
              <div>
                <span className="block text-[10px] font-mono text-slate-500 dark:text-[#A39A90]/80 uppercase tracking-wider mb-0.5">Value</span>
                <span className="text-xs font-mono text-[#C85A32] dark:text-[#E26838] bg-[#C85A32]/5 dark:bg-[#E26838]/10 px-2 py-1 rounded border border-[#C85A32]/20 dark:border-[#E26838]/20 transition-colors">
                  {activeStepObj.metricValue}
                </span>
              </div>
            </div>
          </div>

          {/* Real-Time Live Logs console simulator */}
          <div className="md:col-span-8 flex flex-col bg-[#F4EFEA] dark:bg-[#110F0E] rounded-lg border border-[#EBE5DC] dark:border-[#2B2622] p-4 font-mono text-xs text-[#191919] dark:text-[#FBF9F6] transition-colors duration-300">
            <div className="flex items-center justify-between pb-3 border-b border-[#EBE5DC] dark:border-[#2B2622] mb-3">
              <span className="text-[10px] text-[#545454] dark:text-[#A39A90] uppercase tracking-widest font-bold">KERNEL LOG STREAM</span>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#C85A32] dark:bg-[#E26838] animate-pulse" />
                <span className="text-[9px] text-[#C85A32] dark:text-[#E26838]">LISTENING</span>
              </div>
            </div>

            <div className="flex-1 space-y-3 leading-relaxed max-h-[140px] overflow-y-auto">
              <div className="text-slate-500 dark:text-[#A39A90]/70">
                [ {new Date().toLocaleTimeString()} ] INF INITIALIZING CONTEXT ENGINE DISPATCHER...
              </div>
              <div className="text-slate-500 dark:text-[#A39A90]/70">
                [ {new Date().toLocaleTimeString()} ] INF STAGE DETECTED: {activeStepObj.name.toUpperCase()}
              </div>
              <div className="text-[#C85A32] dark:text-[#E26838] font-semibold">
                &gt; {activeStepObj.telemetry}
              </div>
              <div className="text-[#191919] dark:text-[#FBF9F6] leading-snug break-all text-[11px] font-semibold">
                SYSTEM_STATE: {'{'} stage: "{activeStepObj.id}", buffer_payload_size: "{activeStepObj.metricValue}", relevance_coefficient: {relevanceScore} {'}'}
              </div>
            </div>

            {/* Simulated progress slider in console footer */}
            <div className="mt-4 pt-3 border-t border-[#EBE5DC] dark:border-[#2B2622] flex items-center justify-between text-[10px] text-slate-500 dark:text-[#A39A90]/80">
              <span>COMPILATION: COMPLETE</span>
              <span>SHA-256: 0x{activeStepObj.id.toUpperCase().padEnd(8, '4')}...9E</span>
            </div>
          </div>

        </motion.div>
      </AnimatePresence>
    </div>
  );
};
