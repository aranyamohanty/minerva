/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowRight, ArrowUpRight, Menu, X, Terminal, Cpu, Shield, 
  Sparkles, CheckCircle2, Zap, Network, ChevronRight, Bookmark, MoveRight,
  Sun, Moon
} from 'lucide-react';
import { HeroScene, QuantumComputerScene } from './components/QuantumScene';
import { ContextPipeline } from './components/ContextPipeline';
import { CognitiveArchitecture } from './components/CognitiveArchitecture';
import { MemoryGraph } from './components/MemoryGraph';
import { CommandLineTerminal } from './components/CommandLineTerminal';
import { IntegrationMap } from './components/IntegrationMap';
import { RoadmapOrbit } from './components/RoadmapOrbit';

// High-fidelity performance counter with ease-out cubic animation
const AnimatedCounter: React.FC<{ target: number; suffix: string; label: string; subLabel: string }> = ({ 
  target, suffix, label, subLabel 
}) => {
  const [value, setValue] = useState(0);
  const elementRef = useRef<HTMLDivElement>(null);
  const [hasTriggered, setHasTriggered] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !hasTriggered) {
          setHasTriggered(true);
        }
      },
      { threshold: 0.1 }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [hasTriggered]);

  useEffect(() => {
    if (!hasTriggered) return;

    let startTime: number | null = null;
    const duration = 1800; // 1.8 seconds

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      
      // Ease out cubic
      const easePercentage = 1 - Math.pow(1 - percentage, 3);
      setValue(Math.floor(easePercentage * target));

      if (percentage < 1) {
        requestAnimationFrame(animate);
      } else {
        setValue(target);
      }
    };

    requestAnimationFrame(animate);
  }, [hasTriggered, target]);

  return (
    <motion.div 
      ref={elementRef} 
      className="flex flex-col items-start p-8 bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] hover:border-[#C85A32]/35 dark:hover:border-[#E26838]/40 rounded-2xl transition-all duration-500 shadow-lg cursor-default"
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div className="font-mono text-5xl lg:text-7xl font-bold tracking-tight text-[#191919] dark:text-[#FBF9F6] mb-4 flex items-baseline">
        <span>{value}</span>
        <span className="text-[#C85A32] dark:text-[#E26838] font-semibold ml-0.5">{suffix}</span>
      </div>
      <h3 className="text-lg font-serif text-[#191919] dark:text-[#FBF9F6] font-medium mb-1">{label}</h3>
      <p className="text-xs font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-wider">{subLabel}</p>
    </motion.div>
  );
};

