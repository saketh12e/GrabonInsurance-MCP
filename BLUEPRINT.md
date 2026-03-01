# GrabInsurance MCP — Project Blueprint
>
> GrabOn VibeCoder Challenge 2025 | Project 02 | Contextual Embedded Insurance at Deal Redemption
> Author: Saketh T | Status: Ready for Claude Code / Antigravity

---

## Skills Loaded for This Build

These skills are pre-installed and Claude must consult them whenever relevant:

- mcp-builder via `npx skills add https://github.com/anthropics/skills --skill mcp-builder`
  Use for: MCP server design, tool schema, resource/prompt primitives, stdio transport setup
- async-python-patterns via `npx skills add https://github.com/wshobson/agents --skill async-python-patterns`
  Use for: All FastAPI routes, async def patterns, asyncio.gather for concurrent API calls, non-blocking SQLite
- fastapi-python via `npx skills add https://github.com/mindrally/skills --skill fastapi-python`
  Use for: API bridge structure, Pydantic v2 models, RORO pattern, lifespan context, HTTPException
- MCP Integration via `npx skills add https://github.com/anthropics/claude-code --skill 'MCP Integration'`
  Use for: Claude Desktop config wiring, tool registration, MCP client connection testing

When Claude encounters ambiguity in any of these domains, it must re-read the relevant skill before proceeding.

---

## 1. What We Are Building — Plain English

GrabOn is India's #1 coupon platform. When a user redeems a deal — say a Goa flight for Rs 12,400 — we want to show them a single, relevant insurance offer at that exact moment. Not a popup. Not a generic ad. A card that says: "Your Rs 12,400 Goa trip. Protect it for Rs 89."

This system has four jobs:

First, it reads the deal the user just activated (merchant, category, deal value, user history) and classifies what kind of insurance makes sense — this is the intent classifier.

Second, it picks the best 1-2 products from an 8-product catalog and calculates the premium based on the deal value and user risk tier.

Third, it asks Claude to write a personalized, specific insurance offer string — not generic copy, but copy that mentions the actual destination, actual amount, actual premium.

Fourth, it runs A/B tests automatically — every user session gets one of three copy variants (urgency, value, social proof), and the system tracks which one converts better.

The whole system is exposed as an MCP server so Claude Desktop can call it directly. The frontend is a React insurance storefront that GrabOn could embed at checkout.

---

## 2. Business Rules That Must Be Enforced

- Never show an insurance offer if deal_value is below Rs 200 — not worth the friction
- Never show more than 2 insurance products simultaneously regardless of cart size
- Travel insurance always wins in a multi-category cart — it has the highest intent signal
- Electronics cover is only relevant for items above Rs 5,000
- Every copy string must mention the rupee amount of the deal and the premium — no vague language
- Copy must stay under 120 characters for the storefront card
- Premium must never be below Rs 19 or above Rs 499 regardless of formula output

---

## 3. Technology Stack

Layer | Technology | Reason
MCP Server | Python 3.11 with mcp[cli] FastMCP | Official Anthropic SDK, stdio transport for Claude Desktop
Intent Engine | Claude claude-3-5-sonnet-20241022 | Structured JSON output mode for classification
Copy Generation | Claude claude-3-5-sonnet-20241022 | Few-shot prompted for personalized strings
Pricing API | FastAPI async on port 8001 | Lightweight mock insurer pricing service
A/B Framework | Python with aiosqlite | Session-based, async-safe, conversion event log
API Bridge | FastAPI async on port 8000 | CORS-enabled bridge between React and MCP logic
Frontend | React 18 with TailwindCSS and Vite | Insurance storefront, polished for partner demo
Data Models | Pydantic v2 throughout | All inputs and outputs validated at every boundary
Package Manager | uv preferred, pip acceptable | pyproject.toml for Python, package.json for React
Testing | pytest with pytest-asyncio | Full async test coverage including all edge cases

---

## 4. Complete Folder Structure

