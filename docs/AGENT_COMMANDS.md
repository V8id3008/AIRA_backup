# A.I.R.A. Agent Commands

## Project path

```text
C:\Users\Pratyush Tyagi\AIRA
```

## Python command

Use the installed Python interpreter:

```cmd
C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe
```

If the path with spaces causes a CMD parsing problem, use the short path:

```cmd
C:\Users\PRATYU~1\AppData\Local\Programs\Python\PYTHON~2\python.exe
```

## Agent Command Center

File:

```text
C:\Users\Pratyush Tyagi\AIRA\agents\command_agent.py
```

Run it:

```cmd
cd /d "C:\Users\Pratyush Tyagi\AIRA"
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" -m agents.command_agent
```

The command center lists all agents, shows whether each is READY or PLANNED, and lets you launch an independent agent instance by number.

Inside the command center:

```text
number  Select and launch an agent
list    Display the agent list again
exit    Close the command center
```

## Available agents

| Number | Agent | Module | Status |
|---:|---|---|---|
| 1 | Debugging Agent | `agents.debug_agent` | READY |
| 2 | Planning Agent | `agents.planning_agent` | READY |
| 3 | Memory Agent | `agents.memory_agent` | READY |
| 4 | Research Agent | `agents.research_agent` | READY |
| 5 | Coding Agent | `agents.coding_agent` | READY |
| 6 | Testing Agent | `agents.testing_agent` | READY |
| 7 | Self-Building Agent | `agents.self_building_agent` | READY |
| 8 | Code Review Agent | planned | PLANNED |
| 9 | Documentation Agent | planned | PLANNED |
| 10 | System Agent | planned | PLANNED |
| 11 | Security Agent | planned | PLANNED |
| 12 | Multi-Agent Coordinator | planned | PLANNED |

## Agent access through the command center

### Debugging Agent

Select agent `1` in the command center. It performs compilation checks and bounded agent tests.

Example request:

```text
debug why AIRA is not starting
```

### Planning Agent

Select agent `2` in the command center. It creates a dependency-aware execution plan.

Example request:

```text
plan how to fix the memory system
```

### Memory Agent

Select agent `3` in the command center. It provides memory recall, candidate extraction, validation, and explicit storage operations.

Example request:

```text
what do you remember about my project
```

### Research Agent

Select agent `4` in the command center. It collects and formats web research sources. Internet access may be required.

Example request:

```text
research the latest AI agent frameworks
```

### Coding Agent

Select agent `5` in the command center. It inspects Python files and proposes coding work. It is currently read-only.

Example request:

```text
inspect the memory database and propose a fix
```

### Testing Agent

Select agent `6` in the command center. It runs compilation and the deterministic agent test suite.

Example request:

```text
run the agent tests
```

### Self-Building Agent

File:

```text
C:\Users\Pratyush Tyagi\AIRA\agents\self_building_agent.py
```

Run the normal read-only build cycle:

```cmd
cd /d "C:\Users\Pratyush Tyagi\AIRA"
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" -m agents.self_building_agent
```

Show only the build plan:

```cmd
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" -m agents.self_building_agent --plan-only
```

It inspects installed agents, identifies the next planned agent, runs compilation, and runs agent tests. It does not edit files automatically.

## Project test commands

Run the configured full test suite:

```cmd
cd /d "C:\Users\Pratyush Tyagi\AIRA"
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" -m pytest -q
```

Compile the agent and orchestrator code:

```cmd
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" -m compileall -q agents orchestrator
```

## Main A.I.R.A. application

```cmd
cd /d "C:\Users\Pratyush Tyagi\AIRA"
"C:\Users\Pratyush Tyagi\AppData\Local\Programs\Python\Python312\python.exe" main.py
```

## Safety note

The current agents are read-only or diagnostic. The Self-Building Agent reports plans and test results but does not modify project files. Future code-writing and system agents should require explicit confirmation before applying edits or performing destructive actions.
