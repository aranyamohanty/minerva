import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Network, Cpu, Layers, GitFork, 
  Terminal, ShieldCheck, Database, Compass, Radio 
} from 'lucide-react';
import { ArchitectureModule } from '../types';

export const CognitiveArchitecture: React.FC = () => {
  const [hoveredModule, setHoveredModule] = useState<string | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>('graph');

  // Architecture modules distributed around center (0,0)
  const modules: ArchitectureModule[] = [
    {
      id: 'vector',
      name: 'Vector Search',
      category: 'Indexing Engine',
      description: 'Locates raw candidate matches using 1536-dimensional float vectors and custom cosine kernels.',
      x: 0,
      y: -140,
      angle: 270,
      dependencies: ['core', 'embedding'],
      details: 'Integrates HNSW indexing with scalar quantization to perform nearest neighbor queries on millions of vectors with < 3ms latencies.'
    },
    {
      id: 'graph',
      name: 'Knowledge Graph',
      category: 'Semantic Struct',
      description: 'Maintains strict relational links between files, topics, meeting summaries, and operational goals.',
      x: 110,
      y: -90,
      angle: 320,
      dependencies: ['core', 'vector'],
      details: 'Expresses relationships as a semantic database of subject-predicate-object triples. Enables deep hop walks to find correlated entities.'
    },
    {
      id: 'mmr',
      name: 'MMR Engine',
      category: 'Relevance Diver',
      description: 'Iteratively filters context documents to maximize information density and cancel redundancy.',
      x: 140,
      y: 30,
      angle: 12,
      dependencies: ['core'],
      details: 'Uses Maximal Marginal Relevance algorithms. Prevents the AI model from seeing the exact same code blocks, saving tremendous token space.'
    },
    {
      id: 'compiler',
      name: 'Prompt Compiler',
      category: 'Synthesizer',
      description: 'Transforms compressed, ranked text nodes into structural LLM prompt packages.',
      x: 90,
      y: 120,
      angle: 50,
      dependencies: ['core', 'compression'],
      details: 'Structures final compiled text with semantic boundary dividers, protecting context from model hallucinations or direct prompt injections.'
    },
    {
      id: 'compression',
      name: 'Compression Layer',
      category: 'Optimizing Pipeline',
      description: 'Linguistically strips whitespace, repetitive idioms, boilerplate, and low-entropy grammatical constructs.',
      x: -90,
      y: 120,
      angle: 130,
      dependencies: ['core'],
      details: 'Uses entropy thresholds to remove unnecessary syntactic tokens, guaranteeing maximum context coverage without sacrificing comprehension.'
    },
    {
      id: 'embedding',
      name: 'Embedding Engine',
      category: 'Vectorization',
      description: 'Generates mathematical vectors from incoming database additions or code commits.',
      x: -140,
      y: 30,
      angle: 180,
      dependencies: ['vector'],
      details: 'Built-in local small language embeddings. Runs bge-small-en-v1.5 locally on CPU via ONNX Runtime for zero-cloud dependency.'
    },
    {
      id: 'mcp',
      name: 'MCP Interface',
      category: 'Communication Protocol',
      description: 'Model Context Protocol linking third-party editors directly to internal context graphs.',
      x: -110,
      y: -90,
      angle: 220,
      dependencies: ['core', 'clients'],
      details: 'Implements the Model Context Protocol (MCP) by Anthropic, enabling seamless read-write permissions inside VS Code, Cursor, or Windsurf.'
    },
    {
      id: 'clients',
      name: 'AI Clients',
      category: 'Target Consumers',
      description: 'Receiving models including OpenAI GPT-4o, Claude 3.5 Sonnet, and Gemini Pro.',
      x: -150,
      y: -150,
      angle: 235,
      dependencies: ['mcp'],
      details: 'Ingests compiled payloads directly via API calls or workspace integrations. Guarantees 0-cache misses and extreme semantic density.'
    }
  ];

  const getModuleIcon = (id: string, color: string) => {
    switch (id) {
      case 'vector': return <Database className={color} size={16} />;
      case 'graph': return <Network className={color} size={16} />;
      case 'mmr': return <GitFork className={color} size={16} />;
      case 'compiler': return <Terminal className={color} size={16} />;
      case 'compression': return <Cpu className={color} size={16} />;
      case 'embedding': return <Layers className={color} size={16} />;
      case 'mcp': return <Radio className={color} size={16} />;
      case 'clients': return <ShieldCheck className={color} size={16} />;
      default: return <Compass className={color} size={16} />;
    }
  };

  const selectedModuleObj = modules.find(m => m.id === selectedModule) || modules[0];
  const activeHoverObj = hoveredModule ? modules.find(m => m.id === hoveredModule) : null;

  return (
    <div className="relative bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-2xl p-6 lg:p-10 overflow-hidden paper-shadow transition-colors duration-300">
      
      {/* Decorative side editorial flare */}
      <div className="absolute bottom-0 left-0 w-80 h-80 rounded-full bg-[#C85A32]/5 dark:bg-[#E26838]/5 blur-[80px] pointer-events-none" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        {/* Orbital interactive visualizer map */}
        <div className="lg:col-span-7 flex flex-col items-center justify-center min-h-[380px] lg:min-h-[460px] relative">
          
          {/* Subtle background radar circles */}
          <div className="absolute w-[280px] h-[280px] border border-[#E6E1D8] dark:border-[#2B2622]/50 rounded-full animate-pulse-glow" style={{ animationDuration: '6s' }} />
          <div className="absolute w-[180px] h-[180px] border border-[#E6E1D8] dark:border-[#2B2622]/50 rounded-full" />
          <div className="absolute w-[380px] h-[380px] border border-[#EBE5DC]/50 dark:border-[#2B2622]/20 rounded-full hidden md:block" />

          {/* SVG Connection Lines */}
          <div className="absolute inset-0 z-0 pointer-events-none">
            <svg className="w-full h-full" viewBox="-200 -200 400 400">
              {/* Lines from satellites to core */}
              {modules.map((m) => {
                const isDependencyHighlighted = 
                  hoveredModule === m.id || 
                  hoveredModule === 'core' ||
                  (hoveredModule && m.dependencies.includes(hoveredModule)) ||
                  (activeHoverObj && activeHoverObj.dependencies.includes(m.id));

                const color = isDependencyHighlighted 
                  ? 'var(--color-terracotta)' 
                  : selectedModule === m.id 
                    ? 'var(--color-charcoal)' 
                    : 'var(--color-sand-border)';
                
                const width = isDependencyHighlighted ? '1.5' : '1';

                return (
                  <g key={`lines-${m.id}`}>
                    <line
                      x1={0}
                      y1={0}
                      x2={m.x}
                      y2={m.y}
                      stroke={color}
                      strokeWidth={width}
                      strokeDasharray={isDependencyHighlighted ? '3, 3' : 'none'}
                      className={isDependencyHighlighted ? 'animate-signal-flow' : ''}
                      transition="stroke 0.3s"
                    />

                    {/* Satellites with dependency links between themselves */}
                    {m.dependencies.map(depId => {
                      if (depId !== 'core') {
                        const targetItem = modules.find(item => item.id === depId);
                        if (targetItem) {
                          const isSpecialActive = (hoveredModule === m.id || hoveredModule === depId);
                          return (
                            <line
                              key={`dep-${m.id}-${depId}`}
                              x1={m.x}
                              y1={m.y}
                              x2={targetItem.x}
                              y2={targetItem.y}
                              stroke={isSpecialActive ? 'var(--color-terracotta)' : 'var(--color-sand-border)'}
                              strokeWidth={isSpecialActive ? '1.5' : '0.8'}
                              strokeDasharray={isSpecialActive ? '4,4' : 'none'}
                              className={isSpecialActive ? 'animate-signal-flow' : ''}
                            />
                          );
                        }
                      }
                      return null;
                    })}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Core Center Node */}
          <div 
            className="absolute z-20 flex flex-col items-center justify-center cursor-pointer group"
            onMouseEnter={() => setHoveredModule('core')}
            onMouseLeave={() => setHoveredModule(null)}
            onClick={() => setSelectedModule('graph')}
          >
            <div className="w-18 h-18 rounded-full border border-[#E6E1D8] dark:border-[#2B2622] bg-[#FBF9F6] dark:bg-[#181513] flex items-center justify-center p-0.5 shadow-md relative transition-all duration-500 group-hover:scale-105 group-hover:border-[#C85A32]/50">
              {/* Spinning out rings */}
              <div className="absolute inset-0 rounded-full border border-dashed border-[#C85A32]/20 dark:border-[#E26838]/30 animate-slow-rotate" />
              <div className="absolute -inset-2 rounded-full border border-[#DFD9CE]/30 dark:border-[#2B2622]/40 animate-medium-rotate" style={{ animationDirection: 'reverse' }} />
              
              <div className="w-full h-full rounded-full bg-[#E9E1D8] dark:bg-[#27221E] border border-[#DFD9CE] dark:border-[#2B2622] flex flex-col items-center justify-center z-10 shadow-inner">
                <Cpu size={24} className="text-[#C85A32] dark:text-[#E26838] animate-pulse" />
                <span className="text-[8px] font-mono font-bold uppercase tracking-widest text-[#545454] dark:text-[#A39A90] mt-1">CORE</span>
              </div>
            </div>
            {/* Core Label */}
            <span className="text-[10px] font-mono font-black tracking-widest text-[#C85A32] dark:text-[#E26838] mt-2 group-hover:text-[#191919] dark:group-hover:text-[#F5EFEA] transition-colors">
              MINERVA CORE
            </span>
          </div>

          {/* Orbiting Satellite Nodes */}
          {modules.map((m, idx) => {
            const isHovered = hoveredModule === m.id;
            const isSelected = selectedModule === m.id;
            
            // Determine styles dynamically Based on context
            const activeColor = isHovered 
              ? 'border-[#C85A32] dark:border-[#E26838] text-[#C85A32] dark:text-[#E26838] bg-[#FBF9F6] dark:bg-[#181513] shadow-sm' 
              : isSelected 
                ? 'border-[#191919] dark:border-[#FBF9F6] text-[#191919] dark:text-[#FBF9F6] bg-[#E9E1D8] dark:bg-[#27221E] shadow-inner' 
                : 'border-[#E6E1D8] dark:border-[#2B2622] text-[#545454] dark:text-[#A39A90] bg-[#FBF9F6] dark:bg-[#181513]';

            return (
              <motion.div
                key={m.id}
                className="absolute z-10"
                style={{
                  x: m.x,
                  y: m.y,
                  translateX: "-50%",
                  translateY: "-50%"
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 350, damping: 24, delay: idx * 0.02 }}
                whileHover={{ scale: 1.15 }}
              >
                <button
                  onMouseEnter={() => setHoveredModule(m.id)}
                  onMouseLeave={() => setHoveredModule(null)}
                  onClick={() => setSelectedModule(m.id)}
                  className={`w-10 h-10 rounded-full border flex items-center justify-center active:scale-95 transition-all duration-300 group cursor-pointer ${activeColor}`}
                >
                  <div className="transition-transform group-hover:rotate-12 duration-300 text-current">
                    {getModuleIcon(m.id, 'text-current')}
                  </div>

                  {/* Micro floating title hint */}
                  <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[9px] font-mono tracking-wider bg-[#191919] text-[#FBF9F6] border border-[#545454]/10 py-0.5 px-2 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-all scale-90 group-hover:scale-100 z-50">
                    {m.name}
                  </span>
                </button>
              </motion.div>
            );
          })}

        </div>

        {/* Selected Module Metadata Inspector panel */}
        <div className="lg:col-span-5 flex flex-col justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedModule}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] rounded-xl p-6 relative paper-shadow-lg transition-colors duration-300"
            >
              <div className="flex items-center justify-between border-b border-[#E6E1D8] dark:border-[#2B2622] pb-4 mb-4">
                <div>
                  <span className="text-[10px] font-mono text-[#C85A32] dark:text-[#E26838] uppercase tracking-widest block mb-0.5 font-bold">
                    {selectedModuleObj.category}
                  </span>
                  <h3 className="text-xl font-serif text-[#191919] dark:text-[#FBF9F6] font-medium">
                    {selectedModuleObj.name}
                  </h3>
                </div>
                {getModuleIcon(selectedModuleObj.id, 'text-[#C85A32] dark:text-[#E26838] w-8 h-8 p-1.5 bg-[#F4EFEA] dark:bg-[#110F0E] rounded-md border border-[#E6E1D8] dark:border-[#2B2622]')}
              </div>

              <p className="text-sm text-[#545454] dark:text-[#A39A90] mb-4 leading-relaxed">
                {selectedModuleObj.description}
              </p>

              <div className="bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] p-4 rounded-lg font-mono text-xs text-[#545454] dark:text-[#A39A90] leading-relaxed mb-4 transition-colors duration-300">
                <span className="text-[#C85A32] dark:text-[#E26838] font-bold block mb-1">SYSTEM INSTANTIATION</span>
                {selectedModuleObj.details}
              </div>

              {/* Connected channels logs */}
              <div className="space-y-2 mt-4">
                <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest font-black block">
                  SYSTEM RELATIONAL PATHS
                </span>
                
                <div className="flex flex-wrap gap-2">
                  <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-full text-[10px] font-mono text-[#545454] dark:text-[#A39A90]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#C85A32] dark:bg-[#E26838]" />
                    <span>ConOS Core</span>
                  </div>

                  {selectedModuleObj.dependencies.map(dep => {
                    const matchedDep = modules.find(mod => mod.id === dep);
                    if (!matchedDep) return null;
                    return (
                      <div key={dep} className="flex items-center gap-1.5 px-2.5 py-1 bg-[#C85A32]/5 dark:bg-[#E26838]/10 border border-[#C85A32]/20 dark:border-[#E26838]/20 rounded-full text-[10px] font-mono text-[#545454] dark:text-[#A39A90]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#C85A32] dark:bg-[#E26838]" />
                        <span>{matchedDep.name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

            </motion.div>
          </AnimatePresence>
          
          <div className="mt-4 px-4 py-2 bg-[#E9E1D8] dark:bg-[#27221E] border border-[#DFD9CE] dark:border-[#2B2622] rounded-lg text-[#545454] dark:text-[#A39A90] text-[10px] font-mono flex items-center justify-between text-center transition-colors duration-300">
            <span>CORE CLOCK SPEED: 4.8 GHZ</span>
            <span>NODE COUNT: 9 ACTIVE</span>
          </div>
        </div>

      </div>

    </div>
  );
};
