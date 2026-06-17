import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Rocket, Circle, CheckCircle2, ArrowRight, ChevronDown, HelpCircle
} from 'lucide-react';
import { RoadmapPhase } from '../types';

export const RoadmapOrbit: React.FC = () => {
  const [selectedPhaseIdx, setSelectedPhaseIdx] = useState<number>(0); // Highlight Phase 1 initially
  const [expandedMsIdx, setExpandedMsIdx] = useState<number | null>(null);

  const roadmapPhases: RoadmapPhase[] = [
    {
      phase: '01',
      title: 'Memory Engine & MCP Core',
      description: 'Establish the core local-first structured database registry, embedding model pipeline, and MCP stdio tools.',
      status: 'completed',
      progress: 100,
      orbitalDistance: 100,
      baseAngle: 180,
      milestones: [
        {
          title: 'Local SQLite Structured Memory',
          completed: true,
          details: 'Robust database schema with project scoping, soft-deletes, audit logging, and schema migrations.'
        },
        {
          title: 'Local BGE-Small Embeddings',
          completed: true,
          details: 'CPU-efficient ONNX runtime execution of bge-small-en-v1.5 with zero cloud latency and no external data egress.'
        },
        {
          title: 'Hybrid FTS5 + Vector Retrieval',
          completed: true,
          details: 'Weighted search scoring combining BM25 keyword relevance, vector cosine similarity, recency decay, and importance.'
        },
        {
          title: 'MMR & Link Boosting Filters',
          completed: true,
          details: 'Maximal Marginal Relevance to suppress duplicates, and relationship link boosts to bubble relevant contexts.'
        },
        {
          title: 'Universal XML Prompt Compiler',
          completed: true,
          details: 'Strict token budget check with a 0.85 safety margin and dynamic capacity redistribution.'
        },
        {
          title: 'FastMCP stdio Integration',
          completed: true,
          details: '14 named tools and 4 resources exposing active contexts directly to Cursor, Windsurf, and Claude Desktop.'
        }
      ]
    },
    {
      phase: '02',
      title: 'Web Integration Extensions',
      description: 'Expand prompt context interception and DOM observers to standard web browsers and chat systems.',
      status: 'future',
      progress: 0,
      orbitalDistance: 130,
      baseAngle: 215,
      milestones: [
        {
          title: 'Chrome & Firefox Extensions',
          completed: false,
          details: 'Develop WebExtensions APIs to execute context injections inside active web tab pages.'
        },
        {
          title: 'DOM Event Listeners for Web UIs',
          completed: false,
          details: 'Interceptors for Claude.ai, ChatGPT, and Gemini web input fields to inject context on-the-fly.'
        },
        {
          title: 'Local Browser-Sync Bridge',
          completed: false,
          details: 'Expose local-daemon socket communication interface to browser processes securely.'
        },
        {
          title: 'Web Workspace Scopes Panel',
          completed: false,
          details: 'Side-panel overlay inside the browser displaying active project memory nodes and constraints.'
        }
      ]
    },
    {
      phase: '03',
      title: 'IDE Extensions & Code Interception',
      description: 'Deploy native plugins to inject context directly into active IDE workflows.',
      status: 'future',
      progress: 0,
      orbitalDistance: 160,
      baseAngle: 250,
      milestones: [
        {
          title: 'VS Code Extension public release',
          completed: false,
          details: 'Marketplace package displaying directory scopes, active tasks, and context configuration properties.'
        },
        {
          title: 'Cursor / Windsurf Interceptor',
          completed: false,
          details: 'Custom proxy layer to hijack Cursor Cmd-K / Windsurf Cascade chat queries and inject re-ranked prompt context.'
        },
        {
          title: 'Active file change listeners',
          completed: false,
          details: 'Real-time filesystem watchers to stream edit differences directly to the memory engine.'
        },
        {
          title: 'Inline editor context annotations',
          completed: false,
          details: 'Display constraint markers and related decision highlights inline directly in the editor scroll margins.'
        }
      ]
    },
    {
      phase: '04',
      title: 'Cognitive Reasoner & Local Re-rank',
      description: 'Upgrade the core vector database retrieval to support deep link-hops and heavy local reranking models.',
      status: 'future',
      progress: 0,
      orbitalDistance: 190,
      baseAngle: 285,
      milestones: [
        {
          title: 'Multi-hop graph walk reasoning',
          completed: false,
          details: 'Recursive entity graph traversal to assemble contexts separated by multi-level relationship edges.'
        },
        {
          title: 'Automated file linking engines',
          completed: false,
          details: 'Local heuristic analysis to link files to goals, decisions, or constraints automatically without manual intervention.'
        },
        {
          title: 'BERT Local Cross-Encoder Rerank',
          completed: false,
          details: 'Run small BERT cross-encoders locally on CPU to score and rerank final candidate nodes.'
        },
        {
          title: 'Dynamic compiler prompt templates',
          completed: false,
          details: 'Allow custom user-specified XML tags and structural formats for different model target endpoints.'
        }
      ]
    },
    {
      phase: '05',
      title: 'P2P Sync & Collaborative Intel',
      description: 'Establish peer-to-peer sandboxed sync clusters and optional cloud synchronization servers.',
      status: 'future',
      progress: 0,
      orbitalDistance: 220,
      baseAngle: 320,
      milestones: [
        {
          title: 'P2P Encrypted Memory Sharing',
          completed: false,
          details: 'Mesh network sync enabling developers in a local repository to share structural contexts securely.'
        },
        {
          title: 'Remote Project Sync Clusters',
          completed: false,
          details: 'Resolve conflict-free replicated data types (CRDTs) to sync memory branches between multiple workspaces.'
        },
        {
          title: 'Cloud E2E Sync (Paid B2B Tier)',
          completed: false,
          details: 'Zero-knowledge cloud synchronization service where user hosts keys and our servers synchronize encrypted payloads.'
        },
        {
          title: 'Community Context Plugins registry',
          completed: false,
          details: 'Allow developers to publish and download pre-defined context libraries (e.g. legal compliance frameworks).'
        }
      ]
    }
  ];

  const activePhase = roadmapPhases[selectedPhaseIdx];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-[10px] font-mono text-emerald-800 dark:text-emerald-400 uppercase font-bold tracking-wider">Deploy Completed</span>;
      case 'in-progress':
        return <span className="px-2.5 py-0.5 rounded-full bg-[#C85A32]/15 border border-[#C85A32]/30 text-[10px] font-mono text-[#C85A32] dark:text-[#E26838] uppercase font-bold tracking-wider">Active Sprints</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] text-[10px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-wide">Scheduled Horizon</span>;
    }
  };

  // Reset expanded milestone detail on phase change
  React.useEffect(() => {
    setExpandedMsIdx(null);
  }, [selectedPhaseIdx]);

  return (
    <div className="relative bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-2xl p-6 lg:p-10 overflow-hidden paper-shadow transition-colors duration-300">
      
      {/* Decorative background grid and halo */}
      <div className="absolute inset-0 grid-bg opacity-10 dark:opacity-[0.04] pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #DFD9CE 1px, transparent 1px)', backgroundSize: '16px 16px' }} />
      <div className="absolute top-1/2 left-0 w-80 h-80 rounded-full bg-[#C85A32]/5 dark:bg-[#E26838]/5 blur-[70px] pointer-events-none" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
        
        {/* Left Side: Sweeping orbital arc roadmap diagram */}
        <div className="lg:col-span-5 flex items-center justify-center min-h-[300px] lg:min-h-[380px] relative">
          
          {/* Circular orbital tracks (nested roadmap arcs) */}
          {roadmapPhases.map((rp, idx) => (
            <div 
              key={`orbit-line-${idx}`}
              className="absolute border border-[#E1DAD0] dark:border-[#2B2622]/40"
              style={{
                width: rp.orbitalDistance * 2.2,
                height: rp.orbitalDistance * 2.2,
                top: `calc(50% - ${rp.orbitalDistance * 1.1}px)`,
                left: `calc(50% - ${rp.orbitalDistance * 1.1}px)`
              }}
            />
          ))}

          {/* Sweeping road arc overlay */}
          <div className="absolute w-[240px] h-[240px] border-l-2 border-b-2 border-gradient border-dashed border-[#C85A32]/10 dark:border-[#E26838]/10 rounded-full rotate-45 pointer-events-none" />

          {/* Core System launch anchor */}
          <div className="absolute z-10 flex flex-col items-center">
            <div className="w-12 h-12 rounded-full border border-[#EBE5DC] dark:border-[#2B2622] bg-[#FBF9F6] dark:bg-[#181513] flex items-center justify-center shadow-sm select-none">
              <Rocket size={18} className="text-[#C85A32] dark:text-[#E26838] animate-bounce" />
            </div>
            <span className="text-[8px] font-mono font-black text-slate-500 dark:text-[#A39A90]/60 uppercase tracking-widest mt-1.5">LAUNCH</span>
          </div>

          {/* Connected Orbital Nodes rendering */}
          {roadmapPhases.map((rp, idx) => {
            // Polar coordinates calculation
            const angleRad = (rp.baseAngle * Math.PI) / 180;
            const x = Math.cos(angleRad) * rp.orbitalDistance * 1.1;
            const y = Math.sin(angleRad) * rp.orbitalDistance * 1.1;

            const isSelected = idx === selectedPhaseIdx;
            
            // Build visual configuration states
            let nodeBorder = 'border-[#EBE5DC] dark:border-[#2B2622] bg-[#FBF9F6] dark:bg-[#181513] text-[#545454] dark:text-[#A39A90]';
            if (isSelected) {
              nodeBorder = 'border-[#C85A32] dark:border-[#E26838] bg-[#FBF9F6] dark:bg-[#110F0E] text-[#C85A32] dark:text-[#E26838] ring-4 ring-[#C85A32]/15 dark:ring-[#E26838]/15 scale-110 shadow-md';
            } else if (rp.status === 'completed') {
              nodeBorder = 'border-emerald-400 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400';
            }

            return (
              <motion.div
                key={`phase-node-${rp.phase}`}
                className="absolute z-20"
                style={{
                  x,
                  y,
                  translateX: "-50%",
                  translateY: "-50%"
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 350, damping: 24, delay: idx * 0.03 }}
                whileHover={{ scale: 1.15 }}
              >
                <div 
                  className="relative group cursor-pointer"
                  onClick={() => setSelectedPhaseIdx(idx)}
                >
                  <div className={`w-8 h-8 rounded-full border flex items-center justify-center font-mono text-xs font-black transition-all group-hover:scale-110 active:scale-95 select-none ${nodeBorder}`}>
                    {rp.phase}
                  </div>

                  {/* Bubble popup hint */}
                  <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] py-1 px-2.5 rounded text-[9px] font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-all scale-95 group-hover:scale-100 z-50 shadow-md">
                    <span className="font-semibold block text-[#191919] dark:text-[#FBF9F6]">{rp.title}</span>
                  </div>
                </div>
              </motion.div>
            );
          })}

        </div>

        {/* Right Side: Active phase inspector panel card */}
        <div className="lg:col-span-7 flex flex-col justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedPhaseIdx}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] rounded-xl p-6 lg:p-8 paper-shadow-lg relative z-30 transition-colors duration-300 flex flex-col justify-between"
            >
              <div>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#EBE5DC] dark:border-[#2B2622] pb-4 mb-4">
                  <div>
                    <span className="text-[10px] font-mono text-[#C85A32] dark:text-[#E26838] uppercase tracking-widest block mb-0.5 font-bold">
                      DEVELOPER CHRONOLOGY • PHASE {activePhase.phase}
                    </span>
                    <h3 className="text-2xl font-serif text-[#191919] dark:text-[#FBF9F6] font-medium">
                      {activePhase.title}
                    </h3>
                  </div>

                  <div className="self-start md:self-center">
                    {getStatusBadge(activePhase.status)}
                  </div>
                </div>

                {/* Progress bar HUD */}
                <div className="mb-4">
                  <div className="flex justify-between items-center text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-wider mb-1">
                    <span>Phase Completion Progress</span>
                    <span className="font-bold">{activePhase.progress}%</span>
                  </div>
                  <div className="w-full bg-[#EBE5DC] dark:bg-[#2B2622] h-1 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${activePhase.progress}%` }}
                      transition={{ duration: 0.6, ease: "easeOut" }}
                      className="bg-gradient-to-r from-[#C85A32] to-[#E26838] h-full rounded-full"
                    />
                  </div>
                </div>

                <p className="text-xs font-mono text-[#545454] dark:text-[#A39A90] mb-5 leading-relaxed bg-[#F4EFEA]/40 dark:bg-[#110F0E]/40 p-3 rounded-lg border border-[#EBE5DC]/55 dark:border-[#2B2622]/55">
                  {activePhase.description}
                </p>

                {/* Milestones listed checkpoint checklist */}
                <div className="space-y-3">
                  <span className="text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest font-black block mb-1">
                    DEVELOPMENT MILESTONES (Click for technical spec)
                  </span>

                  <div className="grid grid-cols-1 gap-2">
                    {activePhase.milestones.map((ms, index) => {
                      const isExpanded = expandedMsIdx === index;
                      return (
                        <div key={`ms-${index}`} className="flex flex-col">
                          <button 
                            onClick={() => setExpandedMsIdx(isExpanded ? null : index)}
                            className={`flex items-center justify-between p-2.5 bg-[#F4EFEA] dark:bg-[#110F0E] hover:bg-[#EDE7DF] dark:hover:bg-[#1C1816] border border-[#EBE5DC] dark:border-[#2B2622] rounded-lg text-xs transition-all text-left cursor-pointer group ${
                              isExpanded ? 'border-[#C85A32]/45 dark:border-[#E26838]/45 ring-1 ring-[#C85A32]/10 dark:ring-[#E26838]/10' : ''
                            }`}
                          >
                            <div className="flex items-center gap-2.5">
                              <div className="flex-shrink-0">
                                {ms.completed ? (
                                  <CheckCircle2 size={13} className="text-emerald-600 dark:text-emerald-400" />
                                ) : (
                                  <Circle size={13} className="text-slate-400 dark:text-slate-600" />
                                )}
                              </div>
                              <span className="text-[#191919] dark:text-[#FBF9F6] font-medium leading-tight">{ms.title}</span>
                            </div>
                            <ChevronDown 
                              size={12} 
                              className={`text-slate-400 transition-transform ${isExpanded ? 'rotate-180 text-[#C85A32] dark:text-[#E26838]' : ''}`} 
                            />
                          </button>
                          
                          <AnimatePresence initial={false}>
                            {isExpanded && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.14, ease: "easeOut" }}
                                className="overflow-hidden"
                              >
                                <div className="p-3 mt-1 rounded-lg bg-[#FBF9F6] dark:bg-[#181513] border border-dashed border-[#EBE5DC] dark:border-[#2B2622] text-[11px] text-slate-500 dark:text-[#A39A90] font-light leading-relaxed flex gap-2">
                                  <HelpCircle size={12} className="text-[#C85A32] dark:text-[#E26838] shrink-0 mt-0.5" />
                                  <span>{ms.details}</span>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Stepper controls */}
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-[#EBE5DC] dark:border-[#2B2622]">
                <button
                  disabled={selectedPhaseIdx === 0}
                  onClick={() => setSelectedPhaseIdx(prev => Math.max(0, prev - 1))}
                  className="px-3 py-1.5 rounded-lg border border-[#EBE5DC] dark:border-[#2B2622] text-[10px] font-mono uppercase tracking-wider font-semibold disabled:opacity-40 hover:bg-[#EDE7DF] dark:hover:bg-[#1C1816] transition-colors cursor-pointer select-none text-[#191919] dark:text-[#FBF9F6]"
                >
                  &larr; Back
                </button>
                <div className="flex gap-1.5">
                  {roadmapPhases.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedPhaseIdx(i)}
                      className={`w-2 h-2 rounded-full transition-all cursor-pointer ${
                        i === selectedPhaseIdx 
                          ? 'bg-[#C85A32] dark:bg-[#E26838] w-4' 
                          : 'bg-slate-300 dark:bg-slate-800'
                      }`}
                    />
                  ))}
                </div>
                <button
                  disabled={selectedPhaseIdx === roadmapPhases.length - 1}
                  onClick={() => setSelectedPhaseIdx(prev => Math.min(roadmapPhases.length - 1, prev + 1))}
                  className="px-3 py-1.5 rounded-lg border border-[#EBE5DC] dark:border-[#2B2622] text-[10px] font-mono uppercase tracking-wider font-semibold disabled:opacity-40 hover:bg-[#EDE7DF] dark:hover:bg-[#1C1816] transition-colors cursor-pointer select-none text-[#191919] dark:text-[#FBF9F6]"
                >
                  Next &rarr;
                </button>
              </div>

            </motion.div>
          </AnimatePresence>
        </div>

      </div>

    </div>
  );
};
