from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.config import settings
from app.core.orchestrator import DynamicOrchestrator, InvestmentResearchReport
from app.tools.financial_engine import FinancialEngine, DCFInput, DCFResult
from app.tools.monte_carlo import MonteCarloSimulator, MonteCarloResult
from app.eval.benchmark_lab import BenchmarkLabEngine, BenchmarkComparisonReport
from app.core.temporal_memory import TemporalMemoryEngine, TemporalDiffResult

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Evidence-Grounded Investment Due-Diligence System"
)

# Configure CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    company_name: str
    target_question: Optional[str] = "Should I invest in this company?"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.post("/api/research/analyze", response_model=InvestmentResearchReport)
def analyze_company(req: ResearchRequest):
    try:
        orchestrator = DynamicOrchestrator()
        report = orchestrator.run_investigation(req.company_name, req.target_question)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/valuation/dcf", response_model=DCFResult)
def calculate_custom_dcf(inputs: DCFInput):
    try:
        return FinancialEngine.calculate_dcf(inputs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/valuation/monte-carlo", response_model=MonteCarloResult)
def calculate_custom_monte_carlo(inputs: DCFInput, num_simulations: int = 5000):
    try:
        return MonteCarloSimulator.run_simulation(inputs, num_simulations=num_simulations)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/eval/benchmark", response_model=BenchmarkComparisonReport)
def get_benchmark_results():
    try:
        return BenchmarkLabEngine.run_benchmark_suite()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{ticker}", response_model=TemporalDiffResult)
def get_temporal_history(ticker: str):
    try:
        # Default mock current metrics for temporal diff demonstration
        return TemporalMemoryEngine.compute_temporal_diff(
            ticker=ticker,
            current_val=128.50,
            current_growth=0.32,
            current_wacc=0.09,
            current_risks=["Customer custom silicon acceleration", "TSMC supply chain bottleneck"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
