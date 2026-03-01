# GrabInsurance MCP

> GrabOn VibeCoder Challenge 2025 | Project 02 | Contextual Embedded Insurance at Deal Redemption

## Section 1: What I Built

GrabInsurance MCP is a contextual embedded insurance system designed for GrabOn, India's largest coupon and deal discovery platform. When a user redeems a deal—whether it's a flight booking, electronics purchase, or food delivery—the system analyzes the deal context in real-time and presents a single, highly relevant insurance offer at the moment of maximum purchase intent.

The system is built as an MCP (Model Context Protocol) server, enabling direct integration with Claude Desktop. This architecture allows natural language interactions like "What insurance should I offer for this Rs 12,400 Goa flight?" while maintaining programmatic access through standard API endpoints. The system includes rule-based classification with Claude API fallback, dynamic premium calculation, personalized copy generation with A/B testing, and a React storefront for visual demonstration.

## Section 2: Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GrabInsurance MCP                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────────┐
│              │     │              │     │         MCP Server               │
│    React     │────▶│   FastAPI    │────▶│  ┌────────────────────────────┐  │
│   Frontend   │     │    Bridge    │     │  │  classify_deal_intent      │  │
│  (port 5173) │     │  (port 8000) │     │  │  get_insurance_quote       │  │
│              │◀────│              │◀────│  │  insurance://catalog       │  │
└──────────────┘     └──────────────┘     │  │  generate_copy prompt      │  │
                                          │  └────────────────────────────┘  │
                                          └──────────────────────────────────┘
                                                          │
                     ┌────────────────────────────────────┼────────────────┐
                     │                                    │                │
                     ▼                                    ▼                ▼
            ┌──────────────┐                    ┌──────────────┐  ┌──────────────┐
            │   Insurance  │                    │    Claude    │  │   SQLite     │
            │    Engine    │                    │     API      │  │  (aiosqlite) │
            │              │                    │              │  │              │
            │ • Classifier │                    │ • Fallback   │  │ • A/B events │
            │ • Pricing    │                    │ • Copy gen   │  │ • Sessions   │
            │ • Cart logic │                    │              │  │ • Metrics    │
            └──────────────┘                    └──────────────┘  └──────────────┘
                     │
                     ▼
            ┌──────────────┐
            │  Pricing API │
            │  (port 8001) │
            └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           Claude Desktop                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  "What insurance should I offer for this Samsung phone deal?"       │    │
│  │  → Calls classify_deal_intent tool                                  │    │
│  │  → Returns: ELEC_SCREEN (90% confidence), ELEC_WARRANTY (85%)       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Section 3: Key Architecture Decisions

### Why MCP over REST for Claude Integration?

MCP provides native Claude Desktop integration with automatic tool discovery, typed inputs/outputs, and conversational context. Unlike REST, Claude can explore resources (like the insurance catalog) and use prompts (for copy generation) within a single conversation flow. This enables natural interactions like "classify this deal and generate copy for it" without manual API orchestration.

### Why SQLite over Redis for Demo Scope?

SQLite with aiosqlite provides async-safe persistence without infrastructure overhead. For a demo with 10 scenarios and 3 A/B variants, SQLite's simplicity and zero-config setup outweigh Redis's speed advantages. The aiosqlite library ensures the event loop is never blocked during database operations.

### Why FastMCP over Raw MCP SDK?

FastMCP provides decorator-based tool registration, automatic schema generation, and built-in stdio transport handling. This reduces boilerplate by ~60% compared to raw SDK usage while maintaining full protocol compliance. The trade-off (less control over transport details) is acceptable for this use case.

### Why Rule-Based + Claude Fallback?

Rule-based classification handles 80% of deals instantly (sub-millisecond) with deterministic results. Claude API is only invoked for unknown categories or low-confidence matches, reducing costs and latency while maintaining accuracy for edge cases.

## Section 4: How to Run Locally

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- uv package manager (recommended) or pip

### Step 1: Clone and Setup

```bash
cd grabinsurance-mcp

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -e ".[dev]"
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Step 3: Start Backend Services

```bash
# Terminal 1: API Bridge
uvicorn api.main:app --port 8000 --reload

