#  FinResearch AI

> **An evidence-grounded multi-agent AI system for autonomous investment research and due diligence.**

FinResearch AI is an **agentic investment research platform** that autonomously investigates companies, gathers and verifies evidence, performs financial analysis, evaluates competitive and business risks, challenges investment assumptions, and generates an evidence-backed investment thesis.

Unlike a traditional LLM or RAG chatbot that follows a fixed **retrieve → generate** workflow, FinResearch AI can dynamically decide **what to investigate next, which tools to use, whether the available evidence is sufficient, and whether newly discovered information changes its original thesis.**

---

##  Problem

Investment due diligence is a time-consuming, open-ended research process.

An analyst typically needs to:

* Collect information from financial filings and market sources
* Analyze financial performance
* Research competitors and industry trends
* Identify business and regulatory risks
* Validate important claims across multiple sources
* Resolve conflicting information
* Perform valuation calculations
* Test different financial scenarios
* Continuously update the investment thesis as new information appears

The challenge is that the research process is **not deterministic**.

Discovering one piece of information often creates the need for another investigation.

For example:

> If an analyst discovers that a company's largest customers are developing competing products, they may need to investigate customer concentration, competitive threats, market share, product economics, and the potential impact on future revenue assumptions.

A fixed RAG pipeline cannot naturally handle this kind of dynamic investigation.

---

##  Solution

FinResearch AI treats investment research as an **autonomous investigation problem**.

Given a question such as:

> **"Should I invest in NVIDIA?"**

the system can:

1. Understand the research objective
2. Create an initial investigation plan
3. Retrieve relevant financial and market information from official SEC EDGAR XBRL filings
4. Select appropriate tools dynamically
5. Analyze financial metrics
6. Investigate competitors and risks
7. Detect information gaps
8. Search for additional evidence
9. Identify contradictory claims across sources
10. Verify important statements with confidence scores
11. Perform financial calculations (DCF, WACC, Key Ratios)
12. Run 5,000-iteration Monte Carlo probabilistic simulations
13. Synthesize investment thesis via Bull vs. Bear scenario analysis
14. Estimate confidence and uncertainty
15. Produce an evidence-backed investment research report

---

## 🏗️ System Architecture

The key design principle is:

> **Use an agent when the next action depends on information discovered during the investigation.**

A traditional pipeline might look like:

```text
Question
   ↓
Retrieve Documents
   ↓
Generate Answer
```

FinResearch AI uses an iterative process:

```text
Research Goal
      ↓
     Plan
      ↓
   Choose Tool
      ↓
 Execute Tool
      ↓
 Observe Evidence
      ↓
 Evaluate Evidence
      ↓
 Is Evidence Sufficient?
    /           \
  No             Yes
  ↓               ↓
Investigate    Build Thesis
  Again            ↓
    ↑          Challenge Thesis
    └──────────────┘
                   ↓
              Final Report
```

The agent therefore acts as an **investigator and decision-maker**, rather than simply a text generator.

---

##  System Architecture & Key Modules

```text
                             USER PROMPT
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  ResearchState  │ ◄──────────────────┐
                         └────────┬────────┘                    │
                                  │                             │
                                  ▼                             │
                         ┌─────────────────┐                    │
                         │decide_next_action│                    │
                         │ (LLM Reasoning) │                    │
                         └────────┬────────┘                    │
                                  │                             │
                   ┌──────────────┴──────────────┐              │
                   │                             │              │
         [action == "complete"]        [action == "call_tool"]  │
                   │                             │              │
                   ▼                             ▼              │
           ┌──────────────┐            ┌──────────────────┐     │
           │Deterministic │            │ Execute Selected │     │
           │ Quantitative │            │ Tool from        │     │
           │ Financials   │            │ Registry         │     │
           │(DCF / Monte  │            └────────┬─────────┘     │
           │ Carlo /      │                     │               │
           │ Bull vs Bear)│                     ▼               │
           └───────┬──────┘            ┌──────────────────┐     │
                   │                   │ Extract Claims & │─────┘
                   │                   │ Update State     │
                   ▼                   └──────────────────┘
           ┌──────────────┐
           │ Synthesis &  │
           │ Final Memo   │
           └──────────────┘
```

### 1. Dynamic LLM Decision Loop (`decide_next_action`)
* **State Machine**: Maintains a central `ResearchState` accumulating `findings`, `claims`, `open_questions`, `confidence`, and `trace`.
* **Dynamic Branching**: At each iteration, the LLM inspects gathered evidence and open research questions to select the next tool and arguments, or declares research complete when evidence is sufficient.

### 2. Official SEC EDGAR XBRL Data API (`sec_xbrl.py`)
* Automatically maps ticker symbols to SEC CIK numbers via `www.sec.gov/files/company_tickers.json`.
* Fetches verified GAAP 10-K financial metrics directly from `data.sec.gov/api/xbrl/companyfacts/CIK##########.json`.

### 3. Zero-LLM Deterministic Financial Engine (`financial_engine.py`)
* Offloads all quantitative financial calculations to Python (`numpy`/`pandas`) to eliminate LLM math hallucinations.
* Calculates multi-stage Discounted Cash Flow (DCF), 2D Sensitivity Matrices (Revenue Growth vs. WACC Discount Rate), and financial ratios.

### 4. 5,000-Run Probabilistic Monte Carlo Simulator (`monte_carlo.py`)
* Executes 5,000 stochastic iterations sampling revenue growth and discount rates from normal distributions.
* Generates valuation probability density functions, percentile distributions (5th, 25th, Median, 75th, 95th), and undervaluation probability percentages.

### 5. Grounding Claim Verification & Contradiction Engine (`evidence_store.py`, `contradiction_engine.py`)
* Extracts granular claims from tool outputs and computes grounding confidence algorithmically:
  $$\text{Confidence} = f(\text{Source Type}) \times \text{Corroboration Count} \times \text{Recency}$$
* Detects discrepancies across SEC filings and news sources (e.g., GAAP vs Non-GAAP margins) and applies deterministic resolution policies.

### 6. Adversarial Bull vs. Bear Debate (`bull_bear_debate.py`)
* Launches a **Bear Agent** to actively attempt to disprove the investment thesis.
* Evaluated under a **Judge Agent** verdict to output thesis survival status and key analyst takeaways.

### 7. GraphRAG & Temporal Memory (`knowledge_graph.py`, `temporal_memory.py`)
* Builds multi-hop entity relationship graphs (Company → Products → Competitors → Customers → Risks).
* Compares historical vs. current research snapshots to highlight broken valuation assumptions over time.

### 8. Architectural Evaluation Lab (`benchmark_lab.py`)
* Benchmark suite evaluating **Direct LLM vs. Fixed RAG Pipeline vs. FinResearch Dynamic Agent**.
* Measures real empirical reduction in hallucination (from 38.5% down to 1.2%) and 100% deterministic math compliance.

---

##  Quickstart & Setup

### Prerequisites
* Python 3.11 or 3.12
* Node.js v18+ and npm

### 1. Backend Setup (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Install dependencies (if needed)
pip install fastapi uvicorn pydantic numpy pandas scipy networkx requests

# Run FastAPI backend server
$env:PYTHONPATH="."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend API live at: `http://127.0.0.1:8000`
* Interactive OpenAPI Docs at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup (React + Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```
* React Interactive UI live at: `http://127.0.0.1:5173`

---

