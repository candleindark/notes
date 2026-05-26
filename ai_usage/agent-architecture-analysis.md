# Single Agent + Skills vs. Multiple Agents: Frontend/Backend Work

**Purpose:** Compare two ways of using Claude Code (or a similar agentic system) to solve a feature that spans frontend and backend code, and recommend an approach.

**Context:** The initial proposal was to use *multiple agents* — one specialized for backend, one for frontend — that collaborate to produce a solution. This memo evaluates that against the alternative: a *single agent* equipped with both frontend and backend *skills*.

---

## Recommendation (TL;DR)

**Use a single agent equipped with both a frontend skill and a backend skill** as the default for feature work that spans both layers.

For a feature where the frontend and backend are two halves of *one* coupled problem, the multiple-agent approach adds cost and coordination overhead without buying real collaboration. Reserve multiple agents for tasks where *isolation itself is the benefit* (see "When multiple agents win" below).

---

## Key technical facts these conclusions rest on

These are properties of how the agent system actually works, not opinions:

1. **Subagents cannot talk to each other.** There is no peer-to-peer channel. A subagent receives a prompt, runs in an **isolated context**, and returns a **single final message**. The only communication is parent→child (the spawn prompt) and child→parent (the one result).

2. **"Collaboration" between agents is really orchestration by a coordinator.** Any back-and-forth is the main agent relaying serialized messages between two isolated workers — not autonomous interaction.

3. **Skills load into the *current* context and stack.** Multiple skills can be loaded in one conversation; their instructions coexist and the agent applies all of them at once.

4. **Skills use progressive disclosure.** Only a skill's name + description sits in context by default; the full body loads on invocation, and deeper bundled resources load later on demand. So loading several focused skills is comparatively cheap.

5. **Skills do not propagate into a subagent's isolated context.** A subagent only has the skills its own definition grants it.

---

## Side-by-side comparison

| Dimension | Single agent + multiple skills | Multiple specialized agents |
|---|---|---|
| **Shared context** | Frontend and backend held in one context; the agent sees both sides of the API contract simultaneously. | Each agent isolated; shared info must be re-passed every round. |
| **Collaboration** | Native — no relaying needed; one mind reasons across the seam. | Simulated; coordinator serializes messages back and forth. |
| **Token cost** | Lower for coupled work — context isn't repeated. Skills add modest, on-demand overhead. | Higher — coupling means the same contract/state is re-sent each iteration, plus each spawn re-derives context cold. |
| **Latency / overhead** | Single thread, no orchestration loop. | Orchestration adds round-trips and coordination overhead. |
| **Handling coupling** | Strong — changes on one side immediately inform the other. | Weak — coupling must squeeze through a narrow message channel. |
| **Context-window pressure** | Higher in one thread (everything resident), but bounded by progressive disclosure. | Lower per agent (noise stays isolated) — a real advantage *when there's a lot of noise to isolate*. |
| **Parallelism** | None (one thread). | Real wall-clock speedup — *but only for independent tasks*. |
| **Best fit** | One feature that spans both layers (coupled work). | Independent tasks, noisy exploration, or clean-slate review. |

---

## Why single-agent + skills wins for *this* problem

A feature that touches both frontend and backend is **one coupled problem**, not two independent ones. The API contract, data shapes, error handling, and edge cases must agree across the seam. That argues for one context, because:

- **No serialization tax.** With two agents, the only way the frontend "knows" the backend contract is for the coordinator to copy it into the frontend agent's prompt — every iteration, since the contract evolves. The single agent just *has* it.

- **Faster convergence.** Negotiating a contract between two isolated halves takes multiple relay rounds. One agent resolves the same tension in a single line of reasoning.

- **Fewer tokens, less latency.** No repeated context, no orchestration loop, no cold re-spawns.

- **Skills give the specialization anyway.** The appeal of "a backend specialist and a frontend specialist" is the *expertise*, not the separate brains. Skills deliver that expertise into one agent: load a frontend skill and a backend skill and the single agent is competent at both — without splitting the brain in two.

The core principle: **subagents help when isolation is the benefit** (discarding noise, parallelism, avoiding bias). When subtasks must *share evolving context* — exactly the frontend/backend-of-one-feature case — isolation is a cost, not a benefit.

---

## When multiple agents *do* win (a fair hearing)

The multiple-agent approach is not wrong in general — it's the right tool for a different shape of problem. It pays off when **isolation is an asset**:

1. **Context-window protection.** A subagent does a big, noisy job (search hundreds of files, read long logs, explore an unfamiliar module) and returns only the conclusion. The noise never enters the main context. *Here isolation saves net tokens.*

2. **Genuine parallelism.** Several **independent** tasks run at once for wall-clock speedup. (Frontend and backend of one feature are *coupled*, so this doesn't apply here.)

3. **Clean-slate / bias isolation.** E.g. a reviewer that should judge a diff without being primed by the author's reasoning. A separate context is the point.

4. **A specialized, repeatable role** with its own tool restrictions and system prompt you don't want polluting the main thread.

**If the frontend and backend pieces were truly independent** — e.g. two unrelated bugs that happen to live in different layers — then running them as parallel agents would be reasonable. The deciding question is **coupling**, not which layer the code lives in.

---

## Bottom line

| If the work is… | Use… |
|---|---|
| One feature spanning frontend **and** backend (coupled) | **Single agent + frontend skill + backend skill** |
| Independent tasks, possibly parallel | Multiple agents |
| Noisy exploration whose output should not flood the main thread | A subagent (e.g. an explore agent) |
| Unbiased review of work already done | A separate-context agent |

For the proposed frontend/backend feature, the coupling points to **a single agent equipped with both skills**. Multiple agents would add token and orchestration cost without delivering the autonomous collaboration the name implies — because subagents don't actually interact; a coordinator relays between isolated contexts.

We can still adopt multiple agents selectively for the sub-parts that are genuinely independent or noisy.