# Terminal 2: Pricing API
uvicorn api.pricing_api:app --port 8001 --reload
```

### Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### Step 5: Open Application

Navigate to <http://localhost:5173> in your browser.

## Section 5: How to Connect to Claude Desktop

> **See also:** [MCP_CONNECTION_GUIDE.md](MCP_CONNECTION_GUIDE.md) for the full step-by-step guide with detailed troubleshooting.

### 1. Locate your Claude Desktop config file

| OS | Config File Path |
|----|-----------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

### 2. Add the MCP server config (recommended: using `uv`)

```json
{
  "mcpServers": {
    "grabinsurance": {
      "command": "/ABSOLUTE/PATH/TO/uv",
      "args": [
        "run",
        "--directory", "/ABSOLUTE/PATH/TO/Grabon-MCP",
        "python",
        "mcp_server/server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here",
        "CATALOG_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/insurance_catalog.json",
        "AB_DB_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/ab_events.db"
      }
    }
  }
}
```

Run `which uv` and `pwd` to find your absolute paths. Replace `/ABSOLUTE/PATH/TO/` with the actual values.

### 3. Restart Claude Desktop (Cmd+Q, then reopen)

### 4. Test the connection

- Click the **🔨 hammer icon** in the chat input area
- You should see `classify_deal_intent` and `get_insurance_quote` listed
- Try: *"What insurance products are available in the catalog?"*

### ⚠️ Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `Failed to spawn process: No such file or directory` | `python` command doesn't exist on macOS (only `python3`) | Use full path to `uv` or `python3` via `which uv` |
| Claude Desktop can't find `uv` or `python3` | Claude Desktop doesn't inherit your shell's PATH | Always use **full absolute paths** in the config |
| `hatchling` build error during `uv sync` | Missing `[tool.hatch.build.targets.wheel]` in `pyproject.toml` | Already fixed — ensure `packages = ["mcp_server", "insurance_engine", "api"]` is present |
| Config file can't be found via terminal | `Application Support` has a space in the path | Quote the path: `open "$HOME/Library/Application Support/Claude/..."` |

## Section 6: Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test files
pytest tests/test_mcp_tools.py -v      # MCP tool edge cases
pytest tests/test_classifier.py -v     # Classification logic
pytest tests/test_pricing.py -v        # Premium calculations
pytest tests/test_ab_testing.py -v     # A/B framework
pytest tests/test_cart_resolver.py -v  # Multi-cart logic
pytest tests/test_copy_quality.py -v   # Copy generation rules

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html
```

### What Each Test File Covers

| File | Coverage |
| ---- | -------- |
| `test_mcp_tools.py` | All 12 edge cases from blueprint + tool validation |
| `test_classifier.py` | Rule-based classification, fallback logic, confidence scores |
| `test_pricing.py` | Premium formula, floor/cap bounds, risk multipliers |
| `test_ab_testing.py` | Deterministic variants, impression recording, conversion tracking |
| `test_cart_resolver.py` | Waterfall logic, deduplication, multi-cart scenarios |
| `test_copy_quality.py` | Prompt structure, forbidden words, character limits |

## Section 7: What I Would Do Differently

### Real-Time Premium API

Currently, premiums are calculated using a static formula. In production, I would integrate with actual insurance provider APIs (like Digit or Acko) for real-time quotes, dynamic pricing based on claims history, and regulatory-compliant policy generation.

### Embedding-Based Classification

The rule-based classifier works well for known categories but requires manual updates for new product types. A production system would use embeddings (e.g., OpenAI's text-embedding-3-small or Claude's embeddings) to classify deals based on semantic similarity to past successful insurance matches.

### Redis for A/B Testing at Scale

SQLite works for demos but wouldn't handle thousands of concurrent sessions. Redis Streams would provide sub-millisecond event recording with built-in TTL for session expiry and pub/sub for real-time dashboard updates.

### Server-Sent Events for Live Conversion Updates

The dashboard currently polls for updates. SSE or WebSocket connections would push conversion events to all open dashboards instantly, enabling real-time A/B monitoring during high-traffic campaigns.

### Internationalization

All copy is currently in English with Rs for currency. Production would need full i18n support for regional languages (Hindi, Tamil, Telugu) and proper number formatting for Indian locale conventions.

### Fraud Detection

No validation exists for suspicious patterns (same user converting multiple times, unusual session lengths). Production would need anomaly detection on the A/B event stream to flag potential gaming of the system.

---

Built for the GrabOn VibeCoder Challenge 2025 by Saketh T.