grabinsurance-mcp/
├── CLAUDE.md
├── blueprint.md
├── pyproject.toml
├── .env.example
├── .env
├── package.json
├── README.md
├── claude_desktop_config_example.json
│
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tools.py
│   ├── resources.py
│   ├── prompts.py
│   └── schemas.py
│
├── insurance_engine/
│   ├── __init__.py
│   ├── catalog.py
│   ├── classifier.py
│   ├── pricing.py
│   ├── ab_testing.py
│   └── cart_resolver.py
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── pricing_api.py
│   └── routes/
│       ├── __init__.py
│       ├── deals.py
│       ├── insurance.py
│       └── ab_events.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       └── components/
│           ├── InsuranceStorefront.jsx
│           ├── DealCard.jsx
│           ├── InsuranceOfferCard.jsx
│           ├── ABVariantRenderer.jsx
│           ├── ConversionDashboard.jsx
│           └── CartScenarioDemo.jsx
│
├── data/
│   ├── insurance_catalog.json
│   ├── mock_deals.json
│   └── mock_users.json
│
└── tests/
    ├── conftest.py
    ├── test_mcp_tools.py
    ├── test_classifier.py
    ├── test_pricing.py
    ├── test_ab_testing.py
    ├── test_cart_resolver.py
    └── test_copy_quality.py

---

## 5. Environment Variables

File: .env.example

ANTHROPIC_API_KEY=your-api-key-here
MCP_SERVER_NAME=GrabInsurance
AB_DB_PATH=./data/ab_events.db
CATALOG_PATH=./data/insurance_catalog.json
DEALS_PATH=./data/mock_deals.json
USERS_PATH=./data/mock_users.json
PRICING_API_URL=<http://localhost:8001>
API_BRIDGE_URL=<http://localhost:8000>

---

## 6. MCP Server Specification

### Transport and Entry

The server must use stdio transport. It must start cleanly with: python mcp_server/server.py
It must be connectable to Claude Desktop using the config in claude_desktop_config_example.json.
This will be tested live during evaluation — it is not optional.

### server.py Structure

Import FastMCP from mcp.server.fastmcp.
Create instance: mcp = FastMCP("GrabInsurance", description="Contextual embedded insurance at deal redemption")
Register tools using @mcp.tool() decorator: classify_intent and get_premium_quote
Register resource using @mcp.resource("insurance://catalog") decorator: get_insurance_catalog
Register prompt using @mcp.prompt() decorator: generate_insurance_copy_prompt
Entry: if __name__ == "__main__": mcp.run(transport="stdio")

### MCP Tool 1: classify_intent

Purpose: Takes a deal object and returns the top 2 insurance products with confidence scores.

Inputs:

- merchant (str): merchant name e.g. "IndiGo", "Samsung", "Zomato"
- category (str): one of travel, electronics, food, health, fashion
- subcategory (str): flight, hotel, gadget, phone, delivery, pharmacy, etc.
- deal_value (float): deal amount in INR
- user_history (dict): keys are total_purchases (int), categories_bought (list of str), risk_tier (str: low/medium/high)

Outputs (as Pydantic ClassificationResult):

- top_products (list of InsuranceMatch, max 2): each has product_id, product_name, confidence (0.0-1.0), reason (1 sentence)
- cart_context (str): "single", "multi", or "ambiguous"
- show_offer (bool): False if deal_value < 200, True otherwise
- fallback_used (bool): True if Claude API timed out and rules were used instead

Classification Logic (Rule-Based First, Claude Fallback Second):

- travel + flight subcategory → TRVL_CANCEL (confidence 0.92), TRVL_MED if deal_value > 8000 (confidence 0.75)
- travel + hotel subcategory → TRVL_RETURN (confidence 0.85), TRVL_CANCEL (confidence 0.65)
- travel + international subcategory → TRVL_MED (confidence 0.95), TRVL_CANCEL (confidence 0.88)
- electronics + phone or tablet → ELEC_SCREEN (confidence 0.90), ELEC_WARRANTY if deal_value > 5000 (confidence 0.85)
- electronics + laptop or tv or gadget → ELEC_WARRANTY (confidence 0.90), PURCHASE_PROTECT (confidence 0.60)
- food + delivery → FOOD_ACCIDENT (confidence 0.70), PURCHASE_PROTECT (confidence 0.45)
- health + pharmacy or clinic → HEALTH_OPD (confidence 0.88), PURCHASE_PROTECT (confidence 0.55)
- fashion (any) → PURCHASE_PROTECT (confidence 0.40) — low confidence, always flag as fallback

If category is not in known list OR confidence of best match is below 0.35, call Claude API with the deal object and the catalog loaded from insurance://catalog resource. If Claude API times out (5 second timeout), use rule-based result and set fallback_used = True.

