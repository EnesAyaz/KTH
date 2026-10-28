# Design-loop log

One section per round (newest at the bottom). Format:

```
## <date> - <short title>
Comment (Enes): ...
Plan: ...
-> <agent>: task ...
<- <agent>: result ... (numbers)
Checks: ...
Commit: <hash>
```

## 2026-10-27 - Loop set up
Comment (Enes): one leader to talk to, specialists that work in parallel, visible communication.
Plan: six agent definitions in .claude/agents, leader protocol in CLAUDE.md, this log.
Checks: none yet (no agent run).

## 2026-10-28 - Project-meeting poster
Comment (Enes): update the ICPE poster with the SPB review paper and the design-flow presentation.
Plan: leader did it directly (single document, no parallel work): scripts/make_poster.py, template style kept.
Checks: Inkscape PDF/PNG export, A0, no overflow (preview + 150 dpi detail checked).
Commit: 2aca85c
