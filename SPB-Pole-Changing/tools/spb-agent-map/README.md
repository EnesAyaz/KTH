# spb-agent-map

Claude Code mod: a live pane beside the chat that maps the SPB-Pole-Changing agent
team. Each agent (leader, lit-scout, analyst, simulator, figure-maker, writer) is a
node that pulses while it works and shows its task and current tool call. An arrow
lights up when the leader dispatches an agent, when an agent reads a file from
another agent's folder (the blackboard handoff), and when an agent reports back.
State is mirrored to `board/agent_status.json`.

Load it in a session:
- Desktop app: ask Claude to load this mod (plugin-authoring), or set the user
  environment variable `CLAUDE_CODE_PLUGIN_DIRS` to this folder and restart the app.
- Terminal: `claude --plugin-dir tools/spb-agent-map`

`/agent-map` reopens the pane. Test: `claude plugin test tools/spb-agent-map`.
