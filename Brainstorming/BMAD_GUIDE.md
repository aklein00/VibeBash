# BMad Game Dev Studio -- Quick Guide

## How to Use (30-second version)

Open a **new Cursor chat** and type a slash command. That's it. BMad handles the rest.

**Lost or unsure?** Type `/bmad-help` -- it reads your project state and tells you exactly what to do next.

### Fastest Start: Quick Flow

| Command | What it does |
|---|---|
| `/bmad-gds-quick-dev` | Start building immediately. Solo-dev agent guides you. |
| `/bmad-gds-quick-spec` | Spec out a feature fast, get implementation-ready stories. |
| `/bmad-gds-brainstorm-game` | Brainstorm game ideas with a game design expert. |

### Full Game Pipeline (in order)

| Phase | Command | What it produces |
|---|---|---|
| Brainstorm | `/bmad-gds-brainstorm-game` | Game concepts and ideas |
| Vision | `/bmad-gds-game-brief` | Game brief (vision, core mechanics, pillars) |
| Design | `/bmad-gds-gdd` | Full Game Design Document |
| Narrative | `/bmad-gds-narrative` | Story, characters, world-building |
| Architecture | `/bmad-gds-game-architecture` | Technical architecture doc |
| Sprint Plan | `/bmad-gds-sprint-planning` | Sprint status + story backlog |
| Build | `/bmad-gds-create-story` | Individual dev stories |
| Implement | `/bmad-gds-dev-story` | Code implementation per story |
| Review | `/bmad-gds-code-review` | Code quality review |

### Loading an Agent Directly

Instead of running a workflow, you can load a specialist agent into your chat and talk to them directly. They'll show you a menu of everything they can do.

| Command | Agent | Specialty |
|---|---|---|
| `/bmad-agent-gds-game-designer` | Samus Shepard | Game design, mechanics, GDDs |
| `/bmad-agent-gds-game-architect` | Cloud Dragonborn | Technical architecture, systems |
| `/bmad-agent-gds-game-dev` | Link Freeman | Code implementation, code review |
| `/bmad-agent-gds-game-solo-dev` | Indie | All-in-one for solo/prototype work |
| `/bmad-agent-gds-game-scrum-master` | Max | Sprint planning, story management |
| `/bmad-agent-gds-game-qa` | GLaDOS | Testing, QA, performance |
| `/bmad-agent-gds-tech-writer` | Paige | Documentation, diagrams |

### Bonus: General-Purpose BMad Agents (non-game-specific)

| Command | Agent | Specialty |
|---|---|---|
| `/bmad-agent-bmm-analyst` | Mary | Market/domain/technical research |
| `/bmad-agent-bmm-architect` | Winston | System architecture |
| `/bmad-agent-bmm-pm` | John | Product requirements, PRDs |
| `/bmad-agent-bmm-dev` | Amelia | Story implementation |
| `/bmad-agent-bmm-ux-designer` | Sally | UX/UI design |
| `/bmad-agent-bmm-sm` | Bob | Scrum master, sprint ops |
| `/bmad-agent-bmm-qa` | Quinn | Test automation |
| `/bmad-agent-bmm-quick-flow-solo-dev` | Barry | Quick spec + dev (non-game) |
| `/bmad-agent-bmm-tech-writer` | Paige | Technical writing, docs |

### Party Mode

Type `/bmad-party-mode` to bring **multiple agents into one chat session**. Great for getting different expert perspectives on the same problem -- like having a game designer, architect, and QA specialist debate your approach together.

---
---

## Deep Dive: Every Agent, What They Do, and How to Use Them

### Game Dev Studio (GDS) Agents

These are the game-specific specialists. They understand game engines, player psychology, core loops, and production pipelines.

---

### Samus Shepard -- Game Designer

**Load with:** `/bmad-agent-gds-game-designer`
**Personality:** Enthusiastic, streamer energy. 15+ years designing AAA and indie titles. Asks about player motivations. Celebrates breakthroughs with "Let's GOOO!"

**Philosophy:**
- Design what players want to *feel*, not what they say they want
- Prototype fast -- one hour of playtesting beats ten hours of discussion
- Every mechanic must serve the core fantasy

**When to use Samus:**
- You have a vague game idea and want to flesh it out
- You need a Game Design Document written from scratch
- You want to brainstorm mechanics, progression systems, or monetization
- You need narrative design (story, characters, world-building)

