# Media Analyst Agent

> An autonomous AI agent that acts as a Junior Media Analyst for e-commerce teams — understanding natural language questions, querying BigQuery in real time, and delivering actionable insights.

---

## Quick Example

**Question:**
"Which channel has the best performance?"

**Answer:**
"Search leads in revenue with $142k and a 4.2% conversion rate.
Recommendation: increase budget allocation before peak season."

---

## Overview

Media and growth teams spend too much time manually crossing traffic data with sales data to understand the real performance of each channel. This MVP solves that by exposing a conversational API backed by a ReAct agent that decides autonomously which data to fetch and how to interpret it.

**Language support:**
The agent supports multilingual queries and responds in the same language as the user, enabling seamless interaction in both English and Portuguese.

**Example interactions:**

- *"How did the Search channel perform last month?"*
- *"Which channel has the best conversion rate and why?"*
- *"Show me revenue by channel for the last 7 days."*

---

## Architecture

The agent is built on a **ReAct (Reasoning + Acting)** loop using LangGraph. Instead of a single giant prompt, the LLM autonomously decides which tool to call based on the user's question.

```
User Message (HTTP POST /api/v1/chat)
        │
        ▼
  ┌─────────────┐
  │   FastAPI   │  ← routes.py: receives and validates the request
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────────────────┐
  │     LangGraph ReAct Agent       │  ← agent.py: orchestrates the reasoning loop
  │                                 │
  │  1. Reads the user message      │
  │  2. Decides which tool to call  │
  │  3. Calls the tool              │
  │  4. Interprets the result       │
  │  5. Returns a natural response  │
  └──────────────┬──────────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
get_traffic  get_revenue  get_channel
  _volume    _by_channel  _comparison
        │        │        │
        └────────┼────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ BigQueryService │  ← bigquery_service.py: executes parameterized SQL
        └─────────┬───────┘
                  │
                  ▼
    bigquery-public-data.thelook_ecommerce
```

### Why this architecture?

| Decision | Rationale |
|---|---|
| **LangGraph ReAct** | Gives the agent a reasoning loop (think → act → observe) instead of a single prompt call. The agent chooses tools dynamically based on intent. |
| **Tool Calling** | Each tool is a well-scoped Python function. The LLM never sees raw SQL — it only sees structured results. This separates concerns cleanly. |
| **FastAPI** | Async-ready, automatic OpenAPI docs, and native Pydantic integration for request/response validation. |
| **Pydantic schemas** | `ChatRequest`, `ChatResponse`, `TrafficVolumeParams`, etc. enforce types at every boundary. |
| **Parameterized SQL** | All BigQuery queries use `ScalarQueryParameter` — no string interpolation, no SQL injection risk. |

---

## Tools

The agent has access to three tools. It picks the right one based on the user's intent:

### `get_traffic_volume`

**When:** User asks about visits, user volume, or a specific channel (Search, Organic, Facebook, etc.)

**Query:** Aggregates `COUNT(*)` from the `users` table grouped by `traffic_source`, filtered by a date window.

**Example trigger:** *"How many users came from Email in the last 14 days?"*

---

### `get_revenue_by_channel`

**When:** User asks about revenue, sales, orders, or financial performance.

**Query:** JOINs `users → orders → order_items`, excludes cancelled/returned orders, and returns `total_revenue`, `total_orders`, and `avg_order_value` per channel.

**Example trigger:** *"What was our revenue by channel last month?"*

---

### `get_channel_comparison`

**When:** User wants a full ranking, wants to know which channel performs best, or asks for an overall analysis.

**Query:** A single LEFT JOIN across all three tables that returns `total_users`, `total_orders`, `total_revenue`, `conversion_rate_pct`, and `revenue_per_user` per channel — all in one shot.

**Example trigger:** *"Which channel has the best performance?"*

**Ranking criteria:** Channels are ranked by `revenue_per_user` — the metric that best reflects commercial efficiency, combining both reach (total users) and monetization (revenue). Conversion rate and total revenue are also returned for full context.

---

### Out-of-scope guardrail

If the user asks something outside the media/revenue domain (e.g. *"What's the weather?"*), the agent politely declines without calling any tool.

---

## Project Structure

```
media-analyst-agent/
├── app/
│   ├── agent/
│   │   ├── agent.py             # LangGraph ReAct agent orchestration
│   │   └── tools.py             # 3 BigQuery tools with @tool decorator
│   ├── api/
│   │   └── routes.py            # FastAPI POST /api/v1/chat endpoint
│   ├── core/
│   │   └── config.py            # Pydantic settings (reads from .env)
│   ├── prompts/
│   │   └── system_prompt.py     # System prompt (separated from logic)
│   ├── schemas/
│   │   ├── chat.py              # ChatRequest, ChatResponse
│   │   └── query.py             # Tool input params (Pydantic)
│   └── services/
│       └── bigquery_service.py  # BigQuery client with parameterized queries
├── main.py                      # FastAPI entrypoint
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## Setup

### Prerequisites

- Python 3.10+
- A [Google Cloud](https://console.cloud.google.com) account with BigQuery API enabled
- A GCP Service Account with `BigQuery Data Viewer` and `BigQuery Job User` roles
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone the repository

```bash
git clone https://github.com/anaeggerdemier/media-analyst-agent.git
cd media-analyst-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Google Cloud credentials