### MCP Tool 2: get_premium_quote

Purpose: Returns a premium quote for a given product, deal value, and risk tier.

Inputs:

- product_id (str): must match an id in insurance_catalog.json
- deal_value (float): INR amount
- risk_tier (str): "low", "medium", or "high"

Outputs (as Pydantic PremiumQuote):

- premium_inr (float): calculated premium, floored at 19, capped at 499
- coverage_inr (float): deal_value multiplied by product coverage_multiplier divided by 100
- validity_days (int): standard 30 days
- policy_type (str): from product catalog

Premium Formula:
risk_multipliers = {"low": 0.8, "medium": 1.0, "high": 1.4}
base = product.base_premium_rate multiplied by deal_value
premium = base multiplied by risk_multipliers[risk_tier]
final = max(19, min(499, round(premium, 0)))

### MCP Resource: insurance://catalog

Returns the full contents of data/insurance_catalog.json as a formatted string.
Claude loads this before any classification to have full product context in memory.

### MCP Prompt: generate_insurance_copy_prompt

Arguments: product_name, deal_description, premium_inr, variant ("urgency" | "value" | "social_proof")
Returns: A message list (user role) that instructs Claude to generate one copy string under 120 characters.

The prompt must include these hard rules for Claude:

- Always mention the deal amount in INR explicitly
- Always mention the premium in INR explicitly
- Never use the words: "Buy", "Purchase", "Get protected", "Insurance available"
- Variant urgency: use time pressure or loss framing
- Variant value: use coverage ratio math (Xratio times your premium)
- Variant social_proof: mention how many users protected similar deals

The prompt must include three few-shot examples:
BAD: "Buy Travel Insurance for your trip" — GOOD: "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89."
BAD: "Electronics warranty available" — GOOD: "Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499."
BAD: "Health cover for your purchase" — GOOD: "Healthkart order protected 30 days. Theft, damage, non-delivery. Rs 31."

---

## 7. Insurance Product Catalog — All 8 Products

Build this in data/insurance_catalog.json as a JSON array. Each product has these fields:
id, name, category_triggers (list), subcategory_triggers (list, use * for wildcard), base_premium_rate (float), coverage_multiplier (int), description (str)

Product 1: id=TRVL_CANCEL, name=Travel Cancellation Cover
  category_triggers: [travel], subcategory_triggers: [flight, train, bus]
  base_premium_rate: 0.007, coverage_multiplier: 100
  description: Covers trip cancellation due to illness, weather, or airline fault

Product 2: id=TRVL_MED, name=Travel Medical Cover
  category_triggers: [travel], subcategory_triggers: [flight, international]
  base_premium_rate: 0.005, coverage_multiplier: 200
  description: Medical expenses abroad or during travel

Product 3: id=ELEC_WARRANTY, name=Electronics Extended Warranty
  category_triggers: [electronics], subcategory_triggers: [laptop, gadget, tv]
  base_premium_rate: 0.03, coverage_multiplier: 50
  description: Extends manufacturer warranty by 1 year

Product 4: id=ELEC_SCREEN, name=Screen Damage Cover
  category_triggers: [electronics], subcategory_triggers: [phone, tablet]
  base_premium_rate: 0.02, coverage_multiplier: 40
  description: Single accidental screen damage repair covered once

Product 5: id=FOOD_ACCIDENT, name=Personal Accident Cover Food Delivery
  category_triggers: [food], subcategory_triggers: [delivery]
  base_premium_rate: 0.001, coverage_multiplier: 5000
  description: Accidental injury coverage during food delivery interaction

Product 6: id=HEALTH_OPD, name=Health OPD Cover
  category_triggers: [health], subcategory_triggers: [pharmacy, clinic, diagnostics]
  base_premium_rate: 0.015, coverage_multiplier: 30
  description: Outpatient doctor visit and medicine coverage

Product 7: id=TRVL_RETURN, name=Return Journey Protection
  category_triggers: [travel], subcategory_triggers: [hotel, bus, train]
  base_premium_rate: 0.004, coverage_multiplier: 80
  description: Covers missed or cancelled return journey

Product 8: id=PURCHASE_PROTECT, name=Purchase Protection
  category_triggers: [electronics, fashion, health], subcategory_triggers: [*]
  base_premium_rate: 0.01, coverage_multiplier: 20
  description: 30-day coverage against theft, damage, or non-delivery. Universal fallback product.

