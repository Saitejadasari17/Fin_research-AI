from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Optional

from app.config import settings

from app.core.orchestrator import (
    DynamicOrchestrator,
    InvestmentResearchReport,
)

from app.tools.financial_engine import (
    FinancialEngine,
    DCFInput,
    DCFResult,
)

from app.tools.monte_carlo import (
    MonteCarloSimulator,
    MonteCarloResult,
)

from app.eval.benchmark_lab import (
    BenchmarkLabEngine,
    BenchmarkComparisonReport,
)

from app.core.temporal_memory import (
    TemporalMemoryEngine,
    TemporalDiffResult,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Autonomous Evidence-Grounded "
        "Investment Due-Diligence System"
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ResearchRequest(BaseModel):
    company_name: str
    target_question: Optional[str] = (
        "Should I invest in this company?"
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def read_root():

    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
    }


# ============================================================
# INVESTMENT RESEARCH
# ============================================================

@app.post(
    "/api/research/analyze",
    response_model=InvestmentResearchReport,
)
def analyze_company(req: ResearchRequest):

    company_name = req.company_name.strip()

    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Company name cannot be empty.",
        )

    try:

        orchestrator = DynamicOrchestrator()

        report = orchestrator.run_investigation(
            company_name,
            req.target_question,
        )

        return report

    except HTTPException:
        raise

    except Exception as e:

        # Print the complete exception to the backend
        # terminal so development errors are visible.
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to execute dynamic investigation: "
                f"{type(e).__name__}: {str(e)}"
            ),
        )


# ============================================================
# CUSTOM DCF
# ============================================================

@app.post(
    "/api/valuation/dcf",
    response_model=DCFResult,
)
def calculate_custom_dcf(inputs: DCFInput):

    try:

        return FinancialEngine.calculate_dcf(
            inputs
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ============================================================
# MONTE CARLO
# ============================================================

@app.post(
    "/api/valuation/monte-carlo",
    response_model=MonteCarloResult,
)
def calculate_custom_monte_carlo(
    inputs: DCFInput,
    num_simulations: int = 5000,
):

    try:

        if num_simulations < 100:
            raise ValueError(
                "num_simulations must be at least 100."
            )

        if num_simulations > 100000:
            raise ValueError(
                "num_simulations cannot exceed 100000."
            )

        return MonteCarloSimulator.run_simulation(
            inputs,
            num_simulations=num_simulations,
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ============================================================
# BENCHMARK
# ============================================================

@app.get(
    "/api/eval/benchmark",
    response_model=BenchmarkComparisonReport,
)
def get_benchmark_results():

    try:

        return BenchmarkLabEngine.run_benchmark_suite()

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# TEMPORAL MEMORY
# ============================================================

@app.get(
    "/api/history/{ticker}",
    response_model=TemporalDiffResult,
)
def get_temporal_history(ticker: str):

    try:

        # NOTE:
        # This endpoint is retained for frontend compatibility.
        #
        # The actual research pipeline should populate temporal
        # memory from the current research run rather than using
        # these demo values.

        return TemporalMemoryEngine.compute_temporal_diff(
            ticker=ticker,
            current_val=0.0,
            current_growth=0.0,
            current_wacc=0.09,
            current_risks=[],
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )