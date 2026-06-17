import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, Sparkles, Layers, Info, Calendar, Database, Eye } from 'lucide-react';
import { MemoryNode } from '../types';

export const MemoryGraph: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // High-fidelity node definitions representing the context of a software project
  const [nodes, setNodes] = useState<MemoryNode[]>([
    {
      id: 'g1',
      label: 'Goal: Thread-Safe Lock Engine',
      type: 'Goals',
      x: 350, y: 150,
      relevance: 0.98,
      size: 16,
      connections: ['d1', 'c1', 'o1'],
      metadata: {
        created: '2026-06-15',
        summary: 'Deliver a high-performance transactional lock scheduler handling parallel DB connections.',
        tokens: '120 tokens',
        hash: '0x9EFA98'
      }
    },
    {
      id: 'c1',
      label: 'Constraint: Limit Memory Budget to 64MB',
      type: 'Constraints',
      x: 200, y: 100,
      relevance: 0.95,
      size: 13,
      connections: ['g1', 'co1'],
      metadata: {
        created: '2026-06-12',
        summary: 'Enforce strict heap allocations on the local context index buffer to accommodate edge VMs.',
        tokens: '85 tokens',
        hash: '0x4F8CA2'
      }
    },
    {
      id: 'd1',
      label: 'Decision: SQLite structured memory store',
      type: 'Decisions',
      x: 500, y: 120,
      relevance: 0.97,
      size: 14,
      connections: ['g1', 'co1', 'cs1'],
      metadata: {
        created: '2026-06-14',
        summary: 'Use zero-config, fast, on-disk SQLite for structured memory store.',
        tokens: '142 tokens',
        hash: '0xFA39C2'
      }
    },
    {
      id: 'co1',
      label: 'Code: src/db/schema.ts',
      type: 'Code',
      x: 360, y: 280,
      relevance: 0.92,
      size: 14,
      connections: ['g1', 'c1', 'd1', 'cs1', 'r1'],
      metadata: {
        created: '2026-06-16',
        summary: 'Defines memory schema structures, vector lookup indexes, and index triggers.',
        tokens: '840 tokens',
        hash: '0xBD89A4'
      }
    },
    {
      id: 'cs1',
      label: 'Code: src/db/connection.ts',
      type: 'Code',
      x: 520, y: 260,
      relevance: 0.89,
      size: 11,
      connections: ['d1', 'co1', 'r2'],
      metadata: {
        created: '2026-06-16',
        summary: 'Manages parallel connection pools, lock queues, and transaction pipelines.',
        tokens: '412 tokens',
        hash: '0x1A2F99'
      }
    },
    {
      id: 'r1',
      label: 'Research: HNSW Graph Complexity paper',
      type: 'Research',
      x: 220, y: 240,
      relevance: 0.86,
      size: 11,
      connections: ['co1', 'o2'],
      metadata: {
        created: '2026-05-30',
        summary: 'Mathematical verification of nearest neighbor search complexity logarithmic limits.',
        tokens: '1,540 tokens',
        isResearch: true,
        hash: '0x92CFE1'
      }
    },
    {
      id: 'o1',
      label: 'Conversation: Lock thread chat logs',
      type: 'Conversations',
      x: 480, y: 30,
      relevance: 0.78,
      size: 10,
      connections: ['g1', 'd1'],
      metadata: {
        created: '2026-06-14',
        summary: 'Engineering discussion regarding deadlock edge cases under extreme concurrent loads.',
        tokens: '4,280 tokens',
        hash: '0xE9BC10'
      }
    },
    {
      id: 'o2',
      label: 'Doc: docs/architecture.md',
      type: 'Documents',
      x: 180, y: 320,
      relevance: 0.94,
      size: 12,
      connections: ['r1', 'co1'],
      metadata: {
        created: '2026-06-11',
        summary: 'Core design blueprint detailing modular subsystems and dependency structures.',
        tokens: '2,400 tokens',
        hash: '0x7C92EA'
      }
    },
    {
      id: 'r2',
      label: 'Task: Resolve multi-thread deadlocks',
      type: 'Tasks',
      x: 580, y: 340,
      relevance: 0.91,
      size: 12,
      connections: ['cs1', 'd1'],
      metadata: {
        created: '2026-06-16',
        summary: 'Audit of deadlock vulnerabilities during bulk concurrent inserts.',
        tokens: '190 tokens',
        hash: '0x32AEEB'
      }
    }
  ]);

  const [selectedNode, setSelectedNode] = useState<string>('g1');
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);
  const mousePos = useRef({ x: 0, y: 0 });
  const selectedNodeObj = nodes.find(n => n.id === selectedNode) || nodes[0];

  // Helper colors for different node categories (aligned to warm sand/terracotta/charcoal theme)
  const getNodeColor = (type: string, isLight = false) => {
    const isDarkMode = typeof document !== 'undefined' && document.documentElement.classList.contains('dark');
    if (isDarkMode) {
      switch (type) {
        case 'Goals': return isLight ? '#E56D3E' : 'rgba(229, 109, 62, 0.25)';
        case 'Constraints': return isLight ? '#CBB7A9' : 'rgba(203, 183, 169, 0.25)';
        case 'Decisions': return isLight ? '#F5EFEA' : 'rgba(245, 239, 234, 0.35)';
        case 'Code': return isLight ? '#B2A392' : 'rgba(178, 163, 146, 0.25)';
        case 'Documents': return isLight ? '#C5B9AC' : 'rgba(197, 185, 172, 0.25)';
        case 'Conversations': return isLight ? '#D0C7BD' : 'rgba(208, 199, 189, 0.25)';
        case 'Research': return isLight ? '#9F9082' : 'rgba(159, 144, 130, 0.25)';
        default: return isLight ? '#DDD4C9' : 'rgba(221, 212, 201, 0.25)';
      }
    } else {
      switch (type) {
        case 'Goals': return isLight ? '#C85A32' : 'rgba(200, 90, 50, 0.25)';
        case 'Constraints': return isLight ? '#917966' : 'rgba(145, 121, 102, 0.25)';
        case 'Decisions': return isLight ? '#191919' : 'rgba(25, 25, 25, 0.25)';
        case 'Code': return isLight ? '#776C5D' : 'rgba(119, 108, 93, 0.25)';
        case 'Documents': return isLight ? '#8B7E74' : 'rgba(139, 126, 116, 0.25)';
        case 'Conversations': return isLight ? '#A59D95' : 'rgba(165, 157, 149, 0.25)';
        case 'Research': return isLight ? '#5C5248' : 'rgba(92, 82, 72, 0.25)';
        default: return isLight ? '#8C8276' : 'rgba(140, 130, 118, 0.25)';
      }
    }
  };

  // Node physics simulation + visual drawing loop on Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let particles: Array<{ x: number; y: number; progress: number; speed: number; origin: string; target: string; color: string }> = [];

    // Scale canvas for high-DPI retina screens
    const handleResize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    handleResize();
    window.addEventListener('resize', handleResize);

    // Initialize node speeds
    nodes.forEach(n => {
      if (n.vx === undefined) n.vx = 0;
      if (n.vy === undefined) n.vy = 0;
    });

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width / window.devicePixelRatio;
      const height = canvas.height / window.devicePixelRatio;
      const isDarkMode = document.documentElement.classList.contains('dark');
      const coalClr = isDarkMode ? '#F5EFEA' : '#191919';

      // PHYSICS TICK
      // Repulsive forces between nodes (Coulomb's Law style)
      for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 185) {
            const force = (185 - dist) * 0.015;
            n1.vx! -= (dx / dist) * force;
            n1.vy! -= (dy / dist) * force;
            n2.vx! += (dx / dist) * force;
            n2.vy! += (dy / dist) * force;
          }
        }
      }

      // Attractive structural forces along connected edges (Hooke's Law style)
      nodes.forEach(n1 => {
        n1.connections.forEach(id => {
          const n2 = nodes.find(n => n.id === id);
          if (n2) {
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const naturalLength = 110;
            const force = (dist - naturalLength) * 0.003;
            n1.vx! += (dx / dist) * force;
            n1.vy! += (dy / dist) * force;
            n2.vx! -= (dx / dist) * force;
            n2.vy! -= (dy / dist) * force;
          }
        });
      });

      // Drag + Center Gravity Pull to keep clusters bound on screen
      nodes.forEach(n => {
        const cx = width / 2;
        const cy = height / 2;
        const dx = cx - n.x;
        const dy = cy - n.y;
        n.vx! += dx * 0.0005;
        n.vy! += dy * 0.0005;

        // Apply friction
        n.vx! *= 0.88;
        n.vy! *= 0.88;

        // If hovered/dragged by user, override position
        if (draggedNode === n.id) {
          n.x = mousePos.current.x;
          n.y = mousePos.current.y;
          n.vx = 0;
          n.vy = 0;
        } else {
          n.x += n.vx!;
          n.y += n.vy!;
        }

        // Keep inside canvas bounds
        n.x = Math.max(40, Math.min(width - 40, n.x));
        n.y = Math.max(40, Math.min(height - 40, n.y));
      });

      // DRAW EDGES (Connections)
      nodes.forEach(n1 => {
        n1.connections.forEach(id2 => {
          const n2 = nodes.find(n => n.id === id2);
          if (n2) {
            // Highlight connections if node is hovered or selected
            const isSelfHovered = hoveredNodeId === n1.id || hoveredNodeId === n2.id;
            const isSelfSelected = selectedNode === n1.id || selectedNode === n2.id;
            
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            
            if (isSelfHovered) {
              ctx.strokeStyle = 'rgba(200, 90, 50, 0.4)';
              ctx.lineWidth = 1.8;
            } else if (isSelfSelected) {
              ctx.strokeStyle = isDarkMode ? 'rgba(245, 239, 234, 0.4)' : 'rgba(25, 25, 25, 0.35)';
              ctx.lineWidth = 1.5;
            } else {
              ctx.strokeStyle = isDarkMode ? 'rgba(245, 239, 234, 0.08)' : 'rgba(25, 25, 25, 0.06)';
              ctx.lineWidth = 0.8;
            }
            ctx.stroke();

            // Edge particle generator (only generate on active paths)
            if ((isSelfHovered || isSelfSelected) && Math.random() < 0.02) {
              particles.push({
                x: n1.x,
                y: n1.y,
                progress: 0,
                speed: 0.015 + Math.random() * 0.01,
                origin: n1.id,
                target: n2.id,
                color: isSelfHovered ? '#C85A32' : coalClr
              });
            }
          }
        });
      });

      // UPDATE & DRAW PARTICLES along active links
      particles.forEach((p, idx) => {
        const originNode = nodes.find(n => n.id === p.origin);
        const targetNode = nodes.find(n => n.id === p.target);
        
        if (originNode && targetNode) {
          p.progress += p.speed;
          p.x = originNode.x + (targetNode.x - originNode.x) * p.progress;
          p.y = originNode.y + (targetNode.y - originNode.y) * p.progress;
          
          // Draw particle
          ctx.beginPath();
          ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
        }
      });
      particles = particles.filter(p => p.progress < 1.0);

      // DRAW NODES
      nodes.forEach(n => {
        const isHovered = hoveredNodeId === n.id;
        const isSelected = selectedNode === n.id;
        const radius = n.size;

        // Draw glowing halos
        if (isHovered || isSelected) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, radius + (isHovered ? 8 : 4), 0, Math.PI * 2);
          ctx.fillStyle = isHovered ? 'rgba(200, 90, 50, 0.12)' : (isDarkMode ? 'rgba(245, 239, 234, 0.08)' : 'rgba(25, 25, 25, 0.08)');
          ctx.fill();
        }

        // Draw main node body
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = getNodeColor(n.type, true);
        ctx.strokeStyle = isHovered ? coalClr : isSelected ? '#C85A32' : (isDarkMode ? 'rgba(245,239,234,0.15)' : 'rgba(25,25,25,0.2)');
        ctx.lineWidth = isHovered || isSelected ? 2 : 1;
        ctx.fill();
        ctx.stroke();

        // Draw inner dot
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = isDarkMode ? '#181513' : '#FBF9F6';
        ctx.fill();

        // Draw label text beside node (only dynamic or big ones) with an elegant high-contrast badge
        if (isHovered || isSelected || radius > 12) {
          const rawText = isHovered || isSelected ? n.label : n.label.split(':')[0];
          ctx.font = '500 10.5px monospace';
          const textMetrics = ctx.measureText(rawText);
          const bgWidth = textMetrics.width + 12;
          const bgHeight = 18;
          const bgX = n.x - bgWidth / 2;
          const bgY = n.y - radius - 20;

          // Draw pill background
          ctx.beginPath();
          if (ctx.roundRect) {
            ctx.roundRect(bgX, bgY, bgWidth, bgHeight, 4);
          } else {
            ctx.rect(bgX, bgY, bgWidth, bgHeight);
          }
          ctx.fillStyle = isDarkMode ? 'rgba(17, 15, 14, 0.88)' : 'rgba(251, 249, 246, 0.88)';
          ctx.strokeStyle = isHovered ? '#C85A32' : (isDarkMode ? 'rgba(245, 239, 234, 0.15)' : 'rgba(25, 25, 25, 0.15)');
          ctx.lineWidth = 1;
          ctx.fill();
          ctx.stroke();

          // Draw the text
          ctx.font = 'bold 10px monospace';
          ctx.fillStyle = isHovered ? '#E26838' : coalClr;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(rawText, n.x, bgY + bgHeight / 2 + 0.5);
        }
      });

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
    };
  }, [nodes, hoveredNodeId, selectedNode, draggedNode]);

  // Event handlers to interact with nodes via mouse/touch
  const getMouseCoord = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getMouseCoord(e);
    
    // Check if mouse clicked on a node
    const clickedNode = nodes.find(n => {
      const dx = n.x - x;
      const dy = n.y - y;
      return Math.sqrt(dx * dx + dy * dy) < n.size + 10;
    });

    if (clickedNode) {
      setDraggedNode(clickedNode.id);
      setSelectedNode(clickedNode.id);
      mousePos.current = { x, y };
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getMouseCoord(e);
    mousePos.current = { x, y };

    if (draggedNode) {
      setNodes(prev => prev.map(n => n.id === draggedNode ? { ...n, x, y } : n));
    } else {
      // Find hovered node
      const hovered = nodes.find(n => {
        const dx = n.x - x;
        const dy = n.y - y;
        return Math.sqrt(dx * dx + dy * dy) < n.size + 8;
      });
      setHoveredNodeId(hovered ? hovered.id : null);
    }
  };

  const handleMouseUp = () => {
    setDraggedNode(null);
  };

  return (
    <div id="memory-graph-pane" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
      
      {/* High-Performance Canvas Interactive Engine */}
      <div 
        ref={containerRef}
        className="lg:col-span-8 bg-[#FBF9F6] dark:bg-[#181513] border border-[#E6E1D8] dark:border-[#2B2622] rounded-2xl h-[420px] lg:h-[500px] relative overflow-hidden group/canvas cursor-grab active:cursor-grabbing shadow-sm transition-colors duration-300"
      >
        {/* Floating background grids and scan lines */}
        <div className="absolute inset-0 grid-bg opacity-15 dark:opacity-[0.06] pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #DFD9CE 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        <div className="absolute inset-0 scanline opacity-5 pointer-events-none" />

        {/* Action prompt floating instructions */}
        <div className="absolute top-4 left-4 bg-[#F4EFEA] dark:bg-[#110F0E] border border-[#EBE5DC] dark:border-[#2B2622] py-1.5 px-3 rounded-lg text-[10px] font-mono text-slate-500 dark:text-[#A39A90] tracking-wider flex items-center gap-2 pointer-events-none select-none transition-colors duration-300">
          <Eye size={11} className="text-[#C85A32] dark:text-[#E26838]" />
          <span>DRAG NODES TO ORGANIZE • HOVER OR CLICK TO DISCOVER</span>
        </div>

        {/* Actual rendering Canvas */}
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="w-full h-full block relative z-10"
        />
        
        {/* Visual category legends */}
        <div className="absolute bottom-4 left-4 z-20 flex flex-wrap gap-2 pointer-events-none max-w-sm md:max-w-none">
          {['Goals', 'Constraints', 'Decisions', 'Code', 'Documents', 'Research'].map(type => (
            <div key={type} className="flex items-center gap-1.5 bg-[#FBF9F6]/90 dark:bg-[#181513]/90 border border-[#EBE5DC] dark:border-[#2B2622] px-2 py-1 rounded text-[9px] font-mono transition-colors">
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: getNodeColor(type, true) }} />
              <span className="text-[#545454] dark:text-[#A39A90] capitalize">{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Structured Cognitive Metadata Panel (Interactive readout) */}
      <div className="lg:col-span-4 lg:h-[500px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedNode}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.25 }}
            className="bg-[#FBF9F6] dark:bg-[#181513] border border-[#EBE5DC] dark:border-[#2B2622] rounded-2xl p-5 lg:p-6 h-full flex flex-col justify-between relative overflow-y-auto paper-shadow-lg scrollbar-thin transition-colors duration-300"
          >
            {/* Visual colored marker edge based on selection node type */}
            <div 
              className="absolute left-0 top-0 bottom-0 w-[4px]" 
              style={{ backgroundColor: getNodeColor(selectedNodeObj.type, true) }}
            />

            <div>
              {/* Type tag wrapper */}
              <div className="flex items-center justify-between mb-4">
                <span 
                  className="px-2.5 py-1 border rounded-full text-[10px] font-mono font-bold tracking-wider uppercase"
                  style={{ 
                    borderColor: `${getNodeColor(selectedNodeObj.type, true)}33`, 
                    color: getNodeColor(selectedNodeObj.type, true),
                    backgroundColor: `${getNodeColor(selectedNodeObj.type, true)}11`
                  }}
                >
                  {selectedNodeObj.type}
                </span>

                <span className="text-[10px] font-mono text-slate-500 dark:text-[#A39A90] uppercase">
                  ID: {selectedNodeObj.metadata.hash}
                </span>
              </div>

              {/* Header Title */}
              <h3 className="text-xl font-serif text-[#191919] dark:text-[#FBF9F6] font-medium mb-3">
                {selectedNodeObj.label.split(': ').length > 1 ? selectedNodeObj.label.split(': ')[1] : selectedNodeObj.label}
              </h3>

              {/* Main Detail summary paragraph */}
              <p className="text-sm text-[#545454] dark:text-[#A39A90] leading-relaxed mb-6">
                {selectedNodeObj.metadata.summary}
              </p>

              {/* Meta metrics readouts */}
              <div className="grid grid-cols-2 gap-4 border-y border-[#EBE5DC] dark:border-[#2B2622] py-4 mb-6">
                <div>
                  <span className="block text-[10px] text-slate-500 dark:text-[#A39A90] font-mono uppercase tracking-widest mb-1 flex items-center gap-1.5 font-bold">
                    <Calendar size={11} /> RECORD DATE
                  </span>
                  <span className="text-xs font-mono text-[#191919] dark:text-[#FBF9F6] font-medium">
                    {selectedNodeObj.metadata.created}
                  </span>
                </div>
                <div>
                  <span className="block text-[10px] text-slate-500 dark:text-[#A39A90] font-mono uppercase tracking-widest mb-1 flex items-center gap-1.5 font-bold">
                    <Layers size={11} /> CHUNK MASS
                  </span>
                  <span className="text-xs font-mono text-[#191919] dark:text-[#FBF9F6] font-medium">
                    {selectedNodeObj.metadata.tokens}
                  </span>
                </div>
              </div>

              {/* Cognitive Weight Gauge bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-wider">
                  <span>COGNITIVE ACCURACY WEIGHT</span>
                  <span className="text-[#C85A32] dark:text-[#E26838] font-bold">{selectedNodeObj.relevance * 100}% Relevance</span>
                </div>
                <div className="h-1.5 bg-[#EBE5DC] dark:bg-[#2B2622] rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-[#191919] dark:from-[#FBF9F6] to-[#C85A32] dark:to-[#E26838] rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${selectedNodeObj.relevance * 100}%` }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  />
                </div>
              </div>
            </div>

            {/* Relations mapping display lists */}
            <div className="mt-8 pt-4 border-t border-[#EBE5DC] dark:border-[#2B2622]">
              <span className="block text-[9px] font-mono text-slate-500 dark:text-[#A39A90] uppercase tracking-widest font-black mb-3">
                BI-RELATIONAL NEURAL CONNECTIONS ({selectedNodeObj.connections.length})
              </span>
              
              <div className="flex flex-col gap-2">
                {selectedNodeObj.connections.map(id => {
                  const target = nodes.find(n => n.id === id);
                  if (!target) return null;
                  return (
                    <div 
                      key={id}
                      onClick={() => setSelectedNode(target.id)}
                      className="flex items-center justify-between p-2 bg-[#F4EFEA] dark:bg-[#110F0E]/80 hover:bg-[#EDE7DF] dark:hover:bg-[#27221E] border border-[#EBE5DC] dark:border-[#2B2622] rounded-lg text-xs font-mono text-[#545454] dark:text-[#A39A90] cursor-pointer hover:border-[#C85A32]/35 dark:hover:border-[#E26838]/50 transition-all group/item shadow-sm"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: getNodeColor(target.type, true) }} />
                        <span className="text-[11px] truncate">{target.label.split(': ').length > 1 ? target.label.split(': ')[1] : target.label}</span>
                      </div>
                      <span className="text-[9px] text-[#C85A32] group-hover/item:translate-x-1 transition-transform">→</span>
                    </div>
                  );
                })}
              </div>
            </div>

          </motion.div>
        </AnimatePresence>
      </div>

    </div>
  );
};
