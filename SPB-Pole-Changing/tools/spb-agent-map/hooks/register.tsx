import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { AgentNode, Handoff, MapEvent, Role, Team } from '../types'

// The project this map watches; the mod only writes its status file there.
const PROJECT = 'C:/Github/KTH/SPB-Pole-Changing'
const STATUS_FILE = `${PROJECT}/board/agent_status.json`
const PANE = 'spb-agent-map'
const TITLE = 'SPB agent map'
const HANDOFF_GLOW_MS = 30_000

const ROLES: Role[] = [
  'leader',
  'lit-scout',
  'analyst',
  'simulator',
  'figure-maker',
  'writer',
  'gap-critic',
]
const SPECIALISTS = new Set<string>(ROLES.slice(1))

// Folder each role owns (CLAUDE.md handoff protocol).
const OWNER_BY_FOLDER: [string, Role][] = [
  ['/01_literature/', 'lit-scout'],
  ['/02_analytics/', 'analyst'],
  ['/03_simulation/', 'simulator'],
  ['/04_figures/', 'figure-maker'],
  ['/05_reports/', 'writer'],
  ['/06_reviews/', 'gap-critic'],
  ['/board/', 'leader'],
]

const COLOR: Record<Role, string> = {
  leader: '#d97757',
  'lit-scout': '#0e9bb5',
  analyst: '#e08a00',
  simulator: '#2f9e44',
  'figure-maker': '#8a5cd6',
  writer: '#3b6fd6',
  'gap-critic': '#d6336c',
}

// Node centres in the 440 x 340 drawing.
const POS: Record<Role, [number, number]> = {
  leader: [150, 46],
  'gap-critic': [330, 46],
  'lit-scout': [78, 150],
  analyst: [220, 170],
  simulator: [362, 150],
  'figure-maker': [120, 288],
  writer: [320, 288],
}

// The planned flow of work; drawn faint, lit when a handoff happens on it.
const PLANNED: [Role, Role][] = [
  ['leader', 'lit-scout'],
  ['leader', 'analyst'],
  ['leader', 'simulator'],
  ['lit-scout', 'analyst'],
  ['analyst', 'simulator'],
  ['analyst', 'figure-maker'],
  ['simulator', 'figure-maker'],
  ['lit-scout', 'writer'],
  ['figure-maker', 'writer'],
  ['lit-scout', 'gap-critic'],
  ['analyst', 'gap-critic'],
  ['gap-critic', 'leader'],
]

const idleNode = (): AgentNode => ({
  status: 'idle',
  task: '',
  lastTool: '',
  runs: 0,
  updatedAt: 0,
})

const emptyTeam = (): Team => ({
  nodes: Object.fromEntries(ROLES.map(r => [r, idleNode()])) as Record<
    Role,
    AgentNode
  >,
  agentIds: {},
  handoffs: [],
  events: [],
})

const team = atom({ plugin: 'spb-agent-map', key: 'team' } as const, emptyTeam(), {
  shape: 'team-2',
})
const now = atom({ plugin: 'spb-agent-map', key: 'now' } as const, 0, {
  shape: 'now-1',
})

const ownerOf = (path: string): Role | undefined => {
  const p = path.replace(/\\/g, '/')
  if (!p.toLowerCase().includes('spb-pole-changing')) return undefined
  return OWNER_BY_FOLDER.find(([dir]) => p.includes(dir))?.[1]
}

const baseName = (path: string) => path.replace(/\\/g, '/').split('/').pop() ?? path

const clip = (s: string, n: number) => (s.length > n ? `${s.slice(0, n - 1)}…` : s)

const xml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

// One readable line for a tool call, from whatever arguments it has.
const summarize = (tool: string, args: Record<string, unknown>) => {
  const str = (k: string) => (typeof args[k] === 'string' ? (args[k] as string) : '')
  const target =
    (str('file_path') && baseName(str('file_path'))) ||
    str('description') ||
    str('query') ||
    str('url') ||
    str('pattern') ||
    str('command')
  return clip(target ? `${tool}: ${target}` : tool, 48)
}

const withEvent = (t: Team, at: number, who: Role, text: string): Team => ({
  ...t,
  events: [...t.events, { at, who, text } satisfies MapEvent].slice(-40),
})

