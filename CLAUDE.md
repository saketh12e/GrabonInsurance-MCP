# CLAUDE.md - GrabInsurance MCP Project Guide

## Project Purpose

GrabInsurance MCP is a contextual embedded insurance system for GrabOn, India's #1 coupon platform. When a user redeems a deal, the system analyzes the deal context (merchant, category, value, user history) and presents a personalized insurance offer at the moment of maximum intent. The system is exposed as an MCP server, allowing Claude Desktop to interact with it directly.

## How to Start All Services

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (recommended) or pip

### 1. Install Python Dependencies
```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### 2. Set Up Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Start the MCP Server (for Claude Desktop)
```bash
python mcp_server/server.py
```

### 4. Start the API Bridge (port 8000)
```bash
uvicorn api.main:app --port 8000 --reload
```

### 5. Start the Pricing API (port 8001)
```bash
uvicorn api.pricing_api:app --port 8001 --reload
```

### 6. Start the Frontend (port 5173)
```bash
cd frontend
npm install
npm run dev
```

## Data Files

| File | Location | Description |
|------|----------|-------------|
| Insurance Catalog | `data/insurance_catalog.json` | 8 insurance products with triggers, rates, and coverage |
| Mock Deals | `data/mock_deals.json` | 10 test scenarios including single and multi-cart |
| Mock Users | `data/mock_users.json` | 5 user personas with risk profiles |
| A/B Database | `data/ab_events.db` | SQLite database for A/B test tracking (auto-created) |

## Which Skill to Consult

| Task | Skill |
|------|-------|
| MCP server changes | mcp-builder |
| New async code | async-python-patterns |
| New API routes | fastapi-python |
| Claude Desktop integration | MCP Integration |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mcp_tools.py -v

# Run with coverage
pytest tests/ -v --cov=.
```

**Green means:** All edge cases pass, classification rules work correctly, premium calculations are accurate, A/B testing records properly.

## Known Constraints

- **Ports:** 8000 (API), 8001 (Pricing), 5173 (Frontend) - must not conflict
- **SQLite:** All database operations use aiosqlite for async safety
- **Pydantic:** All models are Pydantic v2 - use `model_dump()` not `dict()`
- **Claude API:** 5-second timeout on all Claude API calls with rule-based fallback
- **Premium bounds:** Floor at Rs 19, cap at Rs 499
- **Copy length:** Maximum 120 characters for storefront display
- **Max products:** Never return more than 2 insurance products
