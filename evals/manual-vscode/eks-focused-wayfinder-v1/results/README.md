# EKS focused Wayfinder v1 evidence

These are the frozen chat exports for the manual VS Code comparison described
by [`../protocol.md`](../protocol.md). The compact adjudication is
[`../evaluation-report.md`](../evaluation-report.md).

## Evidence inventory

| Artifact | Condition | SHA-256 | Status |
| --- | --- | --- | --- |
| [`A/A-chat.json`](A/A-chat.json) | Built-in general Agent using canonical Wayfinder | `fa1dbced290d418cb30bf1d1364ff6eb26adc1fd8347dcb9a02a28637c15c96c` | Evaluated |
| [`B/B-chat-superseded.json`](B/B-chat-superseded.json) | Intended focused condition, but the focused custom agent was not active | `2575174e58f5139a6356018920a281e544eb3a308fab9bb80a2849fd0d8f148e` | Superseded; exclude from semantic comparison |
| [`B/B-chat.json`](B/B-chat.json) | Workspace Wayfinder custom agent | `87ef3dba56e94f5b07eb01dd9958d4ca811b9268594a63a270b98b60b9c407cf` | Evaluated |

The external disposable A/B repositories were not copied. Direct inspection
before preservation established that both Wayfinder state directories remained
empty and unchanged, the original repository still matched the frozen source
snapshot, and the only A/B filesystem difference was an A-only zero-byte
`.vscode/settings.json` created before the request.

Agent Debug Logs, Copy All Markdown, run notes, and customization diagnostics
were unavailable. Their metrics and audits are therefore not available, not
zero.