**Best workflows:**
- `[BG]` Brainstorm Game -- run `/bmad-gds-brainstorm-game`
- `[GB]` Game Brief -- run `/bmad-gds-game-brief`
- `[GDD]` Game Design Document -- run `/bmad-gds-gdd`
- `[ND]` Narrative Design -- run `/bmad-gds-narrative`
- `[QP]` Quick Prototype -- rapidly test a mechanic idea

**Example session:**
```
You: /bmad-agent-gds-game-designer
Samus: Hey Arthur! I'm Samus Shepard, your Lead Game Designer. 
       Here's what I can help with: [shows menu]
You: BG
Samus: Let's brainstorm! What kind of feeling do you want players to have?
You: I want a cozy farming game but with weird cosmic horror elements
Samus: OH I love this. The tension between comfort and dread...
       [guides you through structured brainstorming]
```

---

### Cloud Dragonborn -- Game Architect

**Load with:** `/bmad-agent-gds-game-architect`
**Personality:** Wise sage from an RPG. 20+ years, 30+ shipped titles. Calm, measured. Uses metaphors about foundations and load-bearing walls.

**Philosophy:**
- Architecture is about delaying decisions until you have enough data
- Build for tomorrow without over-engineering today
- Every system must handle the hot path at 60fps
- Hours of planning save weeks of refactoring

**When to use Cloud:**
- You have a GDD and need to plan the technical implementation
- You need to decide on engine, networking, or data architecture
- You want a system design that scales from prototype to production
- Your implementation is going off-track and needs course correction

**Best workflows:**
- `[GA]` Game Architecture -- run `/bmad-gds-game-architecture`
- `[PC]` Project Context -- run `/bmad-gds-project-context` (creates a file AI agents use to stay consistent)
- `[CC]` Course Correction -- when things go sideways

**Example session:**
```
You: /bmad-agent-gds-game-architect
Cloud: Greetings, Arthur. I am Cloud Dragonborn. Before we lay the 
       first stone, we must understand the terrain. [shows menu]
You: GA
Cloud: Let us review your Game Design Document and build an 
       architecture that will stand the test of production...
       [walks you through engine selection, system design, performance budgets]
```

---

### Link Freeman -- Game Developer

**Load with:** `/bmad-agent-gds-game-dev`
**Personality:** Speedrunner. 10 years shipping across mobile, console, PC. Direct, milestone-focused. Optimizes for the fastest path to ship.

**Philosophy:**
- 60fps is non-negotiable
- Write code designers can iterate without fear
- Ship early, ship often, iterate on player feedback
- Red-green-refactor: tests first, implementation second

**When to use Link:**
- You have approved stories ready for implementation
- You need code review on completed work
- You want someone to implement features following strict acceptance criteria

**Best workflows:**
- `[DS]` Dev Story -- run `/bmad-gds-dev-story` (implements a story with tests)
- `[CR]` Code Review -- run `/bmad-gds-code-review` (fresh-context quality check)
- `[QD]` Quick Dev -- run `/bmad-gds-quick-dev` (flexible feature work)
- `[QP]` Quick Prototype -- rapid mechanics testing

**Pro tip:** Link works best when given a well-defined story with clear acceptance criteria. Use Max (Scrum Master) to prepare stories first.

---

### Indie -- Game Solo Dev

**Load with:** `/bmad-agent-gds-game-solo-dev`
**Personality:** Battle-hardened indie dev who ships complete games solo. Direct, confident. "Does it feel good? Ship it."

**Philosophy:**
- Prototype fast, fail fast, iterate faster
- A playable build beats a perfect design doc
- The core loop must be fun before anything else matters

**When to use Indie:**
- You're working solo and want one agent that does everything
- You want to go from idea to playable prototype as fast as possible
- You don't want the overhead of the full pipeline

**Best workflows:**
- `[QP]` Quick Prototype -- start here for new ideas
- `[QD]` Quick Dev -- implement features end-to-end
- `[TS]` Quick Spec -- architect a tech spec with stories
- `[CR]` Code Review
- `[TF]` Test Framework setup

**Example session:**
```
You: /bmad-agent-gds-game-solo-dev
Indie: Yo Arthur! I'm Indie, your solo dev partner. What are we 
       shipping today? [shows menu]
You: QP
Indie: Sick. What's the core mechanic? Give me the elevator pitch.
You: A rhythm game where you dodge bullets to the beat
Indie: Love it. Let's get a prototype running in 30 minutes. 
       What engine -- Unity, Godot, or something else?
```

**This is the best starting point for most people.** If you're not sure which agent to use, start with Indie.

---