const App: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [hoveredNav, setHoveredNav] = useState<string | null>(null);
  const isDark = true;

  useEffect(() => {
    const root = document.documentElement;
    root.classList.add('dark');
    localStorage.setItem('context_theme', 'dark');
  }, []);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSmoothScroll = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    setMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      const headerOffset = 90;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className={`min-h-screen bg-[#F4EFEA] dark:bg-[#110F0E] text-[#191919] dark:text-[#FBF9F6] selection:bg-[#C85A32]/20 selection:text-[#C85A32] dark:selection:bg-[#E26838]/25 dark:selection:text-[#E26838] relative overflow-hidden transition-colors duration-300 ${isDark ? 'dark' : ''}`}>
      
      {/* Decorative architectural grid-mesh background */}
      <div className="absolute inset-0 grid-bg opacity-30 pointer-events-none z-0" />
      <div className="absolute inset-0 scanline opacity-5 pointer-events-none z-0" />

      {/* Drifting Ambient Glow Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[10%] left-[5%] w-[450px] h-[450px] rounded-full bg-[#C85A32]/8 dark:bg-[#E26838]/6 blur-[120px] animate-drift-1" />
        <div className="absolute bottom-[20%] right-[5%] w-[500px] h-[500px] rounded-full bg-[#8B7E74]/8 dark:bg-[#A39A90]/6 blur-[120px] animate-drift-2" />
      </div>

      {/* Navigation Header */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled 
          ? 'glass-ui-header py-4 shadow-sm' 
          : 'bg-transparent py-6'
      }`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          
          {/* Logo Brand */}
          <motion.div 
            className="flex items-center gap-3 cursor-pointer group" 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#C85A32] to-[#8B7E74] p-[1px] flex items-center justify-center shadow-sm transition-transform">
              <div className="w-full h-full rounded-[7px] bg-[#F4EFEA] dark:bg-[#110F0E] flex items-center justify-center font-mono font-black text-xs text-[#C85A32] dark:text-[#E26838] overflow-hidden">
                <span className="flex items-center">C
                  <motion.span 
                    className="inline-block origin-center ml-[1px] text-[10px]"
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
                    whileHover={{ rotate: 360, transition: { duration: 1 } }}
                  >⚙</motion.span>
                </span>
              </div>
            </div>
            <span className="font-mono font-black text-sm tracking-[0.25em] text-[#191919] dark:text-[#FBF9F6]">
              CONTEXT<span className="text-[#C85A32] dark:text-[#E26838]">OS</span>
            </span>
          </motion.div>
          
          {/* Main Desktop Links */}
          <div className="hidden md:flex items-center gap-6 text-xs font-mono tracking-wider text-[#545454] dark:text-[#A39A90]">
            {[
              { id: 'pipeline', label: 'Context Flow' },
              { id: 'architecture', label: 'Architecture' },
              { id: 'memory-graph', label: 'Memory Graph' },
              { id: 'cli', label: 'CLI' },
              { id: 'roadmap', label: 'Roadmap' },
            ].map((nav) => (
              <a
                key={nav.id}
                href={`#${nav.id}`}
                onClick={handleSmoothScroll(nav.id)}
                onMouseEnter={() => setHoveredNav(nav.id)}
                onMouseLeave={() => setHoveredNav(null)}
                className="relative py-1.5 px-3 hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors uppercase text-[11px] font-semibold tracking-wider"
              >
                {hoveredNav === nav.id && (
                  <motion.span
                    layoutId="hoverNavHighlight"
                    className="absolute inset-0 rounded-full bg-[#C85A32]/10 dark:bg-[#E26838]/10 -z-10"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ type: "spring", stiffness: 480, damping: 35 }}
                  />
                )}
                {nav.label}
              </a>
            ))}
            
            <motion.a 
              href="#cli" 
              onClick={handleSmoothScroll('cli')} 
              className="ml-2 px-5 py-2.5 bg-[#C85A32]/10 text-[#C85A32] dark:text-[#E26838] hover:bg-[#C85A32]/15 border border-[#C85A32]/20 rounded-full transition-all flex items-center gap-1.5 uppercase text-[10px] font-bold shadow-sm"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span>Initialize CLI</span>
              <ArrowRight size={11} className="transition-transform group-hover:translate-x-1" />
            </motion.a>
          </div>

          {/* Mobile hamburger trigger */}
          <div className="flex md:hidden items-center gap-2">
            <button 
              className="text-[#191919] dark:text-[#FBF9F6] p-2 border border-[#EBE5DC] dark:border-[#2B2622] rounded-lg bg-[#FBF9F6] dark:bg-[#181513] transition-colors shadow-sm" 
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Curtain Menu Drawer */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 bg-[#FBF9F6]/95 dark:bg-[#110F0E]/95 backdrop-blur-lg flex flex-col items-center justify-center gap-8 text-sm font-mono tracking-widest text-[#545454] dark:text-[#A39A90]"
          >
            <a href="#pipeline" onClick={handleSmoothScroll('pipeline')} className="text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors">CONTEXT FLOW</a>
            <a href="#architecture" onClick={handleSmoothScroll('architecture')} className="text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors">ARCHITECTURE</a>
            <a href="#memory-graph" onClick={handleSmoothScroll('memory-graph')} className="text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors">MEMORY GRAPH</a>
            <a href="#cli" onClick={handleSmoothScroll('cli')} className="text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors">CLI ENGINE</a>
            <a href="#roadmap" onClick={handleSmoothScroll('roadmap')} className="text-[#545454] dark:text-[#A39A90] hover:text-[#191919] dark:hover:text-[#FBF9F6] transition-colors">ROADMAP</a>
            
            <a 
              href="#cli" 
              onClick={handleSmoothScroll('cli')} 
              className="mt-4 px-6 py-3 bg-[#C85A32]/10 dark:bg-[#E26838]/10 border border-[#C85A32]/30 dark:border-[#E26838]/30 text-[#C85A32] dark:text-[#E26838] rounded-full shadow-md text-xs font-bold"
            >
              INITIALIZE MINERVA
            </a>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CINEMATIC HERO SECTION */}
      <header className="relative h-screen flex items-center justify-center overflow-hidden bg-[#F4EFEA] dark:bg-[#110F0E] transition-colors duration-300">
        {/* Living 3D Neural Scene Background */}
        <HeroScene />
        
        {/* Soft edge radial background masking */}
        <div className="absolute inset-0 z-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(251,249,246,0.3)_0%,rgba(244,239,234,0.8)_60%,#F4EFEA_100%)] dark:bg-[radial-gradient(circle_at_center,rgba(24,21,19,0.2)_0%,rgba(17,15,14,0.85)_60%,#110F0E_100%)]" />

        <motion.div 
          className="relative z-10 max-w-5xl mx-auto px-6 text-center"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: {},
            visible: {
              transition: {
                staggerChildren: 0.12
              }
            }
          }}
        >
          
          <motion.div 
            variants={{
              hidden: { opacity: 0, y: 15 },
              visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
            }}
            className="inline-flex items-center gap-2 mb-6 px-4 py-1.5 bg-[#FBF9F6]/75 dark:bg-[#181513]/75 border border-[#EBE5DC]/80 dark:border-[#2B2622]/80 text-[10px] tracking-[0.25em] text-[#545454] dark:text-[#A39A90] uppercase font-mono rounded-full font-bold shadow-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#C85A32] dark:bg-[#E26838] animate-ping" />
            <span>AI ORCHESTRATION LAYER • VERSION 1.2.0</span>
          </motion.div>
          
          <motion.h1 
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
            }}
            className="text-5xl md:text-7xl lg:text-8xl font-serif leading-[1.05] tracking-tight mb-8 text-[#191919] dark:text-[#F5EFEA]"
          >
            The Operating System <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#191919] via-[#C85A32] to-[#917966] dark:from-[#FBF9F6] dark:via-[#E26838] dark:to-[#A39A90] italic font-light font-sans">
              for AI Memory.
            </span>
          </motion.h1>
          
          <motion.p 
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
            }}
            className="max-w-2xl mx-auto text-sm md:text-base lg:text-lg text-[#545454] dark:text-[#A39A90] font-light leading-relaxed mb-12 font-mono"
          >
            Transform scattered workspace knowledge, databases, Slack channels, and code repositories into structured, dense intelligence that every major LLM can digest flawlessly.
          </motion.p>

        </motion.div>


      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-6 space-y-36 pb-36">

        {/* SECTION 2: WATCH CONTEXT BECOME INTELLIGENCE */}
        <motion.section 
          id="pipeline" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="mt-12 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] border border-[#C85A32]/20 dark:border-[#E26838]/20 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                STAGE MAPPING
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Watch Context Become Intelligence
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Raw markdown repositories and code channels are structured vectors, but they are full of noise. See how the Minerva compiler filters redundancy, extracts core tokens, and feeds pristine knowledge frames in 42ms.
            </p>
          </div>

          <ContextPipeline />
        </motion.section>

        {/* SECTION 3: COGNITIVE ARCHITECTURE */}
        <motion.section 
          id="architecture" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="-mt-10 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#8B7E74]/10 dark:bg-[#A39A90]/15 text-[#8B7E74] dark:text-[#A39A90] border border-[#8B7E74]/20 dark:border-[#2B2622]/30 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                CORE SCHEMATICS
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Cognitive Architecture
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              The orchestration lattice of Minerva coordinates indexing registries, re-ranking thresholds, vector manifolds and MCP proxies natively. Hover over sub-systems to examine logical dependencies.
            </p>
          </div>

          <CognitiveArchitecture />
        </motion.section>

        {/* SECTION 4: MEMORY GRAPH */}
        <motion.section 
          id="memory-graph" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="-mt-10 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] border border-[#C85A32]/20 dark:border-[#E26838]/20 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                NEURAL LEDGER
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Living Memory Graph
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Our file and meta relationship map behaves like a digital biological network. Direct edits, Slack queries, or task status changes compile structural synapses. Pull on nodes below to test gravity-bond reactions.
            </p>
          </div>

          <MemoryGraph />
        </motion.section>

        {/* SECTION 5: PERFORMANCE */}
        <motion.section 
          id="performance" 
          className="scroll-mt-24 relative overflow-hidden"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          {/* Subtle spinning background layout */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none z-0">
            <QuantumComputerScene />
          </div>

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            <div className="lg:col-span-4 space-y-6 bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg h-fit self-start">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] border border-[#C85A32]/20 dark:border-[#E26838]/20 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                  HARDWARE PERFORMANCE
                </span>
                <div className="w-8 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
              </div>
              <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] leading-tight font-medium">
                Operating System Boundaries
              </h2>
              <p className="text-sm text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
                Minerva bypasses standard cloud SaaS roundtrip lag. By anchoring memory graphs locally inside parallel SQLite vector caches, context is delivered without exposure to network overhead or leakage.
              </p>

              <div className="space-y-3 pt-4">
                <div className="flex items-center gap-3 text-xs font-mono text-[#545454] dark:text-[#A39A90] font-medium">
                  <CheckCircle2 size={14} className="text-[#C85A32] dark:text-[#E26838]" />
                  <span>Zero cold start delays</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono text-[#545454] dark:text-[#A39A90] font-medium">
                  <CheckCircle2 size={14} className="text-[#C85A32] dark:text-[#E26838]" />
                  <span>Full AES-256 local ledger encryption</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono text-[#545454] dark:text-[#A39A90] font-medium">
                  <CheckCircle2 size={14} className="text-[#C85A32] dark:text-[#E26838]" />
                  <span>Standard Model Context Protocol compliance</span>
                </div>
              </div>
            </div>

            {/* Symmetrical Giant typography grid */}
            <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6 relative">
              <AnimatedCounter target={95} suffix="%" label="Context Accuracy" subLabel="ZERO LLM HALUCINATIONS" />
              <AnimatedCounter target={75} suffix="%" label="Token Reduction" subLabel="OPTIMIZED PROMPT MASS" />
              <AnimatedCounter target={14} suffix="x" label="Faster Retrieval" subLabel="LOCAL HYBRID RETRIEVAL KERNEL" />
              <AnimatedCounter target={100} suffix="%" label="Local First" subLabel="ZERO THIRD-PARTY CLOUD STORAGE" />
            </div>

          </div>
        </motion.section>

        {/* SECTION 5.5: CAPABILITIES MATRIX (WHAT WE HAVE VS WHAT WE HAVEN'T) */}
        <motion.section 
          id="capabilities" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] border border-[#C85A32]/20 dark:border-[#E26838]/20 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                SYSTEM SHARDS
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Capabilities Matrix
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Compare the operational elements of Phase 1 (fully verified & running locally) against our future engineering roadmap objectives.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            
            {/* COLUMN 1: FULLY OPERATIONAL (WHAT WE HAVE) */}
            <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] hover:border-[#C85A32]/20 dark:hover:border-[#E26838]/20 rounded-2xl p-8 transition-all duration-300 shadow-md">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#EBE5DC] dark:border-[#2B2622]">
                <h3 className="text-xl font-serif font-bold text-[#191919] dark:text-[#FBF9F6] flex items-center gap-2">
                  <CheckCircle2 className="text-[#C85A32] dark:text-[#E26838] size-5" />
                  <span>Fully Operational (What We Have)</span>
                </h3>
                <span className="text-[10px] font-mono text-[#C85A32] dark:text-[#E26838] uppercase font-bold tracking-wider px-2 py-0.5 bg-[#C85A32]/10 rounded">Phase 1</span>
              </div>
              
              <motion.div 
                className="space-y-6"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                variants={{
                  hidden: {},
                  visible: {
                    transition: {
                      staggerChildren: 0.06
                    }
                  }
                }}
              >
                {[
                  {
                    title: 'Local Memory Ledger',
                    desc: 'SQLite-based relational database storing Goals, Constraints, Decisions, Tasks, Facts, and bilateral links with soft-deletes and audit logging.'
                  },
                  {
                    title: 'BGE-Small Embedding Engine',
                    desc: 'Local CPU-based vector generation utilizing cached BGE-small-en-v1.5 ONNX models with zero data egress.'
                  },
                  {
                    title: 'Hybrid Retrieval Kernel',
                    desc: 'FTS5 BM25 text query matching combined with semantic cosine similarity, exponential recency decay, and importance scaling.'
                  },
                  {
                    title: 'Relational Link Boosting',
                    desc: 'Enhanced search result scoring for entities related by explicitly established semantic database links.'
                  },
                  {
                    title: 'MMR Diversity Reranking',
                    desc: 'Maximal Marginal Relevance filtering to filter redundant search returns and diversify context payloads.'
                  },
                  {
                    title: 'Universal XML Prompt Compiler',
                    desc: 'Capacity-aware prompt assembly supporting system, project_context, relevant_history, conversation, and user blocks.'
                  },
                  {
                    title: 'Model Context Protocol (FastMCP)',
                    desc: '14 stdio-based named tools and 4 resources exposing active context layers directly to Cursor, Windsurf, and Claude Desktop.'
                  },
                  {
                    title: 'Command Line CRUD Utility',
                    desc: 'Hatchling-backed python CLI supporting re-indexing, linking, searching, and previewing with sub-4ms lazy-imports.'
                  }
                ].map((item, idx) => (
                  <motion.div 
                    key={idx} 
                    className="flex gap-4 items-start hover:translate-x-1.5 transition-transform duration-300"
                    variants={{
                      hidden: { opacity: 0, y: 8 },
                      visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 350, damping: 28 } }
                    }}
                  >
                    <div className="bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] p-1.5 rounded-lg text-xs font-mono shrink-0 font-bold">
                      0{idx + 1}
                    </div>
                    <div className="space-y-1">
                      <h4 className="text-sm font-semibold font-mono text-[#191919] dark:text-[#FBF9F6]">{item.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-[#A39A90] font-light leading-relaxed">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </div>

            {/* COLUMN 2: ENGINEERING HORIZON (WHAT WE HAVEN'T) */}
            <div className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] hover:border-[#8B7E74]/20 rounded-2xl p-8 transition-all duration-300 shadow-md">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#EBE5DC] dark:border-[#2B2622]">
                <h3 className="text-xl font-serif font-bold text-[#191919] dark:text-[#FBF9F6] flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full border border-dashed border-[#8B7E74]/60 dark:border-[#A39A90]/60 flex items-center justify-center font-mono text-[10px] text-[#8B7E74] dark:text-[#A39A90] font-black">?</span>
                  <span>Engineering Horizon (What We Haven't)</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-500 dark:text-[#A39A90] uppercase font-bold tracking-wider px-2 py-0.5 bg-slate-500/10 rounded">Phase 2+</span>
              </div>
              
              <motion.div 
                className="space-y-6"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                variants={{
                  hidden: {},
                  visible: {
                    transition: {
                      staggerChildren: 0.06
                    }
                  }
                }}
              >
                {[
                  {
                    title: 'Deep Editor Extension UI',
                    desc: 'Sidebar context visualization trees, inline code annotations, and direct prompt rewriters for Cursor and VS Code.'
                  },
                  {
                    title: 'Web Browser Context Injector',
                    desc: 'Browser extensions for Chrome/Firefox to automatically inject context layers into Claude.ai, ChatGPT, and Gemini Web UIs.'
                  },
                  {
                    title: 'P2P Encrypted Synchronizer',
                    desc: 'Decentralized local mesh networking to sync project memory files securely across developer nodes.'
                  },
                  {
                    title: 'Local Cross-Encoder Reranking',
                    desc: 'Heavy BERT-based re-ranking classifiers running locally to achieve ultra-high relevance scoring on long context windows.'
                  },
                  {
                    title: 'Cloud sync & Collaboration server',
                    desc: 'Optional team shared memory sync layer utilizing end-to-end user-held encryption keys.'
                  },
                  {
                    title: 'System Tray Dashboard GUI',
                    desc: 'Local native application (Tauri/Electron) to audit token savings history, manage scopes, and visualize memory nodes.'
                  }
                ].map((item, idx) => (
                  <motion.div 
                    key={idx} 
                    className="flex gap-4 items-start opacity-75 hover:opacity-100 hover:translate-x-1.5 transition-all duration-300"
                    variants={{
                      hidden: { opacity: 0, y: 8 },
                      visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 350, damping: 28 } }
                    }}
                  >
                    <div className="bg-[#8B7E74]/10 dark:bg-[#A39A90]/15 text-[#8B7E74] dark:text-[#A39A90] p-1.5 rounded-lg text-xs font-mono shrink-0 font-bold">
                      0{idx + 1}
                    </div>
                    <div className="space-y-1">
                      <h4 className="text-sm font-semibold font-mono text-[#191919] dark:text-[#FBF9F6]">{item.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-[#A39A90] font-light leading-relaxed">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </div>

          </div>
        </motion.section>

        {/* SECTION 6: CLI EXPERIENCE */}
        <motion.section 
          id="cli" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="-mt-10 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#8B7E74]/10 dark:bg-[#A39A90]/15 text-[#8B7E74] dark:text-[#A39A90] border border-[#8B7E74]/20 dark:border-[#2B2622]/30 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                DEVELOPER TOOLCHAIN
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Premium Developer Toolchain
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Minerva is built for production terminal environments. Test key commands using the interactive terminal dashboard to watch local directory registration models spin up.
            </p>
          </div>

          <CommandLineTerminal />
        </motion.section>

        {/* SECTION 7: INTEGRATIONS */}
        <motion.section 
          id="integrations" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="-mt-10 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#C85A32]/10 dark:bg-[#E26838]/10 text-[#C85A32] dark:text-[#E26838] border border-[#C85A32]/20 dark:border-[#E26838]/20 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                CONNECTED ECOSYSTEM
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Seamless Client Deliveries
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Whether writing code inside Cursor, organizing multi-model workflows in VS Code, or routing inference requests to Anthropic servers, Minerva provides standard local connections effortlessly.
            </p>
          </div>

          <IntegrationMap />
        </motion.section>

        {/* SECTION 8: ROADMAP */}
        <motion.section 
          id="roadmap" 
          className="scroll-mt-24"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="-mt-10 mb-12 max-w-3xl bg-[#181513] border border-[#2B2622] rounded-2xl p-6 md:p-8 relative z-10 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 bg-[#8B7E74]/10 dark:bg-[#A39A90]/15 text-[#8B7E74] dark:text-[#A39A90] border border-[#8B7E74]/20 dark:border-[#2B2622]/30 text-[9px] font-mono rounded font-bold uppercase tracking-widest">
                CHRONOLOGY HORIZON
              </span>
              <div className="w-12 h-[1px] bg-[#EBE5DC] dark:bg-[#2B2622]" />
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#191919] dark:text-[#F5EFEA] font-medium mb-4">
              Futuristic Roadmap Chronicle
            </h2>
            <p className="text-sm md:text-base text-[#545454] dark:text-[#A39A90] leading-relaxed font-mono">
              Follow our engineering horizon from raw SQLite storage structures to peer-to-peer sandboxed collaborative context synchronizers. Tap orbit locations to inspect targeted milestones.
            </p>
          </div>

          <RoadmapOrbit />
        </motion.section>

      </main>

      {/* FOOTER */}
      <footer className="bg-[#FBF9F6] dark:bg-[#181513] border-t border-[#EBE5DC] dark:border-[#2B2622] py-16 relative overflow-hidden z-10 text-[#545454] dark:text-[#A39A90] transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-12 gap-12 items-start">
          
          <div className="md:col-span-5 space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#C85A32] to-[#8B7E74] dark:from-[#E26838] p-[1px] flex items-center justify-center">
                <div className="w-full h-full rounded-[7px] bg-[#F4EFEA] dark:bg-[#110F0E] flex items-center justify-center font-mono font-black text-xs text-[#C85A32] dark:text-[#E26838]">
                  C⚙
                </div>
              </div>
              <span className="font-mono font-black text-sm tracking-[0.25em] text-[#191919] dark:text-[#FBF9F6]">
                CONTEXT<span className="text-[#C85A32] dark:text-[#E26838]">OS</span>
              </span>
            </div>

            <p className="text-xs text-slate-500 dark:text-[#A39A90] font-mono max-w-sm leading-relaxed">
              The operating system for AI memory. Designed locally. Completely sandboxed. Preserves privacy before sending vectors.
            </p>

            <div className="flex flex-wrap gap-3">
              <span className="px-2 py-1 bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] rounded text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest font-semibold">Local First</span>
              <span className="px-2 py-1 bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] rounded text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest font-semibold">Privacy Preserving</span>
              <span className="px-2 py-1 bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] rounded text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest font-semibold">Model Agnostic</span>
            </div>
          </div>

          <div className="md:col-span-4 grid grid-cols-2 gap-8 text-xs font-mono">
            <div className="space-y-4">
              <h4 className="text-[#191919] dark:text-[#FBF9F6] uppercase font-bold tracking-widest text-[10px]">Architecture</h4>
              <ul className="space-y-2.5">
                <li><a href="#pipeline" onClick={handleSmoothScroll('pipeline')} className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors">Pipeline Stream</a></li>
                <li><a href="#architecture" onClick={handleSmoothScroll('architecture')} className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors">Satellite Core</a></li>
                <li><a href="#memory-graph" onClick={handleSmoothScroll('memory-graph')} className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors">Brain graph</a></li>
                <li><a href="#cli" onClick={handleSmoothScroll('cli')} className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors">Interactive CLI</a></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="text-[#191919] dark:text-[#FBF9F6] uppercase font-bold tracking-widest text-[10px]">Resources</h4>
              <ul className="space-y-2.5">
                <li><a href="#" className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors flex items-center gap-1"><span>Documentation</span><ArrowUpRight size={10} /></a></li>
                <li><a href="#" className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors flex items-center gap-1"><span>GitHub Ledger</span><ArrowUpRight size={10} /></a></li>
                <li><a href="#" className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors flex items-center gap-1"><span>Model Protocol</span><ArrowUpRight size={10} /></a></li>
                <li><a href="#roadmap" onClick={handleSmoothScroll('roadmap')} className="hover:text-[#C85A32] dark:hover:text-[#E26838] transition-colors">Roadmap Horizon</a></li>
              </ul>
            </div>
          </div>

          <div className="md:col-span-3 space-y-4 font-mono text-xs">
            <h4 className="text-[#191919] dark:text-[#FBF9F6] uppercase font-bold tracking-widest text-[10px]">KERNEL PULSE</h4>
            <div className="bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] p-4 rounded-xl space-y-2.5 text-[#545454] dark:text-[#A39A90] shadow-sm">
              <div className="flex items-center justify-between text-[10px]">
                <span>CORE STATE:</span>
                <span className="text-emerald-700 dark:text-emerald-500 font-bold">READY</span>
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span>VECTOR SHARDS:</span>
                <span className="text-[#191919] dark:text-[#FBF9F6]">17,492 COGNITS</span>
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span>COMPRESSION RATE:</span>
                <span className="text-[#C85A32] dark:text-[#E26838] font-semibold">75.42% DECREASE</span>
              </div>
            </div>
          </div>

        </div>

        <div className="max-w-7xl mx-auto px-6 mt-16 pt-8 border-t border-[#EBE5DC] dark:border-[#2B2622] flex flex-col sm:flex-row justify-between items-center gap-4 text-xs font-mono text-[#8B7E74] dark:text-[#A39A90]">
          <span>&copy; {new Date().getFullYear()} Minerva Core. All rights reserved.</span>
          <div className="flex gap-6">
            <span>SECURE LOCAL HOST</span>
            <span>TCP PORT: 3000</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
