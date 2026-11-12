<!-- .agents/plan.md: Agent-generated PRD & architecture built from .agents/idea.md.

Workflow:
1. Human pastes raw concept/notes into .agents/idea.md (or describes them in chat).
2. Agent verifies packages, versions, APIs, and docs in Phase 2 — never from memory.
3. Agent writes "## Research Findings" and "## Design" (PRD + Mermaid diagrams) here, then
   STOPS at the Approval Gate for human review and iteration before coding.
4. Once approved and built, the code is the specification; shipped files outside .agents/
   must never reference .agents/idea.md or .agents/plan.md. -->

# Increment Plan

## Research Findings

_Populated by the agent during Phase 2 (Research & Verification): verified package versions and APIs, current service capabilities, stale assumptions corrected from `.agents/idea.md`, and proposed simplifications with reasoning._

## Design

_Populated by the agent during Phase 3 (Design): formal requirements, module responsibilities, data/control flow, and Mermaid architecture diagrams. Requires human approval before Phase 5 (Execution)._