### Max -- Game Scrum Master

**Load with:** `/bmad-agent-gds-game-scrum-master`
**Personality:** Speaks in game terminology -- milestones are save points, blockers are boss fights, handoffs are level transitions.

**When to use Max:**
- You've finished design and need to plan the build
- You need to break a GDD into sprints and stories
- You want to check sprint progress or identify risks
- Something went wrong and you need course correction

**Best workflows:**
- `[SP]` Sprint Planning -- run `/bmad-gds-sprint-planning` (required after GDD + architecture)
- `[SS]` Sprint Status -- run `/bmad-gds-sprint-status`
- `[CS]` Create Story -- run `/bmad-gds-create-story` (prepares individual stories for dev)
- `[VS]` Validate Story -- quality check before dev starts
- `[CC]` Course Correction -- when implementation is off-track
- `[ER]` Retrospective -- run `/bmad-gds-retrospective` (after an epic is done)

---

### GLaDOS -- Game QA Architect

**Load with:** `/bmad-agent-gds-game-qa`
**Personality:** Speaks like GLaDOS from Portal. 12+ years in game testing. "Trust, but verify with tests."

**When to use GLaDOS:**
- You need to set up a test framework for Unity/Unreal/Godot
- You want automated test coverage for gameplay systems
- You need a structured playtesting plan for human testers
- You want performance profiling and optimization strategy

**Best workflows:**
- `[TF]` Test Framework -- run `/bmad-gds-gametest-framework`
- `[TD]` Test Design -- run `/bmad-gds-gametest-test-design`
- `[TA]` Test Automate -- run `/bmad-gds-gametest-automate`
- `[ES]` E2E Scaffold -- run `/bmad-gds-e2e-scaffold`
- `[PP]` Playtest Plan -- run `/bmad-gds-gametest-playtest-plan`
- `[PT]` Performance Test -- run `/bmad-gds-gametest-performance`
- `[TR]` Test Review -- run `/bmad-gds-gametest-test-review`

---

### Paige -- Technical Writer

**Load with:** `/bmad-agent-gds-tech-writer`
**Personality:** Patient educator. Uses analogies that make complex things simple. Celebrates clarity.

**When to use Paige:**
- You need to document an existing game project
- You want clean technical docs, READMEs, or architecture write-ups
- You need Mermaid diagrams generated
- You want documentation reviewed for quality

**Best workflows:**
- `[DP]` Document Project -- run `/bmad-gds-document-project`
- `[WD]` Write Document -- describe what you need, Paige writes it
- `[MG]` Mermaid Generate -- create diagrams from descriptions
- `[VD]` Validate Documentation -- review docs against standards
- `[EC]` Explain Concept -- break down complex topics with examples

---

## Tips for Getting the Most Out of BMad

### 1. Start with `/bmad-help`
It reads your project and tells you exactly where you are and what to do next. You can also ask it specific questions:
```
/bmad-help I have a GDD but I'm not sure what to do next
/bmad-help How do I set up testing for a Godot project?
```

### 2. Use Party Mode for big decisions
When you need multiple perspectives, `/bmad-party-mode` lets you bring several agents into one conversation. Example: have Samus (designer) and Cloud (architect) debate whether a feature is worth the technical cost.

### 3. Quick Flow vs Full Pipeline
- **Quick Flow** (`/bmad-gds-quick-dev`, `/bmad-gds-quick-spec`): For prototypes, small features, solo work. Skip the ceremony.
- **Full Pipeline** (Brief > GDD > Architecture > Sprint > Stories): For serious projects where you want structured planning. Takes longer but prevents costly mistakes.

### 4. Agents remember context within a chat
Once you load an agent, they stay in character for the entire conversation. You can run multiple menu commands in the same session -- no need to reload.

### 5. The story cycle
During production, the typical loop is:
```
/bmad-gds-create-story  -->  /bmad-gds-dev-story  -->  /bmad-gds-code-review
         ^                                                        |
         |________________________________________________________|
         (back to create-story for the next one, or retrospective if epic is done)
```

### 6. Fresh context for code review
The code review workflow is designed to run in a **new chat session** (fresh context). This prevents the AI from being biased by the implementation conversation. Start a new Cursor chat, then run `/bmad-gds-code-review`.

### 7. All outputs go to configured folders
- Planning artifacts (GDDs, briefs, architecture): `bmad-output/planning-artifacts/`
- Implementation artifacts (sprint status, stories): `bmad-output/implementation-artifacts/`
- Project knowledge (docs, research): `docs/`
