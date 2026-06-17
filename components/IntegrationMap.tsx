import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Terminal, Braces, Code, Laptop, Sparkles, Compass, Layers 
} from 'lucide-react';
import { IntegrationEntity } from '../types';

export const IntegrationMap: React.FC = () => {
  const [activeIntegration, setActiveIntegration] = useState<string | null>('cursor');

  const integrations: IntegrationEntity[] = [
    { id: 'cursor', name: 'Cursor AI Editor', iconName: 'editor', color: '#E26838', angle: 0, radius: 130 },
    { id: 'vscode', name: 'VS Code Extension', iconName: 'editor', color: '#40A9FF', angle: 51.4, radius: 135 },
    { id: 'windsurf', name: 'Windsurf IDE', iconName: 'editor', color: '#84CC16', angle: 102.8, radius: 130 },
    { id: 'openai', name: 'OpenAI API Proxy', iconName: 'api', color: '#06B6D4', angle: 154.2, radius: 140 },
    { id: 'claude', name: 'Claude API Layer', iconName: 'model', color: '#EC4899', angle: 205.6, radius: 135 },
    { id: 'anthropic', name: 'Anthropic MCP Sync', iconName: 'api', color: '#F59E0B', angle: 257, radius: 130 },
    { id: 'gemini', name: 'Google Gemini Pro', iconName: 'model', color: '#8B5CF6', angle: 308.4, radius: 140 }
  ];

  const getEntityIcon = (iconName: string, id: string) => {
    switch (id) {
      case 'cursor': return <Laptop size={16} />;
      case 'vscode': return <Code size={16} />;
      case 'windsurf': return <Terminal size={16} />;
      case 'openai': return <Sparkles size={16} />;
      case 'claude': return <Layers size={16} />;
      case 'anthropic': return <Braces size={16} />;
      case 'gemini': return <Compass size={16} />;
      default: return <Sparkles size={16} />;
    }
  };

  const activeEntity = integrations.find(i => i.id === activeIntegration) || integrations[0];

  return (
    <div className="relative bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#E6E1D8] dark:border-[#2B2622] rounded-2xl p-6 lg:p-10 overflow-hidden paper-shadow transition-colors duration-300">
      
      {/* Dynamic ambient center light flare */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-[#C85A32]/5 dark:bg-[#E26838]/5 blur-[90px] pointer-events-none" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        {/* Left Side: Interconnected circular graph network */}
        <div className="lg:col-span-7 flex items-center justify-center min-h-[380px] lg:min-h-[440px] relative">
          
          {/* Orbital tracks visualizers */}
          <div className="absolute w-[260px] h-[260px] border border-[#E6E1D8]/60 dark:border-[#2B2622]/40 rounded-full" />
          <div className="absolute w-[180px] h-[180px] border border-dashed border-[#EBE5DC] dark:border-[#2B2622]/50 rounded-full animate-slow-rotate" />
          <div className="absolute w-[100px] h-[100px] border border-[#DFD9CE] dark:border-[#2B2622]/30 rounded-full" />

          {/* Core Central System (Minerva Nodes representation) */}
          <div className="absolute z-20 flex flex-col items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-[#F4EFEA] dark:bg-[#110F0E] border-2 border-[#DFD9CE] dark:border-[#2B2622] flex items-center justify-center cursor-pointer select-none transition-colors">
              <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-[#C85A32] to-[#B0A695] flex flex-col items-center justify-center p-0.5 animate-pulse">
                <span className="text-[10px] font-mono font-bold tracking-tighter text-[#FBF9F6]">ConOS</span>
              </div>
            </div>
            <span className="text-[9px] font-mono font-black text-[#545454]/60 dark:text-[#A39A90]/50 tracking-widest mt-2 font-bold">GATEWAY</span>
          </div>

          {/* SVG Animated Connection Web */}
          <div className="absolute inset-0 pointer-events-none z-10">
            <svg className="w-full h-full" viewBox="-200 -200 400 400">
              {integrations.map((item) => {
                const angleRad = (item.angle * Math.PI) / 180;
                const tx = Math.cos(angleRad) * item.radius;
                const ty = Math.sin(angleRad) * item.radius;

                const isActive = activeIntegration === item.id;
                const strokeColor = isActive ? item.color : 'var(--color-sand-border)';
                const strokeWidth = isActive ? '1.5' : '1';

                return (
                  <g key={`edge-${item.id}`}>
                    <line
                      x1={0}
                      y1={0}
                      x2={tx}
                      y2={ty}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      strokeDasharray={isActive ? '4,4' : 'none'}
                      className={isActive ? 'animate-signal-flow' : ''}
                      transition="stroke 0.3s"
                    />

                    {/* Edge streaming payload circles (handshakes) */}
                    {isActive && (
                      <g>
                        <circle r="4" fill={item.color} className="animate-signal-flow">
                          <animateMotion
                            path={`M0,0 L${tx},${ty}`}
                            dur="2s"
                            repeatCount="indefinite"
                          />
                        </circle>
                        <circle r="8" fill="none" stroke={item.color} strokeWidth="1" opacity="0.4">
                          <animateMotion
                            path={`M0,0 L${tx},${ty}`}
                            dur="2s"
                            repeatCount="indefinite"
                          />
                        </circle>
                      </g>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Map floating satellites positions */}
          {integrations.map((item) => {
            const angleRad = (item.angle * Math.PI) / 180;
            const tx = Math.cos(angleRad) * item.radius;
            const ty = Math.sin(angleRad) * item.radius;

            const isActive = activeIntegration === item.id;

            return (
              <div
                key={item.id}
                className="absolute z-20 transition-all duration-300"
                style={{
                  transform: `translate(${tx}px, ${ty}px)`
                }}
              >
                <div 
                  className="relative group cursor-pointer"
                  onClick={() => setActiveIntegration(item.id)}
                >
                  <div 
                    className="w-10 h-10 rounded-xl bg-[#FBF9F6] dark:bg-[#181513] border flex items-center justify-center transition-all duration-300 transform group-hover:scale-110 active:scale-95 text-[#545454] dark:text-[#A39A90] group-hover:text-[#191919] dark:group-hover:text-[#FBF9F6]"
                    style={{
                      borderColor: isActive ? item.color : 'var(--color-sand-border)',
                      boxShadow: isActive ? `0 0 16px ${item.color}44` : 'none'
                    }}
                  >
                    <div style={{ color: isActive ? item.color : 'inherit' }}>
                      {getEntityIcon(item.iconName, item.id)}
                    </div>
                  </div>

                  {/* Absolute outer name ring tag */}
                  <span 
                    className="hidden md:block absolute -bottom-5 left-1/2 -translate-x-1/2 whitespace-nowrap text-[8px] font-mono tracking-widest transition-all"
                    style={{
                      color: isActive ? item.color : '#A39A90',
                      fontWeight: isActive ? 'bold' : 'normal'
                    }}
                  >
                    {item.name.split(' ')[0].toUpperCase()}
                  </span>
                </div>
              </div>
            );
          })}

        </div>

        {/* Right Side: Active integration description display panel */}
        <div className="lg:col-span-5 flex flex-col justify-center">
          <div className="text-[10px] font-mono text-[#C85A32] dark:text-[#E26838] tracking-widest uppercase mb-1 font-bold">
            CONTEXT DELIVERY ENDPOINTS
          </div>
          <h2 className="text-3xl font-serif text-[#191919] dark:text-[#FBF9F6] font-medium mb-4">
            Unified Ecosystem Sync
          </h2>
          <p className="text-sm text-[#545454] dark:text-[#A39A90] leading-relaxed mb-6">
            Minerva acts as the local transport protocol layer, broadcasting optimized prompt intelligence. By complying with the Model Context Protocol (MCP), it acts as a lightweight daemon connecting local knowledge banks to standard client tools.
          </p>

          <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] rounded-xl p-5 relative overflow-hidden paper-shadow transition-colors duration-300">
            <div 
              className="absolute left-0 top-0 bottom-0 w-[4px]"
              style={{ backgroundColor: activeEntity.color }}
            />
            
            <div className="flex items-center gap-2 mb-3">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: activeEntity.color }} />
              <span className="text-xs font-mono font-bold text-[#191919] dark:text-[#FBF9F6]">{activeEntity.name}</span>
            </div>

            <p className="text-xs text-[#545454] dark:text-[#A39A90] leading-relaxed">
              {activeEntity.id === 'cursor' && "Provides dynamic lock and goal files contexts directly inside the Cursor editor. Feeds re-ranked project schemas seamlessly over local socket connections, cutting inference misses by 95%."}
              {activeEntity.id === 'vscode' && "Powers the secondary Minerva background compiler in Visual Studio Code. Listens to workspace file edits, automatically binding goals and decisions in real time."}
              {activeEntity.id === 'windsurf' && "Feeds contextual reference frames to Windsurf cascades. Prompts remain 100% focused on active objectives, constraint bounds, and mathematical document maps."}
              {activeEntity.id === 'openai' && "Proxies API requests. Intercepts outgoing LLM payloads, compressing context windows from 18,000 to 1,900 tokens before re-routing, saving thousands in API overhead."}
              {activeEntity.id === 'claude' && "Maintains Anthropic compatible prompt layouts with optimal XML blocks. Ideal for projects using large structured directory trees."}
              {activeEntity.id === 'anthropic' && "Full client integration implementing Anthropics Model Context Protocol (MCP). Enables complete bi-directional reading and writing of directory structures."}
              {activeEntity.id === 'gemini' && "Integrates with Google Gemini models. Maps highly dimensional, complex multisequence syndromes and files directly over dense context windows."}
            </p>

            <div className="mt-4 pt-3 border-t border-[#EBE5DC] dark:border-[#2B2622] flex items-center justify-between text-[9px] font-mono text-slate-500 dark:text-[#A39A90]/80">
              <span>PROTOCOL: TCP/JSON-RPC</span>
              <span>STATE: SYNCHRONIZED</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