---

## 8. Mock Deal Scenarios — All 10 Required

Build in data/mock_deals.json. These must match exactly so tests can reference them by deal_id.

Deal 1: deal_id=D001, merchant=IndiGo, category=travel, subcategory=flight, deal_value=12400
  user_history: risk_tier=medium, total_purchases=18
  Expected: TRVL_CANCEL + TRVL_MED, show_offer=true, cart_context=single

Deal 2: deal_id=D002, merchant=Boat, category=electronics, subcategory=gadget, deal_value=2999
  user_history: risk_tier=low, total_purchases=5
  Expected: ELEC_WARRANTY only (deal_value under 5000 threshold for screen cover), show_offer=true

Deal 3: deal_id=D003, merchant=Zomato, category=food, subcategory=subscription, deal_value=1499
  user_history: risk_tier=medium, total_purchases=42
  Expected: FOOD_ACCIDENT with low confidence, show_offer=true (value above 200), note ambiguous subcategory

Deal 4: deal_id=D004, merchant=MakeMyTrip, category=travel, subcategory=hotel, deal_value=8500
  user_history: risk_tier=medium, total_purchases=9
  Expected: TRVL_RETURN + TRVL_CANCEL, cart_context=single

Deal 5: deal_id=D005, merchant=Nykaa, category=health, subcategory=pharmacy, deal_value=499
  user_history: risk_tier=low, total_purchases=3
  Expected: HEALTH_OPD (low deal value but above 200 threshold), show_offer=true

Deal 6: deal_id=D006, merchant=Samsung, category=electronics, subcategory=phone, deal_value=74999
  user_history: risk_tier=high, total_purchases=2
  Expected: ELEC_SCREEN + ELEC_WARRANTY (deal_value well above 5000), both shown

Deal 7: deal_id=D007, merchant=CART:Myntra+MakeMyTrip, category=MULTI, subcategory=MULTI
  cart_items: [Myntra kurta Rs 1800 fashion/apparel, MakeMyTrip flight Rs 9600 travel/flight]
  user_history: risk_tier=medium, total_purchases=14
  Expected: Travel wins per waterfall rule, show TRVL_CANCEL for flight deal, cart_context=multi

Deal 8: deal_id=D008, merchant=CART:Swiggy+Healthkart, category=MULTI, subcategory=MULTI
  cart_items: [Swiggy order Rs 400 food/delivery, Healthkart vitamins Rs 2100 health/supplement]
  user_history: risk_tier=low, total_purchases=31
  Expected: Show HEALTH_OPD (higher deal value wins between food and health), cart_context=multi

Deal 9: deal_id=D009, merchant=Puma, category=fashion, subcategory=sports, deal_value=5500
  user_history: risk_tier=medium, total_purchases=7
  Expected: PURCHASE_PROTECT as fallback, confidence=0.40, fallback_used=true, ambiguous category

Deal 10: deal_id=D010, merchant=AirAsia, category=travel, subcategory=international, deal_value=31000
  user_history: risk_tier=medium, total_purchases=22
  Expected: TRVL_MED wins (international), TRVL_CANCEL second, both shown, high value path

---

## 9. A/B Testing Framework Specification

### Variant Assignment

Deterministic assignment using: variant_index = hash(session_id + product_id) modulo 3
Map index 0 to "urgency", 1 to "value", 2 to "social_proof"
This ensures the same session always gets the same variant — stable for tracking.

### SQLite Schema

Table name: ab_sessions
Columns:

- session_id TEXT PRIMARY KEY
- deal_id TEXT NOT NULL
- user_id TEXT NOT NULL
- variant TEXT NOT NULL — one of urgency, value, social_proof
- product_id TEXT NOT NULL
- copy_string TEXT NOT NULL
- shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- converted INTEGER DEFAULT 0
- converted_at TIMESTAMP

The database file must auto-initialize if it does not exist.
Use aiosqlite for all database operations (async, non-blocking).

### Conversion Tracking

A conversion event fires when the user clicks the "Get Covered" button on the frontend.
The frontend sends POST /api/ab-events/convert with body: session_id, product_id.
The API updates converted=1 and converted_at=now() in the ab_sessions table.

### Dashboard Metrics

