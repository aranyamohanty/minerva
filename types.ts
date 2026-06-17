/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface MemoryNode {
  id: string;
  label: string;
  type: 'Goals' | 'Tasks' | 'Constraints' | 'Decisions' | 'Code' | 'Documents' | 'Conversations' | 'Research';
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  relevance: number;
  size: number;
  connections: string[];
  metadata: {
    created: string;
    summary: string;
    tokens?: string;
    accuracy?: string;
    parent?: string;
    hash?: string;
  };
}

export interface PipelineStep {
  id: string;
  name: string;
  description: string;
  metricLabel: string;
  metricValue: string;
  telemetry: string;
  status: 'idle' | 'processing' | 'complete';
}

export interface ArchitectureModule {
  id: string;
  name: string;
  category: string;
  description: string;
  x: number;
  y: number;
  angle: number;
  dependencies: string[];
  details: string;
}

export interface CommandHistory {
  command: string;
  content: string[];
  timestamp: string;
}

export interface RoadmapMilestone {
  title: string;
  completed: boolean;
  details: string;
}

export interface RoadmapPhase {
  phase: string;
  title: string;
  description: string;
  status: 'completed' | 'in-progress' | 'future';
  orbitalDistance: number;
  baseAngle: number;
  milestones: RoadmapMilestone[];
  progress: number;
}

export interface IntegrationEntity {
  id: string;
  name: string;
  iconName: string;
  color: string;
  angle: number;
  radius: number;
}
