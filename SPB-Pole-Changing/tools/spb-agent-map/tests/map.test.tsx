import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'spb-agent-map',
  component: 'Pane',
  requestId: 'spb-agent-map',
  props: {
    title: 'SPB agent map',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

test('a spawned analyst lights up and reading lit-scout output is a handoff', async ($, on) => {
  on('command.register', () => ({ value: { command: 'agent-map' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('clock.every', () => ({ value: { cancel: () => {} } }))
  on('clock.now', () => ({ value: 1_000 }))
  on('fs.write', () => ({ value: undefined }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('agent.spawn', () => ({ model: 'opus', agentId: 'a1' }))
  on('tool.call', () => ({ result: {} }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.agent.spawn({
    prompt: 'envelope',
    description: 'Torque-speed envelope',
    subagentType: 'analyst',
  })
  await $.tool.call({
    tool: 'Read',
    file_path: 'C:/Github/KTH/SPB-Pole-Changing/01_literature/gap_matrix.md',
    agentId: 'a1',
  } as never)

  const term = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const row = await term.find({ type: 'Text', text: /analyst/ })
  expect(row?.text).toContain('● analyst — Torque-speed envelope')
  const ev = await term.find({ type: 'Text', text: /lit-scout → analyst/ })
  expect(ev?.text).toContain('gap_matrix.md')
  await term.unmount()

  const desk = await $.ui.mount({ ...PANE, surface: 'desktop' })
  const svg = await desk.find({ type: 'Svg' })
  expect(String(svg?.props?.alt)).toContain('analyst: running')
  await desk.unmount()
})
