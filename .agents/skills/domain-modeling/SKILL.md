---
description: Build and sharpen a project's domain concepts, terminology and ubiquitous language, domain or context boundaries, and domain responsibilities and relationships, and maintain the applicable domain or context model.
name: domain-modeling
---
# Domain Modeling

Build and sharpen the project's domain model as you design: challenge concepts and terminology, make ubiquitous language precise, test domain or context boundaries, and clarify domain responsibilities and relationships.
Maintain the model through `CONTEXT.md` and, for multiple contexts, `CONTEXT-MAP.md`.
Use this skill when changing the model; ordinary vocabulary lookup only requires reading the relevant glossary.

Domain Modeling does not own generic implementation or module architecture, all project structure, Wayfinder's effort-specific areas and relationships, or a generic architecture-decision store.

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts.
The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── src/
│   ├── ordering/
│   │   └── CONTEXT.md
│   └── billing/
│       └── CONTEXT.md
```

Create files lazily — only when you have something to write.
If no `CONTEXT.md` exists, create one when the first term is resolved.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately.
"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term.
"You're saying 'account' — do you mean the Customer or the User?
Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios.
Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees.
If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there.
Don't batch these up — capture them as they happen.
Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

Keep `CONTEXT.md` focused on domain terms and their meanings.
Keep implementation details, specifications, working notes, and implementation decisions in their own designated artifacts.
