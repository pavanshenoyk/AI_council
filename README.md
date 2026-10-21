# AI_council

A reusable multi-agent AI framework for state management, agent orchestration, iterative reasoning, and human-in-the-loop workflows.

AI Council keeps a structured **project context** (a Pydantic model), passes it through a configurable chain of agents, stores the result in a database, and lets the user keep refining it chat-style. It is the orchestration core behind **Sparkforge**, an SDLC assistant for early-stage planning (requirements, tech stack, architecture, test cases).

## How it works

Each user message triggers one pass through the pipeline:

1. **Context update**: `ContextManager` sends the new message plus the current context to an LLM (OpenAI API) and gets back an updated `ProjectExtraction` JSON. Missing fields stay `null` or empty; nothing is invented.
2. **Agent pipeline**: every enabled agent from `config.py` runs in order. Each receives the context JSON, returns JSON, and `apply_output` validates it and merges it back. Invalid or off-schema output is ignored and the previous context is kept.
3. **Render and save**: the context is rendered to readable text, appended to the project's `chats` list as a prompt/output pair, and the updated context is written back to the database.

### Project context (`ProjectExtraction`) : (Please change it based on your context requirement)

| Field | Type | Purpose |
|---|---|---|
| `project_type` | `str \| None` | Kind of project only (e.g. IoT, mobile app) |
| `project_description` | `str \| None` | What the project does and for whom |
| `team_size` | `int \| None` | Number of people on the project |
| `rules` | `list[str]` | User preferences and constraints |
| `functional_requirements` | `list[str]` | Explicitly stated functional requirements |
| `non_functional_requirements` | `list[str]` | Explicitly stated non-functional requirements |
| `techstack` | `list[TechItem]` | Technologies mapped to their purpose (`name`, `purpose`) |
| `database_design` | `str \| None` | Full database design as text |
| `project_planning` | `str \| None` | Full project plan as text |
| `architecture_design` | `str \| None` | Full architecture design as text |
| `testcases` | `list[str]` | Test cases |

## Project layout 

```
AI_council/
├── Orchestrator.py            # Main loop: context update, agent pipeline, persistence
├── AgentLoader.py             # Loads enabled agents and connects the database
├── config.py                  # Agents, database, and context settings
├── agentloader_test.py        # Smoke test for the loader
├── Agents/
│   └── <agent_name>/agent.pt  # One folder per agent, named after it in config
└── Resources/
    ├── AgentWrapper.py        # Model wrapper exposing generate()
    ├── ContextHandler.py      # ProjectExtraction schema + ContextManager
    ├── ContextHandler_test.py
    ├── DatabaseFunc/
    │   ├── DBAbstract.py      # AbstractDatabaseController
    │   ├── MongoDB.py         # MongoDBController (pymongo)
    │   ├── DBAssigner.py      # (placeholder) backend selection
    │   └── PostgresSQL.py     # (placeholder)
    └── GarbageCollector/
        └── RAMCleanup.py      # (placeholder)
```

## Requirements

- Python 3.10+
- A running MongoDB instance (default `mongodb://localhost:27017`)
- An OpenAI API key, used by `ContextManager`
- [TransformerAgentModels](https://github.com/pavanshenoyk/TransformerAgentModels), the transformer and agent wrapper library needed to load the pickled `agent.pt` files (installed automatically by `requirements.txt`)

```bash
pip install -r requirements.txt
```

Set your API key as an environment variable rather than in code:

```bash
# Linux / macOS
export OPENAI_API_KEY="your-key"

# Windows PowerShell
$env:OPENAI_API_KEY = "your-key"
```

## Configuration

Everything is set in `config.py`:

```python
config = {
    "agents": [
        {
            "name": "test_agent",    # must match the folder name under Agents/
            "interactive": False,    # auto / interactive
            "API": False,            # True = API-backed agent (not implemented yet)
            "api_url": "",
            "enable": True,
            "weight_only": False     # passed to torch.load(weights_only=...)
        }
    ],
    "database": "mongodb",           # only mongodb for now
    "db_url": "",                    # empty = local default
    "db_name": "Spark_DB",
    "context_size": 5                # how many previous iterations to pull in when continuing a chat
}
```

Agents run in the order they appear in the `agents` list. Set `enable` to `False` to skip one.

## Running

Check that agents and the database load:

```bash
python agentloader_test.py
```

Start the chat loop:

```bash
python Orchestrator.py
```

You will be asked for a project id. The project must already exist in the `projects` collection:

| Field | Description |
|---|---|
| `_id` | Project id |
| `main_prompt` | Set from the first message if empty |
| `chats` | List of `{prompt, output}` pairs |
| `context` | The saved `ProjectExtraction` as a dict |

Type a message to run one pipeline pass. Type `quit` or `exit` to stop.

## Adding an agent

1. Create `Agents/<agent_name>/` and put the trained `agent.pt` inside.
2. Add an entry to `config["agents"]` with the same `name`, at the position it should run in the pipeline.
3. The agent object must expose `model.generate(prompt, max_tokens, temperature)`, which is what `Resources/AgentWrapper.py` calls.

> `agent.pt` files are loaded with `weights_only=False` by default in the sample config, which executes pickled code. Only load agents you trust.

## Adding a database backend

Subclass `AbstractDatabaseController` and implement `connect`, `close`, `insert`, `find`, `update`, and `delete`. `MongoDBController` is the reference implementation. The loader currently instantiates `MongoDBController` directly; config-driven backend selection through `DBAssigner` is planned.

## Roadmap

- Config-driven database backend selection (`DBAssigner`)
- PostgreSQL backend
- API-backed agents (`API: true`)
- Pluggable consensus mechanisms (majority vote, weighted vote, debate, judge model)
- Early pipeline termination when an agent needs to ask the user a question
- Context size handling when resuming old chats

## License

MIT. See [LICENSE](LICENSE).