const withHandoff = (t: Team, h: Handoff): Team => {
  const last = [...t.handoffs].reverse().find(x => x.from === h.from && x.to === h.to)
  if (last && h.at - last.at < 5_000) return t
  return withEvent(
    { ...t, handoffs: [...t.handoffs, h].slice(-30) },
    h.at,
    h.to,
    `${h.from} → ${h.to}: ${h.what}`,
  )
}

const setNode = (t: Team, role: Role, patch: Partial<AgentNode>, at: number): Team => ({
  ...t,
  nodes: { ...t.nodes, [role]: { ...t.nodes[role], ...patch, updatedAt: at } },
})

// Mirror of the map for the leader and for later sessions.
async function persist($: EngineInterface) {
  const t = await read($, team)
  await $.fs.write(
    STATUS_FILE,
    JSON.stringify({ nodes: t.nodes, recent: t.events.slice(-15) }, null, 2),
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'agent-map',
      description: 'Open the live SPB agent map pane',
    })
    void $.ui.open({ id: PANE, title: TITLE })

    // Poll the engine's agent list: it is the only place an agent's end shows.
    $.clock.every(2_000, async () => {
      const at = await $.clock.now()
      const list = await $.agent.list()
      let changed = false
      await update($, team, t => {
        let acc = t
        const running = new Set<Role>()
        for (const a of list) {
          const role = t.agentIds[a.id]
          if (!role) continue
          if (a.status === 'running' || a.status === 'pending' || a.status === 'waiting') {
            running.add(role)
          }
        }
        for (const a of list) {
          const role = t.agentIds[a.id]
          if (!role || running.has(role)) continue
          const status =
            a.status === 'completed' || a.status === 'idle'
              ? 'done'
              : a.status === 'failed' || a.status === 'killed'
                ? 'failed'
                : undefined
          if (status && acc.nodes[role].status === 'running') {
            acc = withEvent(setNode(acc, role, { status }, at), at, role, `${status}: ${acc.nodes[role].task}`)
            acc = withHandoff(acc, { from: role, to: 'leader', at, what: 'report' })
            changed = true
          }
        }
        return acc
      })
      await update($, now, () => at)
      if (changed) await persist($)
    })

    return next(e)
  })

  on('command.run', { command: 'agent-map' }, async $ => {
    await $.ui.open({ id: PANE, title: TITLE })
    return { text: 'Agent map opened.' }
  })

  on('turn.start', async ($, e, next) => {
    const at = await $.clock.now()
    await update($, team, t => setNode(t, 'leader', { status: 'running' }, at))
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const at = await $.clock.now()
    await update($, team, t => setNode(t, 'leader', { status: 'idle' }, at))
    await persist($)
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const started = await next(e)
    if (!SPECIALISTS.has(e.subagentType) || !('agentId' in started) || !started.agentId) {
      return started
    }
    const role = e.subagentType as Role
    const id = started.agentId
    const at = await $.clock.now()
    await update($, team, t => {
      const n = t.nodes[role]
      const t2 = setNode(
        { ...t, agentIds: { ...t.agentIds, [id]: role } },
        role,
        { status: 'running', task: clip(e.description, 40), lastTool: '', runs: n.runs + 1 },
        at,
      )
      return withHandoff(t2, { from: 'leader', to: role, at, what: clip(e.description, 40) })
    })
    await persist($)
    return started
  })

  on('tool.call', async ($, e, next) => {
    const at = await $.clock.now()
    const t0 = await read($, team)
    const who: Role | undefined = e.agentId ? t0.agentIds[e.agentId] : 'leader'
    if (who && e.tool !== 'Agent') {
      const args = e as unknown as Record<string, unknown>
      const path = typeof args.file_path === 'string' ? args.file_path : ''
      const owner = path ? ownerOf(path) : undefined
      await update($, team, t => {
        let t2 = setNode(t, who, { lastTool: summarize(e.tool, args) }, at)
        // Reading another agent's output is the handoff the blackboard makes.
        if (owner && owner !== who && e.tool === 'Read') {
          t2 = withHandoff(t2, { from: owner, to: who, at, what: baseName(path) })
        }
        return t2
      })
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const t = await read($, team)
    const at = (await read($, now)) || Date.now()
    const recent = t.handoffs.filter(h => at - h.at < HANDOFF_GLOW_MS)

    const lines = (
      <Box flexDirection="column">
        {t.events.length === 0 && <Text dimColor>No agent activity yet.</Text>}
        {t.events.slice(-8).map(ev => (
          <Text dimColor>
            {new Date(ev.at).toLocaleTimeString().slice(0, 8)} {ev.text}
          </Text>
        ))}
      </Box>
    )

    if (e.surface === 'terminal') {
      return (
        <Box flexDirection="column">
          {ROLES.map(r => {
            const n = t.nodes[r]
            return (
              <Text bold={n.status === 'running'} dimColor={n.status !== 'running'}>
                {n.status === 'running' ? '●' : n.status === 'failed' ? '✕' : '○'} {r}
                {n.task ? ` — ${n.task}` : ''}
                {n.status === 'running' && n.lastTool ? ` · ${n.lastTool}` : ''}
              </Text>
            )
          })}
          {lines}
        </Box>
      )
    }

    const { Svg } = $.ui.resolve(e)
    return (
      <Box flexDirection="column">
        <Svg source={drawMap(t, recent)} alt={altText(t)} isInteractive />
        {lines}
      </Box>
    )
  })
}