This project queries `bigquery-public-data.thelook_ecommerce`, which is publicly available. You only need a GCP service account with BigQuery read permissions.

**Steps:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **BigQuery API**
4. Go to **IAM & Admin → Service Accounts**
5. Create a service account with the roles `BigQuery Data Viewer` and `BigQuery Job User`
6. Download the JSON key file
7. Place it at `app/keys/service_account.json`

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
BQ_PROJECT_ID=your_gcp_project_id
BQ_CREDENTIALS_PATH=app/keys/service_account.json
```

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `BQ_PROJECT_ID` | The GCP project ID that will run the BigQuery jobs (billing target) |
| `BQ_CREDENTIALS_PATH` | Path to the service account JSON key file |

> ⚠️ `BQ_PROJECT_ID` is the project that **executes** the queries, not the dataset's project (`bigquery-public-data`). Querying public datasets is free within the free tier quota.

> ⚠️ Never commit `.env` or `*.json` files. They are already listed in `.gitignore`.

### 6. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`

---

## Usage

### Example requests

**Traffic volume by channel:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How was the volume of users from Search in the last month?"}'
```

**Best performing channel:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which channel has the best performance and why?"}'
```

**Revenue by channel:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What was the revenue per channel in the last 30 days?"}'
```

### Example response

```json
{
  "response": "Based on the last 30 days, Search led all channels with $142,300 in revenue across 1,820 orders (avg $78.18/order). It also has the highest conversion rate at 4.2%, meaning 1 in 24 visitors makes a purchase. Email had the highest average order value at $91.40, suggesting a higher-intent audience. Recommendation: increase budget allocation toward Search while testing higher-value offers through Email.",
  "tool_used": "get_channel_comparison"
}
```

---

## Health check

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok"}
```

---

## Tests

All tests use mocks — no real BigQuery or Anthropic API calls are made.

```bash
pytest tests/ -v
```

### What is covered

| File | What it tests |
|---|---|
| `test_tools.py` | Output format of each tool, empty results, and BigQuery errors |
| `test_bigquery_service.py` | SQL method behavior with mocked query results |
| `test_routes.py` | API endpoints: happy path, validation (422), and error handling (500) |

---

## Dataset

This project uses the public BigQuery dataset [`bigquery-public-data.thelook_ecommerce`](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce), which simulates a clothing e-commerce store.

| Table | Key columns used |
|---|---|
| `users` | `id`, `traffic_source`, `created_at` |
| `orders` | `order_id`, `user_id`, `status`, `created_at` |
| `order_items` | `order_id`, `sale_price` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web framework | FastAPI |
| AI orchestration | LangGraph (ReAct agent) |
| LLM | Claude (Anthropic) via `langchain-anthropic` |
| Data warehouse | Google BigQuery |
| Data validation | Pydantic v2 |
| Configuration | pydantic-settings |

---

## 🔒 Security Notes

- All SQL queries use **parameterized inputs** (`ScalarQueryParameter`) — no raw string interpolation.
- The `.env` file and service account JSON are listed in `.gitignore` and should never be committed.
- The service account only needs `BigQuery Job User` and `BigQuery Data Viewer` — no write permissions required.

---

## 💡 Design Decisions & Trade-offs

**Why LangGraph over a plain LangChain chain?**
LangGraph's `create_react_agent` gives the model a proper reasoning loop with observation steps. This means it can handle multi-step questions or rephrase a follow-up query if the first tool call doesn't fully answer the user's intent — rather than blindly executing a single chain.

**Why three separate tools instead of one?**
Each tool has a focused purpose, which helps the model make better routing decisions. A single "query everything" tool would produce noisier results and make the agent's tool selection less reliable.

**Why not stream the response?**
The MVP keeps things simple with a synchronous response. Streaming can be added via LangGraph's `astream_events` and FastAPI's `StreamingResponse` as a next step.

---

## Possible Next Steps

- [ ] Add conversation memory (multi-turn support)
- [ ] Streaming responses via Server-Sent Events
- [ ] Natural date range parsing ("last week", "Q1", etc.)
- [ ] Add a `get_top_products_by_channel` tool for deeper SKU-level insights
- [ ] Dockerize for easy deployment
- [ ] Add evaluation tests with LangSmith

---

## Author

Ana Caroline Demier
