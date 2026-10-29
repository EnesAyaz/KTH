export type Role =
  | 'leader'
  | 'lit-scout'
  | 'analyst'
  | 'simulator'
  | 'figure-maker'
  | 'writer'
  | 'gap-critic'

export type NodeStatus = 'idle' | 'running' | 'done' | 'failed'

export type AgentNode = {
  status: NodeStatus
  task: string
  lastTool: string
  runs: number
  updatedAt: number
}

export type Handoff = { from: Role; to: Role; at: number; what: string }

export type MapEvent = { at: number; who: Role; text: string }

export type Team = {
  nodes: Record<Role, AgentNode>
  agentIds: Record<string, Role>
  handoffs: Handoff[]
  events: MapEvent[]
}

declare module 'claude-code' {
  interface PluginState {
    'spb-agent-map': { team: Shaped<Team>; now: Shaped<number> }
  }
}
