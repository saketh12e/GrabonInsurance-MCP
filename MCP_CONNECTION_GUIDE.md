# 🔌 Connecting GrabInsurance MCP to Claude Desktop

> Step-by-step guide to register and run your MCP server inside Claude Desktop.

---

## Prerequisites

Before you begin, make sure you have:

- [x] **Claude Desktop** installed — [Download here](https://claude.ai/download)
- [x] **Python 3.11+** installed (system Python or `uv`-managed)
- [x] **uv** installed — [Install uv](https://docs.astral.sh/uv/getting-started/installation/) _(recommended)_
- [x] **All dependencies installed** — `uv sync` or `pip install -e .`
- [x] **Anthropic API key** — from [console.anthropic.com](https://console.anthropic.com)
- [x] The MCP server runs without errors: `uv run python mcp_server/server.py`

---

## Step 1: Locate the Claude Desktop Config File

Claude Desktop stores its MCP server configuration in a JSON file. The location depends on your OS:

| OS      | Config File Path |
|---------|-----------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### On your machine (macOS), the exact path is

```
/Users/saketht/Library/Application Support/Claude/claude_desktop_config.json
```

> [!TIP]
> If this file doesn't exist yet, create it. Claude Desktop will read it on next launch.

---

## Step 2: Get Your Absolute Project Path

Your project lives at:

```
/Users/saketht/Grabon-MCP
```

The MCP server entry point is:

```
/Users/saketht/Grabon-MCP/mcp_server/server.py
```

---

## Step 3: Edit the Config File

Open the Claude Desktop config file and add (or merge) the following JSON.

### Recommended Config (using `uv` — works on all systems)

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
        "ANTHROPIC_API_KEY": "your-actual-api-key-here",
        "CATALOG_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/insurance_catalog.json",
        "AB_DB_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/ab_events.db"
      }
    }
  }
}
```

To find your `uv` path, run:

```bash
which uv
# Example output: /Users/yourname/.local/bin/uv
```

> [!IMPORTANT]
>
> - **Replace `/ABSOLUTE/PATH/TO/`** with your actual paths (run `which uv` and `pwd` inside the project).
> - Replace `your-actual-api-key-here` with your real Anthropic API key.
> - If you already have other MCP servers configured, **merge** the `grabinsurance` entry into the existing `mcpServers` object — do NOT replace the entire file.
> - All paths **must be absolute** (no `~/` or `./` shortcuts).

### Alternative Config (using system Python directly)

If you prefer not to use `uv`, use the full path to `python3`:

```json
{
  "mcpServers": {
    "grabinsurance": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/ABSOLUTE/PATH/TO/Grabon-MCP/mcp_server/server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your-actual-api-key-here",
        "CATALOG_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/insurance_catalog.json",
        "AB_DB_PATH": "/ABSOLUTE/PATH/TO/Grabon-MCP/data/ab_events.db"
      }
    }
  }
}
```

> [!WARNING]
>
> - **Do NOT use just `python`** — macOS often doesn't have a `python` command, only `python3`.
> - **Do NOT use a relative path** like `python3` without the full path — Claude Desktop does not inherit your shell's PATH.
> - Run `which python3` to find the correct full path for your system.

---

## Step 4: Restart Claude Desktop

After saving the config file:

1. **Fully quit** Claude Desktop (Cmd+Q on macOS, not just close the window)
2. **Reopen** Claude Desktop

---

## Step 5: Verify the Connection

Once Claude Desktop restarts, look for the **🔨 hammer icon** (MCP tools indicator) in the chat input area.

1. Click the **🔨 hammer icon** — you should see **GrabInsurance** tools listed:
   - `classify_deal_intent` — Classifies a deal and returns insurance recommendations
   - `get_insurance_quote` — Calculates a premium quote

2. You should also see the **resource** `insurance://catalog` available.

3. **Test it** by typing something like:

   > _"I just booked an IndiGo flight to Goa for Rs 12,400. My risk tier is medium. What insurance do you recommend?"_

   Claude should automatically call the `classify_deal_intent` tool and return insurance product recommendations.

---

## Quick Reference: What Gets Registered

| MCP Primitive | Name | Description |
|--------------|------|-------------|
| **Tool** | `classify_deal_intent` | Classify a deal → top 2 insurance products |
| **Tool** | `get_insurance_quote` | Calculate premium for a specific product |
| **Resource** | `insurance://catalog` | Full 8-product insurance catalog |
| **Prompt** | `generate_copy` | Generate personalized insurance copy (under 120 chars) |

---

## ⚠️ Known Issues & Troubleshooting

These are **real issues** we encountered during setup. If you run into problems, start here.

### Issue 1: `Failed to spawn process: No such file or directory`

