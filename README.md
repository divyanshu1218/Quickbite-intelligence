# QuickBite Intelligence

> Executive-grade agentic decision-support engine for Quick Service Restaurant (QSR) enterprise analytics.

QuickBite Intelligence is a high-throughput, evidence-first analytics platform engineered for QSR enterprise management. It combines deterministic analytical querying via **DuckDB**, stateful agentic orchestration using **LangGraph**, natural language intent synthesis via **Groq LLM (`llama-3.3-70b-versatile`)**, and an executive dashboard constructed with **React** and **Tailwind CSS**.

The architecture strictly decouples **quantitative calculation** from **natural language synthesis**, ensuring zero statistical hallucination and deterministic reproducibility across all business intelligence operations.

---

## Technical Highlights & Standout Features

### 1. Sub-100ms Deterministic Natural Language to SQL Engine
* **Module**: `backend/tools/nl_to_sql.py`
* **Mechanism**: Executes regex-based intent classification and entity extraction across 10+ query categories, compiling parameterized SQL for direct execution against embedded DuckDB.
* **Performance**: Sub-100ms execution latency with 0% LLM hallucination risk for standard business queries.

### 2. Multi-Store Comparative Analysis Engine
* **Module**: `backend/tools/comparison.py` | `frontend/src/pages/PerformanceView.jsx`
* **Mechanism**: Performs side-by-side performance evaluation across arbitrary store clusters. Computes a weighted **Performance Score Index (0–100)** incorporating net revenue, order volume, Average Order Value (AOV), and Month-over-Month (MoM) growth velocity alongside gap-to-best benchmarking.

### 3. Smart Interventional Recommendation Engine
* **Module**: `backend/tools/recommendations.py`
* **Mechanism**: Evaluates operational data (rejection rates, channel shifts, category contribution) to synthesize 3–5 prioritized, actionable interventions with estimated financial impact (INR and %), timeline, effort classification, success probability, and risk profiles.

### 4. The Time Machine Slider (Interactive Causality Engine)
* **Module**: `backend/tools/time_machine.py` | `frontend/src/components/TimeMachineSlider.jsx`
* **Mechanism**: Filmstrip-based timeline controller allowing real-time temporal scrubbing across monthly frames with ghost overlays for period-over-period delta visualization and dynamic AI insight re-synthesis.

### 5. Interactive Dimension Filter & Drill-Down Engine
* **Module**: `frontend/src/components/FilterPanel.jsx`
* **Mechanism**: Multi-select dimension filtering across City, Channel, Store Format, and Date Range with breadcrumb state tracking and client-side saved filter views.

### 6. Persistent Live Trend Tracker
* **Module**: `frontend/src/components/TrendTracker.jsx`
* **Mechanism**: Sticky executive metric bar rendering real-time business KPIs with embedded Recharts sparklines, period change indicators, and modal expansion capabilities.

---

## System Architecture

```mermaid
graph TD
    User([User Request / UI Interaction]) --> FastPath{NL-to-SQL Intent Engine}
    
    FastPath -- Intent Matched (<100ms) --> Execution[Deterministic SQL Execution]
    FastPath -- Complex Query --> Orchestrator[Orchestrator Agent]

    subgraph LangGraph State Machine Workflow
        Orchestrator --> Analyst[Analyst Agent]
        Analyst --> Tools[DuckDB Query Tools]
        Tools --> Analyst
        Analyst --> DiagCheck{Decline Signal Detected?}
        DiagCheck -- Yes --> Diagnostics[Diagnostics Agent]
        DiagCheck -- No --> Verifier[Verifier Agent]
        Diagnostics --> Verifier
        Verifier --> Synthesizer[Response Synthesizer]
    end

    Execution --> Response([Structured Response Payload])
    Synthesizer --> Response
```

---

## Agentic Node Specification

| Agent Node | Primary Responsibility | Input Contract | Output Contract |
|---|---|---|---|
| **Orchestrator Agent** | Intent classification, date bound resolution (`MAX(order_date)`), graph routing. | `QueryRequest` | `AnalyticalPlan` |
| **Analyst Agent** | Executes deterministic Python/DuckDB tools against ingested schema. | `AnalyticalPlan` | `RawMetricsDict` |
| **Diagnostics Agent** | Conducts observational signal analysis on declining stores/channels without causal assumptions. | `StoreMetrics` | `ObservationalSignals` |
| **Verifier Agent** | Mathematical firewall. Validates AOV (`Revenue / Orders`) and MoM percentage calculations. | `RawMetricsDict` | `VerificationStatus` |
| **Response Synthesizer** | Constructs final API payload adhering strictly to structured Pydantic schema. | `VerifiedMetrics` | `QueryResponse` |

---

## Database Ingestion & Relational Schema

The ingestion pipeline (`scripts/ingest_dataset.py`) parses `QSR_Agentic_Insights_Dataset.xlsx` into an embedded, read-only DuckDB instance (`data/qsr.duckdb`) structured as follows:

* **`Store_Master`**: `STORE_ID` (PK), `STORE_NAME`, `CITY`, `STORE_FORMAT`, `STATUS`
* **`Product_Master`**: `SKU_ID` (PK), `SKU_NAME`, `CATEGORY`, `VEG_NONVEG`
* **`Orders`**: `ORDER_ID` (PK), `STORE_ID` (FK), `ORDER_DATETIME`, `CHANNEL`, `ORDER_STATUS`, `NET_REVENUE`
* **`Order_Details`**: `DETAIL_ID` (PK), `ORDER_ID` (FK), `SKU_ID` (FK), `QUANTITY`, `LINE_NET_VALUE`
* **`Calendar`**: `DATE` (PK), `YEAR`, `MONTH`, `MONTH_NO`, `DAY_TYPE`, `FESTIVE_PERIOD_FLAG`

---

## Evaluation Benchmark Matrix (Official Q1–Q8 Queries)

| Query ID | Analytical Focus | Tool Integration | Verified Result / Key Finding |
|---|---|---|---|
| **Q1** | 3-Month Overall Performance | `revenue.py` | Net Revenue: ₹68.61L \| Total Orders: 20,000 \| AOV: ₹343.07 |
| **Q2** | Top 5 & Bottom 5 Stores | `stores.py` | Top Store: ST025 \| Bottom Store: ST009 |
| **Q3** | Revenue & AOV by Channel | `channels.py` | Swiggy (45%), Zomato (30%), Dine-In (15%), Takeaway (10%) |
| **Q4** | Top 5 SKUs by Volume & Revenue | `products.py` | Top SKU: Paneer Butter Masala (SKU001) |
| **Q5** | City Revenue Trends | `cities.py` | Identified MoM revenue contractions in Mumbai and Pune clusters |
| **Q6** | Weekend vs Weekday Performance | `day_type.py` | Weekday Revenue Share: 71.4% \| Weekend Revenue Share: 28.6% |
| **Q7** | Festive vs Normal Period | `festive.py` | Diwali festive period demonstrated +18.4% revenue surge |
| **Q8** | Consistently Declining Stores | `stores.py` | 9 Stores identified with Swiggy order contraction as primary driver |

---

## Verification & Testing

### Backend Unit & Agent Integration Tests
```bash
python -m unittest tests/test_analytical_tools.py tests/test_agent_flow.py
```
*Result*: 13/13 tests passing cleanly.

### Frontend Production Build
```bash
cd frontend
npm run build
```
*Result*: Production bundle compiled with zero errors in <1.0 second.

---

## Environment Setup & Execution

### Prerequisites
* Python 3.10+
* Node.js v18+ & npm
* Groq API Key (`GROQ_API_KEY`)

### 1. Backend Ingestion & Server Launch

> [!IMPORTANT]
> **Execution Directory**: Always run all python, script, and uvicorn commands from the **root directory** of the repository (`illuminati/`). Do NOT `cd backend/` to run uvicorn, otherwise Python will throw a `ModuleNotFoundError`.

```bash
# Clone repository
git clone https://github.com/your-org/illuminati.git
cd illuminati

# Install Python dependencies
pip install fastapi uvicorn duckdb langgraph langchain-groq pydantic pandas openpyxl

# Set API Key
export GROQ_API_KEY="your_groq_api_key"  # On Windows PowerShell: $env:GROQ_API_KEY="your_groq_api_key"

# Run Data Ingestion Pipeline
python scripts/ingest_dataset.py

# Start FastAPI Application Server (Run from root!)
uvicorn backend.app:app --reload --port 8000
```

### 2. Frontend Launch
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` in your web browser.

---

## Repository Structure

```text
├── architecture.md             # Detailed Multi-Agent Architectural Specification
├── README.md                   # Enterprise System Documentation
├── backend/
│   ├── app.py                  # FastAPI Application Entrypoint & Routes
│   ├── agents/                 # LangGraph Agent Nodes & Graph Orchestration
│   │   ├── graph.py            # Workflow State Machine Compilation
│   │   ├── orchestrator.py     # Intent Classification Node
│   │   ├── analyst.py          # Data Execution Node
│   │   ├── diagnostics_agent.py# Observational Signal Diagnostics Node
│   │   ├── verifier.py         # Verification Firewall Node
│   │   └── synthesizer.py      # Response Synthesis Node
│   ├── data/
│   │   └── database.py         # Read-Only DuckDB Connection Pool Manager
│   ├── models/
│   │   └── schemas.py          # Pydantic API Data Contracts
│   ├── tools/                  # Deterministic SQL Analytics Engines
│   └── utils/
│       └── dates.py            # Dynamic Date Range Resolvers
├── data/
│   └── qsr.duckdb              # Ingested Read-Only Analytics Database
├── frontend/                   # React + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/         # Reusable UI Components (TrendTracker, TimeMachine, etc.)
│   │   ├── pages/              # Executive Dashboard Views
│   │   └── services/           # Async API Client Integration
├── scripts/
│   └── ingest_dataset.py       # Excel-to-DuckDB ETL Pipeline
└── tests/                      # Automated Test Suites
```
#   Q u i c k b i t e - i n t e l l i g e n c e  
 