const altText = (t: Team) =>
  ROLES.map(r => `${r}: ${t.nodes[r].status}${t.nodes[r].task ? ` (${t.nodes[r].task})` : ''}`).join('; ')

const drawMap = (t: Team, recent: Handoff[]) => {
  const W = 440
  const H = 340
  const NW = 128
  const NH = 58
  const lit = new Map(recent.map(h => [`${h.from}>${h.to}`, h]))

  const edge = (from: Role, to: Role, isPlanned: boolean) => {
    const [x1, y1] = POS[from]
    const [x2, y2] = POS[to]
    const h = lit.get(`${from}>${to}`)
    if (!h && !isPlanned) return ''
    if (!h) {
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#8884" stroke-width="1.2" stroke-dasharray="3 4"/>`
    }
    const c = COLOR[from]
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="2.6" stroke-dasharray="8 6" marker-end="url(#arrow)">
      <animate attributeName="stroke-dashoffset" from="28" to="0" dur="0.8s" repeatCount="indefinite"/>
      <title>${xml(`${from} → ${to}: ${h.what}`)}</title></line>`
  }

  const plannedKeys = new Set(PLANNED.map(([a, b]) => `${a}>${b}`))
  const edges = [
    ...PLANNED.map(([a, b]) => edge(a, b, true)),
    ...recent
      .filter(h => !plannedKeys.has(`${h.from}>${h.to}`))
      .map(h => edge(h.from, h.to, false)),
  ].join('')

  const nodes = ROLES.map(r => {
    const n = t.nodes[r]
    const [cx, cy] = POS[r]
    const x = cx - NW / 2
    const y = cy - NH / 2
    const c = COLOR[r]
    const isOn = n.status === 'running'
    const badge =
      n.status === 'running' ? 'working' : n.status === 'done' ? 'done' : n.status === 'failed' ? 'failed' : 'idle'
    const pulse = isOn
      ? `<rect x="${x - 4}" y="${y - 4}" width="${NW + 8}" height="${NH + 8}" rx="13" fill="none" stroke="${c}" stroke-width="2">
           <animate attributeName="opacity" values="0.9;0.15;0.9" dur="1.4s" repeatCount="indefinite"/></rect>`
      : ''
    return `<g>${pulse}
      <rect x="${x}" y="${y}" width="${NW}" height="${NH}" rx="10" fill="${isOn ? c : 'Canvas'}" fill-opacity="${isOn ? 0.16 : 1}" stroke="${c}" stroke-width="${isOn ? 2.2 : 1.2}"/>
      <text x="${cx}" y="${y + 16}" text-anchor="middle" font-size="12" font-weight="600" fill="${c}">${r}</text>
      <text x="${cx}" y="${y + 31}" text-anchor="middle" font-size="9.5" fill="CanvasText" opacity="0.85">${xml(clip(n.task || badge, 24))}</text>
      <text x="${cx}" y="${y + 45}" text-anchor="middle" font-size="8.5" fill="CanvasText" opacity="0.6">${xml(isOn ? clip(n.lastTool, 26) : `${badge}${n.runs ? ` · ${n.runs} run${n.runs > 1 ? 's' : ''}` : ''}`)}</text>
      <title>${xml(`${r} — ${badge}\n${n.task}\n${n.lastTool}`)}</title></g>`
  }).join('')

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="system-ui, sans-serif">
    <style>:root{color-scheme:light dark}</style>
    <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/></marker></defs>
    ${edges}${nodes}</svg>`
}
