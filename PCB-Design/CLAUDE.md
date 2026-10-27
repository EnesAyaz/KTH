# PCB-Design: design loop with a leader and specialist agents

The main session is the **leader**. Enes talks only to the leader. The specialists are defined in
`.claude/agents/` (pcb-layout, fab-release, sim-analyst, paper-writer, slides-builder, design-reviewer).

## Leader protocol (one loop round per comment from Enes)

1. **Plan.** Turn the comment into tasks, one per specialist, each with a clear "done" check. Say the plan in two or
   three lines before starting agents.
2. **Delegate.** Start the agents. Parallel only where they do not write the same files:
   - safe together: paper-writer + slides-builder + design-reviewer; sim-analyst + paper-writer (existing results)
   - in order: pcb-layout -> fab-release -> paper-writer / slides-builder (a board change makes fab files, renders
     and numbers stale); trial layouts in a git worktree
3. **Relay.** Agents do not talk to each other; the leader passes results on (e.g. new Q3D numbers from sim-analyst
   to paper-writer, a review finding to pcb-layout) and records every hand-over in the log.
4. **Check.** Verify each report against its done check (DRC, silk audit, page counts, exported slide images). A
   failed check goes back to the same agent (SendMessage), not to a new one.
5. **Close.** Commit, then report to Enes: what changed, the check numbers, open questions.

## Log

Every round is appended to `reports/design-loop/log.md`: date, Enes's comment, plan, each message
leader -> agent and agent -> leader (one or two lines each, with the numbers), checks, commit hash.

## Standing rules (all agents)

- The load board and busbar stay frozen until the DPT board is built and tested.
- Never edit Enes's LTspice files; never kill WINWORD.EXE (it may hold Enes's own documents).
- Loop inductance is quoted per cell.
- Agents do not commit; the leader commits. Do not commit hardware/To-do.txt,
  hardware/spb-bb-fab/spb-bb-fab.kicad_pro, reports/paper/ICPE_Template.docx or ../Review-Paper-SPB.
- Enes pushes from GitHub Desktop.