The ConversionDashboard component must show a table with these columns:
Variant | Impressions | Conversions | CVR% | Best Performing (highlighted row)

---

## 10. Multi-Category Cart Resolution Logic — cart_resolver.py

Apply this exact waterfall when cart_context is "multi":

Step 1: If travel exists in any cart item → travel insurance always takes the primary slot
Step 2: If electronics item has deal_value above 5000 → electronics cover takes the second slot
Step 3: If no travel and no qualifying electronics → pick top 2 products by confidence score
Step 4: If 3 or more categories and no clear winner → show top 2 by confidence, add note "3 more options available"
Step 5: Final rule — never return more than 2 products regardless of cart size

For Deal 7 (fashion + travel): Step 1 fires → show TRVL_CANCEL for the flight portion, fashion is ignored
For Deal 8 (food + health): Steps 1 and 2 do not fire → Step 3 applies, HEALTH_OPD wins by value

---

## 11. All Edge Cases — Must All Pass in Tests

Edge case 1: deal_value below 200
  Input: deal_value = 150
  Expected: return show_offer=false, reason="deal_value_below_threshold", no products returned

Edge case 2: deal_value is 0 or null
  Input: deal_value = 0 or deal_value = None
  Expected: raise HTTPException 400, message="invalid_deal_value"

Edge case 3: category not recognized
  Input: category = "automotive"
  Expected: trigger Claude fallback, if Claude also returns no match then return PURCHASE_PROTECT with confidence 0.3

Edge case 4: user_history is empty dict
  Input: user_history = {}
  Expected: assign risk_tier = "medium" as default, proceed normally, do not raise error

Edge case 5: subcategory not in known list
  Input: subcategory = "gaming-chair"
  Expected: use category-level matching only, log unrecognized subcategory to stderr, continue

Edge case 6: multi-cart with same category twice
  Input: cart has two travel deals
  Expected: deduplicate by keeping the higher deal_value item, treat as single travel deal

Edge case 7: premium formula output below floor
  Input: deal_value = 210, base_premium_rate = 0.001, risk_tier = "low"
  Expected: premium returned is 19 (floor), never below

Edge case 8: Claude API timeout during fallback
  Input: simulate 6+ second response from Claude
  Expected: fallback_used = true, rule-based classification returned, no exception raised

Edge case 9: unknown merchant name
  Input: merchant = "SomeRandomBrand2025"
  Expected: use category name in copy instead ("your travel deal"), do not crash

Edge case 10: A/B session sees all 3 variants already
  Input: session has already been assigned all 3 variants in prior requests
  Expected: rotate back to variant index 0, log event_type = "repeat_exposure" in ab_sessions

---

## 12. Copy Generation Rules — Claude Must Follow These

Rule 1: Always include the deal amount in INR — write "your Rs 12,400 Goa trip" not "your trip"
Rule 2: Always include the premium amount — write "for Rs 89" not "for a small fee"
Rule 3: Maximum 120 characters for the storefront card copy string
Rule 4: Urgency variant — use time pressure, scarcity, or loss aversion framing
Rule 5: Value variant — use coverage ratio math, "your Rs 89 buys Rs 12,400 protection"
Rule 6: Social proof variant — "4,200 travelers protected similar trips last month"
Rule 7: Never use these words: "Buy", "Purchase", "Get protected today", "Insurance available"
Rule 8: When merchant name is known, include destination or product name in copy
Rule 9: All copy must be in English. Do not mix languages in the copy string.

Few-shot examples that MUST be included in the prompt template:
BAD: "Buy Travel Insurance for your trip"
GOOD: "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89."

BAD: "Electronics warranty available"
GOOD: "Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499."

BAD: "Health cover for your purchase"
GOOD: "Healthkart order protected 30 days. Theft, damage, non-delivery. Rs 31."

BAD: "Personal accident insurance"
GOOD: "Swiggy delivery order? Rs 19 covers accidental harm during your meal."

---

## 13. Frontend Component Specifications

InsuranceStorefront.jsx — main wrapper, two-column layout, left is DealCard, right is InsuranceOfferCard, bottom is ConversionDashboard, tab row to switch between CartScenarioDemo and standard view

DealCard.jsx — shows merchant name (large), category chip (colored badge), deal value in green, subcategory in small text, a placeholder square for merchant logo

