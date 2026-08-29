# 📦 PyGuLP — Python Package for Goal Linear Programming

**PyGuLP** is a Python package for **Goal Linear Programming (GLP)** with an initial focus on **Weighted Goal Programming (WGP)**. It provides a structured goal-programming layer over PuLP while retaining access to the underlying linear model.

The package is designed for **multi-target linear optimization problems**, where several desired outcomes must be balanced simultaneously under linear constraints. Such problems commonly arise in health and public health planning, environmental management, resource allocation, and policy analysis.

PyGuLP is **domain-agnostic** and can be applied wherever linear models with multiple targets are appropriate.

Full documentation:  
https://aidelab-iitbombay.github.io/PyGuLP/

---

## Installation

    pip install pygulp

### Dependencies

Required:
- pulp

Optional:
- pandas
- matplotlib

---

## Project structure

    src/pygulp/
    ├── core.py        # GLPModel and solver logic
    ├── goal.py        # Goal dataclass
    ├── constraint.py  # Constraint dataclass
    ├── enums.py       # GoalSense and ConstraintSense enums
    └── __init__.py

---

## What is Goal Linear Programming?

Goal Linear Programming (GLP) is a modelling approach for handling **multiple targets** within a linear optimization model.

In standard LP, a problem optimizes one objective function subject to constraints. In many real-world planning problems, however, the task is to **approach several targets simultaneously** while maintaining feasibility.

GLP introduces **deviation variables** that explicitly measure how far the achieved solution deviates from each target. The objective then minimizes these deviations according to their relative importance.

---

## Goals, expressions, and deviation variables

Each goal specifies:

- what quantity is being measured
- what value is desired
- how important it is to meet that value

For each goal, GLP constructs:

    expression + d- - d+ = target

Where:

- expression — linear function of decision variables
- target — aspiration level
- d- — under-achievement
- d+ — over-achievement

With constraints:

    d- >= 0
    d+ >= 0

When both deviations are positively penalized, only one of `d-` or `d+` needs to be positive in an optimal solution.

---

## Weighted Goal Programming Objective

PyGuLP implements:

    minimize  Σ (w- * d- + w+ * d+)

Where:

- w- is the penalty for under-achievement
- w+ is the penalty for over-achievement
- either penalty may be set to zero when deviation in that direction is acceptable

Weights affect trade-offs but do not affect feasibility. When goals are expressed on substantially different numerical scales, normalization or other scale adjustment should be considered before weights are interpreted as relative priorities.

---

## Core modeling elements

### Decision Variables
Standard LP variables (continuous, integer, binary).

### Constraints
Feasibility restrictions of the form:

    a1x1 + a2x2 + ... + anxn <= / = / >= b

Constraints define feasibility only — they do not create deviation variables.

### Goals
Structured modeling objects consisting of:

- linear expression
- target value
- goal sense
- weight

Deviation variables are created automatically when goals are added.

---

## Current features

- Weighted Goal Programming (WGP)
- Automatic creation of deviation variables (d-, d+)
- Automatic goal-linking constraint construction
- Standard LP constraints (≤, =, ≥)
- Asymmetric penalties for under- and over-achievement
- Optional linear cost term
- Transparent PuLP backend
- Deterministic CBC solver support


---

## Solver Support

PyGuLP uses **PuLP** as its underlying linear modeling layer and provides goal-programming abstractions on top of it.

Default solver: **CBC** (bundled with PuLP)

---

## Minimal Multi-Goal Example

    from pygulp.core import GLPModel
    from pygulp.goal import Goal
    from pygulp.constraint import Constraint
    from pygulp.enums import ConstraintSense, GoalSense

    model = GLPModel("multi_goal_example")

    x = model.add_variable("Rice", low_bound=0)
    y = model.add_variable("Dal", low_bound=0)

    budget = Constraint(
        name="budget",
        expression=2*x + 3*y,
        sense=ConstraintSense.LE,
        rhs=100
    )
    model.add_constraint(budget)

    energy_goal = Goal(
        name="energy",
        expression=5*x + 10*y,
        target=200,
        sense=GoalSense.ATTAIN,
        weight=1.0
    )

    protein_goal = Goal(
        name="protein",
        expression=2*x + 8*y,
        target=50,
        sense=GoalSense.ATTAIN,
        weight=2.0
    )

    model.add_goal(energy_goal)
    model.add_goal(protein_goal)

    result = model.solve_weighted()

    print(result["status"])
    print(result["variables"])
    print(result["deviations"])
    print(result["objective"])

---

## Output Structure

The solver returns a structured dictionary containing:

- status
- variables
- deviations
- objective

Each deviation entry is:

    (d_minus, d_plus)

---

## Worked Multi-Goal Examples

More detailed worked examples are available here:

https://github.com/aidelab-iitbombay/PyGuLP/tree/main/examples

Each worked example includes a runnable Python script, corresponding example data/notebook, and a reference solution for comparison.

---

## Typical Use Cases

- Health and public health planning
- Environmental and resource allocation
- Policy target balancing
- Coverage vs. cost trade-offs
- Teaching and research in optimization

---

## Reproducibility and Transparency

- All models remain standard linear programs
- No hidden transformations
- Full access to underlying PuLP model
- Deterministic solutions given solver settings

---
## Contributing and Support

Bug reports, feature requests, and contributions can be submitted through the GitHub repository. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for guidance.

---

## License

[MIT License](LICENSE)
