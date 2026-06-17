import React from 'react';
import { motion } from 'framer-motion';

// Render a gorgeous high-fidelity vector schematic mesh background
export const HeroScene: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 opacity-40 dark:opacity-15 pointer-events-none select-none overflow-hidden transition-opacity duration-300" style={{ filter: 'blur(8px)' }}>
      <svg className="w-full h-full min-h-screen" xmlns="http://www.w3.org/2000/svg">
        <defs>
          {/* Subtle grid pattern */}
          <pattern id="grid-mesh" width="48" height="48" patternUnits="userSpaceOnUse">
            <path d="M 48 0 L 0 0 0 48" fill="none" stroke="#DFD9CE" strokeWidth="0.8" opacity="0.45" />
          </pattern>
          {/* Accent-tinted subtle dots */}
          <pattern id="dot-mesh" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="1.5" cy="1.5" r="1" fill="#C85A32" opacity="0.12" />
          </pattern>
          {/* Gentle ambient lighting spotlight */}
          <radialGradient id="mesh-glow" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stopColor="#C85A32" stopOpacity="0.06" />
            <stop offset="60%" stopColor="#8B7E74" stopOpacity="0.02" />
            <stop offset="100%" stopColor="#F4EFEA" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* 1. Underlying patterns */}
        <rect width="100%" height="100%" fill="url(#grid-mesh)" />
        <rect width="100%" height="100%" fill="url(#dot-mesh)" />
        <rect width="100%" height="100%" fill="url(#mesh-glow)" />

        {/* 2. Concentric geometric math coordinate mesh */}
        <motion.g 
          transform="translate(480, 280)" 
          className="opacity-90"
          animate={{ rotate: -360 }}
          transition={{ repeat: Infinity, duration: 180, ease: "linear" }}
          style={{ transformOrigin: "480px 280px" }}
        >
          <circle cx="0" cy="0" r="160" fill="none" stroke="#E6E1D8" strokeWidth="1.2" strokeDasharray="3,3" />
          <circle cx="0" cy="0" r="280" fill="none" stroke="#E6E1D8" strokeWidth="1" />
          <circle cx="0" cy="0" r="420" fill="none" stroke="#C85A32" strokeWidth="0.8" strokeDasharray="6,8" opacity="0.15" />
          
          <line x1="-500" y1="0" x2="500" y2="0" stroke="#E6E1D8" strokeWidth="1" opacity="0.35" />
          <line x1="0" y1="-500" x2="0" y2="500" stroke="#E6E1D8" strokeWidth="1" opacity="0.35" />
        </motion.g>

        {/* 3. Neural topology context lattice */}
        <g stroke="#C85A32" strokeWidth="1" opacity="0.22" strokeLinecap="round">
          {/* Primary network branches */}
          <line x1="12%" y1="18%" x2="32%" y2="22%" />
          <line x1="32%" y1="22%" x2="48%" y2="12%" />
          <line x1="48%" y1="12%" x2="68%" y2="28%" />
          <line x1="68%" y1="28%" x2="88%" y2="14%" />
          
          <line x1="12%" y1="18%" x2="22%" y2="42%" />
          <line x1="22%" y1="42%" x2="42%" y2="52%" />
          <line x1="32%" y1="22%" x2="42%" y2="52%" />
          <line x1="48%" y1="12%" x2="54%" y2="38%" />
          
          <line x1="54%" y1="38%" x2="68%" y2="28%" />
          <line x1="54%" y1="38%" x2="64%" y2="60%" />
          <line x1="68%" y1="28%" x2="82%" y2="46%" />
          <line x1="88%" y1="14%" x2="82%" y2="46%" />

          <line x1="22%" y1="42%" x2="28%" y2="70%" />
          <line x1="42%" y1="52%" x2="28%" y2="70%" />
          <line x1="42%" y1="52%" x2="64%" y2="60%" />
          <line x1="64%" y1="60%" x2="58%" y2="82%" />
          <line x1="82%" y1="46%" x2="78%" y2="76%" />
          
          {/* Subtle cross-connection loops */}
          <line x1="32%" y1="22%" x2="54%" y2="38%" strokeDasharray="2,4" />
          <line x1="42%" y1="52%" x2="58%" y2="82%" strokeDasharray="2,4" stroke="#8B7E74" />
        </g>

        {/* 3.5 Animated signal flow pulses travelling down branches */}
        <g stroke="#C85A32" strokeWidth="1.2" opacity="0.45" strokeLinecap="round" className="animate-signal-flow">
          <line x1="12%" y1="18%" x2="32%" y2="22%" />
          <line x1="48%" y1="12%" x2="68%" y2="28%" />
          <line x1="22%" y1="42%" x2="42%" y2="52%" />
          <line x1="54%" y1="38%" x2="64%" y2="60%" />
          <line x1="82%" y1="46%" x2="78%" y2="76%" />
        </g>

        {/* 4. Highlighted vertex synapses */}
        <g fill="#FBF9F6" stroke="#C85A32" strokeWidth="1.8" opacity="0.8">
          <motion.circle cx="12%" cy="18%" r="4.5" fill="#C85A32" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }} />
          <motion.circle cx="32%" cy="22%" r="4" animate={{ y: [0, 3, 0] }} transition={{ repeat: Infinity, duration: 5, ease: "easeInOut", delay: 0.5 }} />
          <motion.circle cx="48%" cy="12%" r="5.5" fill="#C85A32" animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 6, ease: "easeInOut", delay: 0.2 }} />
          <motion.circle cx="68%" cy="28%" r="4" animate={{ y: [0, 4, 0] }} transition={{ repeat: Infinity, duration: 4.5, ease: "easeInOut", delay: 0.8 }} />
          <motion.circle cx="88%" cy="14%" r="4.5" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 5.5, ease: "easeInOut", delay: 0.4 }} />
          
          <motion.circle cx="22%" cy="42%" r="4" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 4.2, ease: "easeInOut", delay: 0.3 }} />
          <motion.circle cx="42%" cy="52%" r="5" fill="#8B7E74" stroke="#8B7E74" animate={{ y: [0, 3, 0] }} transition={{ repeat: Infinity, duration: 5.2, ease: "easeInOut", delay: 0.7 }} />
          <motion.circle cx="54%" cy="38%" r="4" animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 4.8, ease: "easeInOut", delay: 0.1 }} />
          <motion.circle cx="82%" cy="46%" r="5" animate={{ y: [0, 4, 0] }} transition={{ repeat: Infinity, duration: 6.2, ease: "easeInOut", delay: 0.9 }} />

          <motion.circle cx="28%" cy="70%" r="4" fill="#C85A32" animate={{ y: [0, -2, 0] }} transition={{ repeat: Infinity, duration: 4.1, ease: "easeInOut", delay: 0.6 }} />
          <motion.circle cx="64%" cy="60%" r="5" animate={{ y: [0, 3, 0] }} transition={{ repeat: Infinity, duration: 5.1, ease: "easeInOut", delay: 0.2 }} />
          <motion.circle cx="58%" cy="82%" r="4" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 5.8, ease: "easeInOut", delay: 0.8 }} />
          <motion.circle cx="78%" cy="76%" r="4" fill="#8B7E74" stroke="#8B7E74" animate={{ y: [0, 2, 0] }} transition={{ repeat: Infinity, duration: 4.6, ease: "easeInOut", delay: 0.5 }} />
        </g>

        {/* Blueprint-style annotation ticks */}
        <g fill="#8B7E74" fontFamily="monospace" fontSize="8" opacity="0.3">
          <text x="3%" y="95%">SYS_MESH_LATITUDE: 42.18</text>
          <text x="3%" y="97%">GRID_ALIGNED: TRUE</text>
        </g>
      </svg>
    </div>
  );
};

export const QuantumComputerScene: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 opacity-15 dark:opacity-[0.06] pointer-events-none select-none overflow-hidden transition-opacity duration-300" style={{ filter: 'blur(5px)' }}>
      <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="mini-grid" width="24" height="24" patternUnits="userSpaceOnUse">
            <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#EBE5DC" strokeWidth="0.8" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#mini-grid)" />
        <g stroke="#C85A32" strokeWidth="0.8" opacity="0.4" strokeDasharray="3,3">
          <line x1="0%" y1="50%" x2="100%" y2="50%" />
          <line x1="50%" y1="0%" x2="50%" y2="100%" />
        </g>
      </svg>
    </div>
  );
};