**This is the most common issue.** It happens because:

1. **macOS doesn't have a `python` command** — only `python3`. If your config says `"command": "python"`, Claude Desktop will fail.
2. **Claude Desktop does NOT inherit your shell's PATH** — it can't find `python3`, `uv`, or other commands by short name. You must use **full absolute paths**.

**Fix:** Use the full path to `uv` or `python3` in your config:

```bash
# Find your uv path
which uv
# Example: /Users/yourname/.local/bin/uv

# Or find your python3 path
which python3
# Example: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
```

Then update `"command"` in your config to the full path (see Step 3 above).

### Issue 2: `hatchling` build error — "Unable to determine which files to ship"

If you see this when running `uv sync` or `pip install -e .`:

```
ValueError: Unable to determine which files to ship inside the wheel
```

**Fix:** Make sure `pyproject.toml` includes the build target config:

```toml
[tool.hatch.build.targets.wheel]
packages = ["mcp_server", "insurance_engine", "api"]
```

This tells `hatchling` which directories to include. Without it, the build fails because the project name (`grabinsurance-mcp`) doesn't match any directory.

### Issue 3: "Hammer icon not showing"

- ✅ Check config JSON syntax — even a missing comma will break it. Use a JSON validator.
- ✅ Make sure you **fully quit** Claude Desktop (Cmd+Q on macOS) and reopened it — just closing the window is not enough.
- ✅ Check Claude Desktop logs: go to **Help → Diagnostics → View MCP Log** in the menu bar.

### Issue 4: "Server crashes on startup"

Test the server outside of Claude Desktop first:

```bash
# Using uv (recommended)
cd /path/to/Grabon-MCP
uv run python -c "from mcp_server.server import mcp; print('✅ Server loads OK')"

# Or using system python3
python3 -c "from mcp_server.server import mcp; print('✅ Server loads OK')"
```

If it fails with `ModuleNotFoundError`, install dependencies:

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Issue 5: "Tools show but calls fail"

- Check that the `ANTHROPIC_API_KEY` in the config is valid and not expired
- Check that `CATALOG_PATH` points to an existing file (use absolute path)
- Look at Claude Desktop MCP logs: **Help → Diagnostics → View MCP Log**

### Issue 6: Config file path has spaces (macOS)

The Claude Desktop config lives at `~/Library/Application Support/Claude/` — note the space in "Application Support". When navigating via terminal, you must **quote the path** or **escape the space**:

```bash
# ✅ Correct — quoted path
open "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# ✅ Correct — escaped space
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# ❌ Wrong — will fail
open ~/Library/Application Support/Claude/claude_desktop_config.json
```

---

## How It Works Under the Hood

```
┌─────────────────────┐         stdio (stdin/stdout)         ┌──────────────────────────┐
│                     │ ──────────────────────────────────▶  │                          │
│   Claude Desktop    │                                      │  mcp_server/server.py    │
│   (MCP Client)      │ ◀──────────────────────────────────  │  (FastMCP + stdio)       │
│                     │         JSON-RPC messages             │                          │
└─────────────────────┘                                      └──────────────────────────┘
                                                                       │
                                                                       ▼
                                                             ┌──────────────────────────┐
                                                             │  insurance_engine/       │
                                                             │  ├── classifier.py       │
                                                             │  ├── pricing.py          │
                                                             │  ├── ab_testing.py       │
                                                             │  └── cart_resolver.py    │
                                                             └──────────────────────────┘
```

1. Claude Desktop launches `uv run python mcp_server/server.py` as a **child process**
2. Communication happens over **stdio** (stdin/stdout) using **JSON-RPC** messages
3. Claude Desktop discovers the tools, resources, and prompts automatically
4. When a user asks about insurance, Claude calls the tools via MCP and returns results

---

## Quick Commands Cheat Sheet

```bash
# Test server standalone (using uv)
uv run python mcp_server/server.py

# Test server module imports
uv run python -c "from mcp_server.server import mcp; print('✅ Server loads OK')"

# Open the config file (macOS) — note the quotes!
open "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Create config directory if it doesn't exist
mkdir -p "$HOME/Library/Application Support/Claude"

# Find your uv path (needed for config)
which uv

# Find your python3 path (alternative to uv)
which python3

# Verify MCP SDK is installed
uv run python -c "from mcp.server.fastmcp import FastMCP; print('✅ MCP SDK ready')"

# Install all dependencies
uv sync

# Start all services (separate terminals)
# NOTE: MCP Server is auto-launched by Claude Desktop — don't start it manually
uvicorn api.main:app --port 8000 --reload         # API Bridge
uvicorn api.pricing_api:app --port 8001 --reload   # Pricing API
cd frontend && npm install && npm run dev           # Frontend (port 5173)
```
