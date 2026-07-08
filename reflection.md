# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes. Task (a dataclass) represents a single care activity and
holds a description, duration in minutes, priority (high/med/low), category, an
optional clock time, a completion flag, and a frequency (once/daily/weekly). Pet
(a dataclass) holds a name, species, and its own list of Tasks. Owner holds a name,
a daily time budget in minutes, and a list of Pets. Scheduler is the "brain": it
holds no data of its own and instead operates on an Owner to sort tasks, filter them
against the time budget, detect conflicts, and generate a daily plan.

**b. Design changes**

Yes. My initial skeleton's plan method only returned a list of tasks, but the
scenario asks the app to "explain why it chose that plan." I changed generate_plan
to return both the ordered task list and a plain-English reasoning string
(how many tasks were chosen, how much of the budget was used, how many were
deferred or in conflict), so the UI can actually surface the reasoning.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers two constraints: the owner's daily time budget (in minutes)
and each task's priority. Priority matters most — I decided a busy owner should
always do the important tasks (walks, medications) first, so priority is the primary
sort key and clock time is only a tiebreaker between same-priority tasks. The time
budget then caps how many of those sorted tasks make it into the final plan.

**b. Tradeoffs**

My conflict detection only flags tasks that share an exact start time. It won't catch
overlaps — a 30-minute 08:00 walk and an 08:15 feeding don't collide in my system
even though they would in real life. I chose exact-match because it's simple and
readable; duration-overlap detection would need interval comparison and a real time
model.

A second tradeoff: my time-budget filter is greedy — it keeps the highest-priority
tasks that fit, but doesn't try to pack in the most tasks possible (the knapsack
problem). For a pet planner, "do the important stuff first" is the right call, and
greedy is far simpler and more predictable than optimal packing.

---

## 3. AI Collaboration

**a. How you used AI**

I used two AI assistants for different jobs: one for step-by-step guidance,
understanding design decisions, and verifying my logic, and Gemini in VS Code for
inline code generation. The most helpful prompts were concrete ones tied to my
actual files — "fill in this stub given these classes" — rather than vague,
template-style requests. I kept separate chat sessions per phase so the context
stayed focused and I didn't mix up design questions with debugging.

**b. Judgment and verification**

At one point the AI wrote generate_plan to return three values (plan, reasoning,
conflicts), but that would have broken my app.py and main.py, which unpack only two.
I rejected that version and kept the method returning two values, exposing conflicts
through a separate detect_conflicts method instead. I also deliberately kept my
priority label as "med" rather than "medium" so my UI strings matched my
PRIORITY_ORDER dictionary exactly — a mismatch there would have silently broken
sorting. I verified every change by re-running main.py and pytest before committing.

---

## 4. Testing and Verification

**a. What you tested**

I tested the core scheduling behaviors: that marking a task complete flips its status,
that adding a task increases a pet's task count, that tasks come back sorted by
priority then time, that the time-budget filter defers tasks that don't fit, that
two tasks at the same clock time are flagged as a conflict, and that completing a
daily task generates a new occurrence for the next day. These matter because they
are the behaviors the whole app depends on — if sorting or filtering is wrong, the
generated plan is wrong.

**b. Confidence**

I'm fairly confident (4/5) the scheduler works for the cases it's designed to handle,
because each behavior has a passing test. If I had more time I'd add edge cases: a
pet with no tasks, a zero-minute budget, tasks with no time set, and overlapping
(not just identical) times.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the separation between the logic layer (pawpal_system.py) and
the UI (app.py). Because I built and verified the backend with a CLI demo first, the
Streamlit integration was mostly just wiring buttons to methods that already worked.

**b. What you would improve**

I'd add duration-aware overlap detection instead of exact-time matching, and expand
the UI to manage multiple pets rather than a single one. I'd also persist data between
runs so tasks aren't lost when the app restarts.

**c. Key takeaway**

The biggest thing I learned is that being the "lead architect" means owning the
design and the verification, not the typing. AI could generate code fast, but it was
my job to decide the class structure, catch when a suggestion would break existing
code, and prove the result actually worked with tests.