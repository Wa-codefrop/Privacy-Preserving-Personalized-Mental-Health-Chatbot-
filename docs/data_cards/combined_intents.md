# Data Card: combined_intents.json

- Provenance: UNVERIFIED
- Intended use: deterministic intent routing and a small set of response patterns
- Composition: 92 intents, 337 patterns, 156 responses
- Notes: some responses are stored under a legacy misspelling (`resonses`), which must be normalized before any routing use.
- Known bias: intent categories are not a substitute for crisis assessment.
- Forbidden use: never answer a safety-related intent with a canned response if the tier should escalate.
