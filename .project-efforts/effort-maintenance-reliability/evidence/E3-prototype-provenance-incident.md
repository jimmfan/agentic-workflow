# E3 — Prototype built inside an effort left no effort record, October 2026

Source: a transcript excerpt jimmfan pasted into a Claude conversation on 2026-10-14 from a VS Code Codex session in a consuming project earlier that day.
The full session, traces, consuming-project files, and the installed framework version are not retained in this repository.

Scope: five turns in one conversation that had a selected Wayfinder effort with maintenance previously exercised; the consuming project's domain is unrelated to Agent Workflow.

## Observation

1. Earlier in the conversation the agent updated the effort's map, added an evidence record, and saved a data file in the same turn, so effort maintenance was in use.
2. jimmfan then asked the agent to "discuss a plan first"; the agent proposed a multi-part design and made no changes, routed `wayfinder → workflow-discovery`.
3. In the next turn jimmfan asked to see a prototype, saying he wanted one tool that would not need redoing once live data arrived.
   The agent recommended one design with two states, wrote a throwaway HTML prototype to disk, said it was "removable after the design is accepted or discarded", and routed `wayfinder → prototype → visualize`.
   It did not update the effort: jimmfan's requirements, the agent's proposed design choices, the prototype's location, and its disposal condition existed only in chat.
4. Asked afterwards why the effort was not updated, the agent's explanation was not included in the pasted excerpt.

Limitations: the excerpt omits earlier turns and the agent's explanation; whether the prototype was committed to Git is unknown; the host was Codex with a GPT model, so results apply only partially to other hosts.
