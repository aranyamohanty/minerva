import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Copy, ClipboardCheck, Play, RotateCcw } from 'lucide-react';

interface TerminalCmdInfo {
  command: string;
  label: string;
  outputs: string[];
}

export const CommandLineTerminal: React.FC = () => {
  const [selectedCmdIdx, setSelectedCmdIdx] = useState<number>(0);
  const [typedCommand, setTypedCommand] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [visibleOutputs, setVisibleOutputs] = useState<string[]>([]);
  const [isCopied, setIsCopied] = useState<boolean>(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  
  const terminalCommands: TerminalCmdInfo[] = [
    {
      command: 'minerva init',
      label: 'Initialize Engine',
      outputs: [
        'Initializing local database registry directory...',
        'Creating memory repository partitions at .minerva/registry.db',
        'Configuring SQLite hybrid indices (BM25 FTS5 + Semantic vectors)... [OK]',
        'Downloading local embedding model BGE-small-en-v1.5 (cached, 130 MB)... [OK]',
        'Warm booting context scheduler in background daemon.',
        'Minerva successfully initialized. Watching directory: /Users/workspace/project'
      ]
    },
    {
      command: 'minerva add goal "Refactor lock scheduler in schema.ts" --priority 5',
      label: 'Inject Goal Node',
      outputs: [
        'Parsing critical developer intent...',
        'Added Goal #1',
        'Generated Objective Node: [GOAL-4029] "Refactor lock scheduler"',
        'Extracting local references... Found match in src/db/schema.ts (0.91 weight)',
        'Linking goal dependencies...',
        'Context mapping established: 1 Goal node connected to 4 document chunks.',
        'Local graph network re-indexed. 4,192 semantic vectors updated (3ms).'
      ]
    },
    {
      command: 'minerva link decision 1 goal 1',
      label: 'Establish Relationship',
      outputs: [
        'Verifying local project files...',
        'Generating unified embedding manifold representation...',
        'Linked decision #1 and goal #1 (Link #1)',
        'Relationship securely cached in context graph partition.'
      ]
    },
    {
      command: 'minerva search "Where are locked connection pools configured?"',
      label: 'Query Memory Graph',
      outputs: [
        'Converting query vector [ BGE-small-en-v1.5 - 384dim ]...',
        'Traversing local knowledge graph index and calculating cosine distance...',
        'Scanning 17,492 memory chunks... Found 3 target contexts:',
        '  - [Match 0.94] [DECISION #1] (Score: 0.94)',
        '  - [Match 0.89] docs/architecture.md (Section "Thread Locks") [Doc Node]',
        '  - [Match 0.72] src/config.ts (Line 11) [Config Node]',
        'Retrieval completed in 3.4ms.'
      ]
    },
    {
      command: 'minerva preview "Where are locked connection pools configured?" --budget 1000',
      label: 'Preview Context Window',
      outputs: [
        'Assembling relevant context payload...',
        'Compiling related goals, linked files, and recent terminal log context...',
        'Evaluating Token Budget... Original workspace layout count: 18,290 tokens.',
        'Initializing Minerva Lexical Optimizer (Token Compressor)...',
        'Staged 12 files... Retaining core syntactic references...',
        'Compressor finished saving: -75.42% tokens.',
        'Final Dense Context Compiled successfully: 1,940 focus tokens.',
        'Context payload cached: <system>...</system><project_context>...</project_context><relevant_history><!-- [Omitted 10 lower-scoring items] --></relevant_history>'
      ]
    }
  ];

  const typingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const outputTimerRef = useRef<NodeJS.Timeout | null>(null);
  const currentCmd = terminalCommands[selectedCmdIdx];

  const runCommandSim = () => {
    // Clear any existing active timer intervals to prevent overlapping simulation tasks
    if (typingTimerRef.current) clearInterval(typingTimerRef.current);
    if (outputTimerRef.current) clearInterval(outputTimerRef.current);

    setIsTyping(true);
    setTypedCommand('');
    setVisibleOutputs([]);
    
    let currentIdx = 0;
    // Capture the command snapshot to avoid mismatch when tab index changes
    const targetCmd = terminalCommands[selectedCmdIdx];
    const fullText = `$ ${targetCmd.command}`;
    
    // Smooth typing simulator
    typingTimerRef.current = setInterval(() => {
      if (currentIdx < fullText.length) {
        setTypedCommand(fullText.substring(0, currentIdx + 1));
        currentIdx++;
      } else {
        if (typingTimerRef.current) clearInterval(typingTimerRef.current);
        setIsTyping(false);
        
        // Output streaming simulation (displays lines sequentially at 45ms cadence)
        let outputLineIdx = 0;
        outputTimerRef.current = setInterval(() => {
          if (outputLineIdx < targetCmd.outputs.length) {
            setVisibleOutputs(prev => [...prev, targetCmd.outputs[outputLineIdx]]);
            outputLineIdx++;
          } else {
            if (outputTimerRef.current) clearInterval(outputTimerRef.current);
          }
        }, 45);
      }
    }, 12);
  };

  useEffect(() => {
    runCommandSim();
    return () => {
      if (typingTimerRef.current) clearInterval(typingTimerRef.current);
      if (outputTimerRef.current) clearInterval(outputTimerRef.current);
    };
  }, [selectedCmdIdx]);

  useEffect(() => {
    // Auto scroll terminal output
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [visibleOutputs, typedCommand]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(currentCmd.command);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
      
      {/* Command Selector Tab Panels */}
      <div className="lg:col-span-4 flex flex-row lg:flex-col gap-2 overflow-x-auto lg:overflow-x-visible pb-4 lg:pb-0 scrollbar-none">
        {terminalCommands.map((tc, idx) => {
          const isSelected = idx === selectedCmdIdx;
          return (
            <button
              key={tc.command}
              onClick={() => {
                setSelectedCmdIdx(idx);
              }}
              className={`flex-1 lg:flex-initial text-left px-4 py-3.5 rounded-xl border font-mono text-xs tracking-wide transition-all ${
                isSelected 
                  ? 'bg-[#FBF9F6] dark:bg-[#181513] border-[#C85A32] dark:border-[#E26838] text-[#C85A32] dark:text-[#E26838] shadow-sm font-semibold' 
                  : 'bg-[#F4EFEA] dark:bg-[#110F0E] border-[#EBE5DC] dark:border-[#2B2622] text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] hover:border-[#DFD9CE] dark:hover:border-[#36302B]'
              } cursor-pointer whitespace-nowrap lg:whitespace-normal`}
            >
              <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">
                PHASE 0{idx + 1}
              </div>
              <div className="font-semibold">{tc.label}</div>
              <div className="hidden lg:block text-[10px] text-slate-500 mt-1 font-mono">{tc.command.substring(0, 24)}...</div>
            </button>
          );
        })}
      </div>

      {/* Actual Terminal Screen */}
      <div className="lg:col-span-8 flex flex-col bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] rounded-xl overflow-hidden relative shadow-md transition-colors duration-300">
        
        {/* Terminal Header Bar */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#F4EFEA] dark:bg-[#110F0E] border-b border-[#EBE5DC] dark:border-[#2B2622]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
            <span className="w-2.5 h-2.5 rounded-full bg-green-400" />
            <span className="ml-2 text-xs font-mono text-slate-500 dark:text-[#A39A90]">zsh • .minerva/client</span>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={handleCopyCode}
              className="text-slate-505 hover:text-[#C85A32] transition-colors cursor-pointer text-slate-500"
              title="Copy Command"
            >
              {isCopied ? <ClipboardCheck size={14} className="text-[#C85A32]" /> : <Copy size={14} />}
            </button>
            <button 
              onClick={runCommandSim}
              className="text-slate-500 hover:text-[#C85A32] transition-colors cursor-pointer"
              title="Re-run terminal step"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        </div>

        {/* Terminal Text Screen */}
        <div 
          ref={terminalRef}
          className="flex-1 p-6 font-mono text-xs space-y-3 min-h-[300px] max-h-[360px] overflow-y-auto selection:bg-[#C85A32]/25 selection:text-[#C85A32] scrollbar-none"
        >
          {/* Historical trace */}
          <div className="text-slate-500 dark:text-[#A39A90]/70">
            Last logged session compiled: {new Date().toLocaleDateString()} via ContextDaemon
          </div>

          {/* Prompt line */}
          <div className="text-[#191919] dark:text-[#FBF9F6] font-medium flex items-center">
            <span>{typedCommand}</span>
            {isTyping && (
              <span className="w-1.5 h-3.5 bg-[#C85A32] dark:bg-[#E26838] ml-1 animate-pulse" />
            )}
          </div>

          {/* Generated Streaming Outputs */}
          {visibleOutputs.map((line, outIdx) => {
            if (!line || typeof line !== 'string') return null;
            // Determine output element colors based on formatting hints
            let textColor = 'text-[#545454]';
            let bgStyle = '';
            
            if (line.includes('[OK]')) {
              textColor = 'text-green-700 font-semibold';
            } else if (line.includes('[Match ')) {
              textColor = 'text-[#191919] dark:text-[#FBF9F6] font-semibold pl-2 border-l-2 border-[#C85A32] dark:border-[#E26838]';
              bgStyle = 'bg-[#F4EFEA] dark:bg-[#110F0E] py-1 rounded';
            } else if (line.includes('ID: ') || line.includes('GOAL-')) {
              textColor = 'text-[#C85A32] dark:text-[#E26838] font-semibold';
            } else if (line.includes('-75.42%')) {
              textColor = 'text-[#C85A32] dark:text-[#E26838] font-bold';
            } else if (line.startsWith('Initialize') || line.startsWith('Establishing') || line.startsWith('Querying')) {
              textColor = 'text-slate-500 dark:text-[#A39A90]/80';
            }
            
            return (
              <div 
                key={`line-${outIdx}`} 
                className={`leading-normal ${textColor} ${bgStyle} animate-fade-in`}
                style={{ animationDuration: '0.2s' }}
              >
                {line}
              </div>
            );
          })}

          {/* Final Prompt spacer */}
          {!isTyping && visibleOutputs.length === currentCmd.outputs.length && (
            <div className="flex items-center gap-1.5 text-slate-500 dark:text-[#A39A90]/80 pt-2 animate-fade-in">
              <span>$ minerva</span>
              <span className="w-1.5 h-3.5 bg-[#C85A32] dark:bg-[#E26838] animate-pulse" />
            </div>
          )}
        </div>

        {/* Terminal Footer status */}
        <div className="px-4 py-2 bg-[#F4EFEA] dark:bg-[#110F0E] border-t border-[#EBE5DC] dark:border-[#2B2622] flex items-center justify-between text-[10px] text-slate-500 dark:text-[#A39A90] font-mono">
          <span>SERVER DAEMON: LIVE</span>
          <span>COMPRESSION COEF: 0.28</span>
          <span>LATENCY: 4ms</span>
        </div>

      </div>

    </div>
  );
};