InsuranceOfferCard.jsx — shows product name, the generated copy string (largest text, bold), premium amount in orange, coverage amount in small text below, a full-width orange CTA button labeled "Get Covered for Rs [premium]", clicking fires the conversion event

ABVariantRenderer.jsx — small label showing which variant is active (urgency / value / social_proof), used inside InsuranceOfferCard

ConversionDashboard.jsx — table showing variant, impressions, conversions, CVR%, highlight the row with best CVR in light green

CartScenarioDemo.jsx — dropdown of all 10 deal IDs, selecting one loads that deal into DealCard and re-runs classification, shows cart_context badge (single/multi/ambiguous) next to deal title

Design tokens — primary color #FF6B2B (GrabOn orange), background #F8F9FA, cards white with shadow-md rounded-2xl, font Inter or system-ui, CTA button full-width orange with white text

---

## 14. API Routes Reference

FastAPI Bridge on port 8000:

POST /api/classify — body: DealObject → response: ClassificationResult
POST /api/quote — body: QuoteRequest (product_id, deal_value, risk_tier) → response: PremiumQuote
POST /api/generate-copy — body: CopyRequest (product_id, deal_description, premium_inr, variant) → response: CopyResponse (copy_string, variant, session_id)
POST /api/ab-events/convert — body: ConvertRequest (session_id, product_id) → response: ConvertResponse (success, converted_at)
GET /api/ab-events/dashboard — response: DashboardData (list of VariantStats)
GET /api/catalog — response: full insurance catalog array
GET /api/deals — response: all 10 mock deals

Mock Pricing API on port 8001:

POST /pricing/quote — body: (product_id, deal_value, risk_tier) → response: (premium_inr, coverage_inr, validity_days)
GET /pricing/products — response: simplified product list with pricing metadata

---

## 15. Claude Desktop Config

File: claude_desktop_config_example.json

The JSON must have a top-level key "mcpServers" containing a key "grabinsurance".
The grabinsurance entry needs command set to "python", args set to a list with the absolute path to mcp_server/server.py, and env containing ANTHROPIC_API_KEY.

Include a comment in README.md explaining the evaluator must replace /ABSOLUTE/PATH/TO/ with their local path.

---

## 16. CLAUDE.md Content

This file tells future Claude Code sessions how to work on this project.

It must include:

- Project purpose in 3 sentences
- How to start all services (MCP server, API bridge, pricing API, frontend)
- Where the data files are and what they contain
- Which skill to consult for which task (mcp-builder for server changes, async-python-patterns for any new async code, fastapi-python for new routes)
- The test command and what green means
- Known constraints: ports 8000, 8001, 5173 must not conflict; SQLite is async-only via aiosqlite; all Pydantic models are v2

---

## 17. README.md Must Include These Seven Sections

Section 1: What I Built — 2 paragraphs, explain the GrabInsurance concept and the MCP architecture
Section 2: Architecture Diagram — ASCII showing React → FastAPI → MCP Server → Claude API, with SQLite on the side for A/B
Section 3: Key Architecture Decisions — why MCP over REST for Claude integration, why SQLite over Redis for demo scope, why FastMCP over raw MCP SDK
Section 4: How to Run Locally — step by step assuming a fresh machine with Python 3.11 and Node 18
Section 5: How to Connect to Claude Desktop — reference claude_desktop_config_example.json, explain the hammer icon test
Section 6: Running Tests — command is: pytest tests/ -v, explain what each test file covers
Section 7: What I Would Do Differently — be specific and honest, evaluators respect this section

---

## 18. Definition of Done — All Must Be True Before Submitting

- pytest tests/ -v passes with zero failures including all edge case tests
- python mcp_server/server.py starts without any ImportError or missing dependency
- MCP server responds correctly when Claude Desktop calls classify_intent via natural language
- cd frontend && npm install && npm run dev starts on port 5173 without errors
- All 10 deal scenarios return correctly classified insurance products matching expected outputs
- A/B dashboard shows 3 distinct variants with different copy strings per product
- Deal 7 (multi-cart: fashion + travel) shows only travel insurance per waterfall rule
- Deal 8 (multi-cart: food + health) shows HEALTH_OPD per higher-value rule
- Edge case: deal_value = 0 returns HTTP 400 without crashing
- Edge case: unknown subcategory logs to stderr and continues without exception
- README.md is complete, deployable instructions work on a clean machine
- claude_desktop_config_example.json is present and documented
