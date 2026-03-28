# 🎯 Media Analyst Agent

> An autonomous AI agent that acts as a Junior Media Analyst for e-commerce teams — understanding natural language questions, querying BigQuery in real time, and delivering actionable insights.

---

## 📌 Overview

Media and growth teams spend too much time manually crossing traffic data with sales data to understand the real ROI of each channel. This MVP solves that by exposing a conversational API backed by a ReAct agent that decides autonomously which data to fetch and how to interpret it.

**Example interactions:**
- *"How did the Search channel perform last month?"*
- *"Which channel has the best conversion rate and why?"*
- *"Show me revenue by channel for the last 7 days."*

---

## 🏗️ Architecture

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
        ┌────────┴────────┐
        ▼                 ▼                  ▼
 get_traffic_volume  get_revenue_by_channel  get_channel_comparison
        │                 │                  │
        └────────┬─────────────────────────-─┘
                 │
                 ▼
        ┌─────────────────┐
        │  BigQueryService │  ← bigquery_service.py: executes parameterized SQL
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

## 🛠️ Tools

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

**Example trigger:** *"Which channel has the best ROI?"*

---

## 🚀 Setup

### Prerequisites

- Python 3.10+
- A Google Cloud account (free tier works) with access to BigQuery
- An Anthropic API key ([get one here](https://console.anthropic.com/))

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/media-analyst-agent.git
cd media-analyst-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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
5. Create a service account with the role `BigQuery Job User`
6. Download the JSON key file
7. Save it somewhere safe (e.g., `credentials/gcp_key.json`)

### 5. Configure environment variables

Create a `.env` file at the root of the project:

```env
ANTHROPIC_API_KEY=sk-ant-...
BQ_PROJECT_ID=your-gcp-project-id
BQ_CREDENTIALS_PATH=credentials/gcp_key.json
```

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `BQ_PROJECT_ID` | The GCP project ID that will **run** the BigQuery jobs (billing target) |
| `BQ_CREDENTIALS_PATH` | Path to the service account JSON key file |

> ⚠️ The `BQ_PROJECT_ID` is the project that **executes** the queries, not the dataset's project (`bigquery-public-data`). Querying public datasets is free within the free tier quota.

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## 📡 API Usage

### `POST /api/v1/chat`

**Request:**
```json
{
  "message": "Which channel had the highest revenue last month?"
}
```

**Response:**
```json
{
  "response": "Based on the last 30 days, **Search** led all channels with $142,300 in revenue across 1,820 orders (avg $78.18/order). Email had the highest average order value at $91.40, suggesting a higher-intent audience. I'd recommend increasing budget allocation toward Search while testing higher-value offers through Email.",
  "tool_used": "get_revenue_by_channel"
}
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   └── routes.py            # HTTP route definitions
│   ├── agent/
│   │   ├── agent.py             # LangGraph ReAct agent setup
│   │   └── tools.py             # Tool definitions (LangChain @tool)
│   ├── services/
│   │   └── bigquery_service.py  # BigQuery client and SQL queries
│   ├── schemas/
│   │   ├── chat.py              # ChatRequest / ChatResponse models
│   │   └── query.py             # Tool parameter models
│   ├── prompts/
│   │   └── system_prompt.py     # Agent system prompt
│   └── core/
│       └── config.py            # Settings via pydantic-settings
├── credentials/                 # ← put your GCP key here (gitignored)
├── .env                         # ← environment variables (gitignored)
├── requirements.txt
└── README.md
```

---

## 📦 Dependencies

Key packages used:

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `langchain-anthropic` | Anthropic LLM integration for LangChain |
| `langgraph` | ReAct agent orchestration |
| `langchain-core` | Tool decorators and base abstractions |
| `google-cloud-bigquery` | Official BigQuery Python client |
| `pydantic` / `pydantic-settings` | Data validation and config management |

---

## 🔒 Security Notes

- All SQL queries use **parameterized inputs** (`ScalarQueryParameter`) — no raw string interpolation.
- The `.env` file and `credentials/` directory should be added to `.gitignore` and never committed.
- The service account only needs `BigQuery Job User` — no write permissions required.

---

## 💡 Design Decisions & Trade-offs

**Why LangGraph over a plain LangChain chain?**
LangGraph's `create_react_agent` gives the model a proper reasoning loop with observation steps. This means it can handle multi-step questions or rephrase a follow-up query if the first tool call doesn't fully answer the user's intent — rather than blindly executing a single chain.

**Why three separate tools instead of one?**
Each tool has a focused purpose, which helps the model make better routing decisions. A single "query everything" tool would produce noisier results and make the agent's tool selection less reliable.

**Why not stream the response?**
The MVP keeps things simple with a synchronous response. Streaming can be added via LangGraph's `astream_events` and FastAPI's `StreamingResponse` as a next step.

---

## 🗺️ Possible Next Steps

- [ ] Add conversation memory (multi-turn support)
- [ ] Streaming responses via Server-Sent Events
- [ ] Date range parameters exposed to the user naturally ("last week", "Q1", etc.)
- [ ] Add a `get_top_products_by_channel` tool for deeper SKU-level insights
- [ ] Dockerize for easy deployment
- [ ] Add evaluation tests with LangSmith