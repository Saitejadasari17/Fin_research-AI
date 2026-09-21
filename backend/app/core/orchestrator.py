import time
import uuid
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from app.tools.financial_engine import (
    FinancialEngine,
    DCFInput,
    DCFResult,
    FinancialMetrics,
    SensitivityMatrix,
)
from app.tools.monte_carlo import MonteCarloSimulator, MonteCarloResult
from app.tools.search_rag import TOOLS
from app.tools.company_resolver import CompanyResolver, CompanyContext
from app.core.evidence_store import EvidenceStore, ClaimItem
from app.core.contradiction_engine import (
    ContradictionEngine,
    ContradictionAlert,
)
from app.agents.bull_bear_debate import (
    BullBearDebateEngine,
    DebateResult,
)
from app.core.knowledge_graph import (
    KnowledgeGraphEngine,
    KnowledgeGraphData,
)
from app.core.temporal_memory import (
    TemporalMemoryEngine,
    TemporalDiffResult,
)


# ============================================================
# MODELS
# ============================================================

class ResearchTraceStep(BaseModel):
    step_id: int
    timestamp: str
    phase: str
    agent_role: str
    action: str
    tool_called: str
    findings_summary: str
    status: str
    latency_ms: int
    token_cost: float = 0.0


class ResearchState(BaseModel):
    company: str
    goal: str
    company_context: Optional[CompanyContext] = None

    research_id: str = Field(
        default_factory=lambda: f"RES-{uuid.uuid4().hex[:8].upper()}"
    )

    findings: List[Dict[str, Any]] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)

    open_questions: List[str] = Field(
        default_factory=lambda: [
            "financials",
            "market_data",
            "competition",
            "risks",
        ]
    )

    confidence: Dict[str, float] = Field(default_factory=dict)
    trace: List[ResearchTraceStep] = Field(default_factory=list)

    iteration: int = 0


class InvestmentResearchReport(BaseModel):
    research_id: str
    task_id: str

    company_name: str
    ticker: str
    currency: str = "USD"

    executive_summary: str

    investment_recommendation: str
    confidence_score: float
    overall_confidence_breakdown: Dict[str, float]

    financial_metrics: FinancialMetrics
    dcf_result: DCFResult
    monte_carlo_result: MonteCarloResult
    sensitivity_matrix: SensitivityMatrix

    claims: List[ClaimItem]
    contradictions: List[ContradictionAlert]

    debate_result: DebateResult
    knowledge_graph: KnowledgeGraphData
    temporal_diff: TemporalDiffResult

    execution_trace: List[ResearchTraceStep]

    total_latency_seconds: float
    total_cost_usd: float


# ============================================================
# ORCHESTRATOR
# ============================================================

class DynamicOrchestrator:
    """
    Company-aware agentic investment research orchestrator.

    LLM / Agent -> decides WHAT to investigate next
    Tools -> retrieve actual data
    Python -> performs deterministic calculations

    Important data convention:
        Provider financial values are expected in base currency units.
        DCFInput expects monetary values in millions.
        Provider share counts are expected as absolute share counts.
        DCFInput expects shares outstanding in millions.
    """

    @staticmethod
    def _available_tool(*names: str) -> Optional[str]:
        for name in names:
            if name in TOOLS:
                return name
        return None

    @staticmethod
    def _is_indian_company(context: CompanyContext) -> bool:
        country = getattr(context, "country", None)

        if country:
            return str(country).strip().lower() in {
                "india",
                "in",
                "ind",
            }

        currency = getattr(context, "currency", None)

        if currency:
            return str(currency).upper() in {
                "INR",
                "₹",
            }

        nse = getattr(context, "nse_symbol", None)

        return bool(nse)

    @staticmethod
    def _get_finding(
        state: ResearchState,
        tool_names: List[str],
    ) -> Dict[str, Any]:

        for finding in state.findings:
            if finding.get("tool") in tool_names:
                result = finding.get("result")

                if isinstance(result, dict):
                    return result

        return {}

    def decide_next_action(
        self,
        state: ResearchState,
    ) -> Dict[str, Any]:

        context = state.company_context

        if context is None:
            raise ValueError("CompanyContext is required.")

        is_india = self._is_indian_company(context)

        completed_tools = {
            finding.get("tool")
            for finding in state.findings
        }

        # ====================================================
        # 1. FINANCIAL DATA
        # ====================================================

        indian_financial_tool = self._available_tool(
            "get_indian_financials",
            "get_bse_financials",
            "get_nse_financials",
            "get_company_financials",
        )

        us_financial_tool = self._available_tool(
            "get_sec_financials",
        )

        financial_tool = (
            indian_financial_tool
            if is_india
            else us_financial_tool
        )

        if financial_tool and financial_tool not in completed_tools:

            ticker = (
                context.nse_symbol
                or context.ticker
            )

            return {
                "action": "call_tool",
                "tool": financial_tool,
                "args": {
                    "ticker": ticker,
                    "company_name_or_ticker": ticker,
                },
                "reasoning": (
                    f"Retrieve verified financial statements for "
                    f"{context.company_name} using "
                    f"{'Indian market' if is_india else 'US SEC'} data."
                ),
            }

        # ====================================================
        # 2. MARKET DATA
        # ====================================================

        market_tool = self._available_tool(
            "get_indian_market_data"
            if is_india
            else "get_market_data",
            "get_market_data",
        )

        if market_tool and market_tool not in completed_tools:

            ticker = (
                context.nse_symbol
                or context.ticker
            )

            args = {
                "ticker": ticker,
                "company_name_or_ticker": ticker,
            }

            if is_india:
                args["exchange"] = "NSE"

            return {
                "action": "call_tool",
                "tool": market_tool,
                "args": args,
                "reasoning": (
                    f"Retrieve current stock price and market data "
                    f"for {context.company_name}."
                ),
            }

        # ====================================================
        # 3. COMPANY-SPECIFIC NEWS & RISKS
        # ====================================================

        news_tool = self._available_tool(
            "web_search_news",
            "search_company_news",
        )

        if news_tool and news_tool not in completed_tools:

            company = context.company_name

            ticker = (
                context.nse_symbol
                or context.ticker
            )

            topic = (
                f"{company} latest earnings growth drivers "
                f"risks competition"
            )

            return {
                "action": "call_tool",
                "tool": news_tool,
                "args": {
                    "ticker": ticker,
                    "topic": topic,
                },
                "reasoning": (
                    f"Investigate recent news, risks, and "
                    f"growth developments for {company}."
                ),
            }

        # ====================================================
        # 4. SUFFICIENCY GATE
        # ====================================================

        return {
            "action": "complete",
            "tool": "none",
            "args": {},
            "reasoning": (
                "Evidence sufficiency condition met across "
                "Financials, Market Data, and Risks."
            ),
        }

    def run_investigation(
        self,
        company_name: str,
        target_question: str = "Should I invest?",
        max_iterations: int = 8,
    ) -> InvestmentResearchReport:

        start_time = time.time()

        task_id = (
            f"TASK-{uuid.uuid4().hex[:8].upper()}"
        )

        # ====================================================
        # COMPANY RESOLUTION
        # ====================================================

        context = CompanyResolver.resolve(
            company_name
        )

        if context is None:
            raise ValueError(
                f"Could not resolve company: {company_name}"
            )

        state = ResearchState(
            company=context.company_name,
            goal=target_question,
            company_context=context,
        )

        evidence_store = EvidenceStore()

        step_counter = 1

        # ====================================================
        # AGENTIC RESEARCH LOOP
        # ====================================================

        while state.iteration < max_iterations:

            decision = self.decide_next_action(
                state
            )

            step_start = time.time()

            # ------------------------------------------------
            # SUFFICIENCY GATE
            # ------------------------------------------------

            if decision["action"] == "complete":

                latency = int(
                    (time.time() - step_start) * 1000
                )

                state.trace.append(
                    ResearchTraceStep(
                        step_id=step_counter,
                        timestamp=time.strftime(
                            "%H:%M:%S"
                        ),
                        phase="Sufficiency Gate",
                        agent_role="Research Planner",
                        action="Evaluate Evidence Sufficiency",
                        tool_called="Sufficiency Evaluator",
                        findings_summary=decision[
                            "reasoning"
                        ],
                        status="Completed",
                        latency_ms=max(
                            latency,
                            1,
                        ),
                        token_cost=0.0,
                    )
                )

                step_counter += 1

                break

            # ------------------------------------------------
            # TOOL EXECUTION
            # ------------------------------------------------

            tool_name = decision["tool"]

            if tool_name not in TOOLS:
                raise RuntimeError(
                    f"Required tool '{tool_name}' "
                    f"is not registered."
                )

            tool_args = decision.get(
                "args",
                {},
            )

            tool_fn = TOOLS[tool_name]

            # Introspect the actual function signature
            # so tools with different argument names can
            # still be called safely.

            import inspect

            sig = inspect.signature(
                tool_fn
            )

            filtered_args = {
                key: value
                for key, value in tool_args.items()
                if key in sig.parameters
            }

            if (
                not filtered_args
                and len(sig.parameters) > 0
            ):

                first_param = list(
                    sig.parameters.keys()
                )[0]

                filtered_args = {
                    first_param: (
                        tool_args.get("ticker")
                        or tool_args.get(
                            "company_name_or_ticker"
                        )
                    )
                }

            # ------------------------------------------------
            # CALL TOOL
            # ------------------------------------------------

            try:

                result = tool_fn(
                    **filtered_args
                )

            except Exception as exc:

                latency = int(
                    (time.time() - step_start) * 1000
                )

                state.trace.append(
                    ResearchTraceStep(
                        step_id=step_counter,
                        timestamp=time.strftime(
                            "%H:%M:%S"
                        ),
                        phase="Dynamic Investigation",
                        agent_role="Research Agent",
                        action=decision[
                            "reasoning"
                        ],
                        tool_called=tool_name,
                        findings_summary=str(exc),
                        status="Failed",
                        latency_ms=max(
                            latency,
                            1,
                        ),
                        token_cost=0.0,
                    )
                )

                raise RuntimeError(
                    f"Tool '{tool_name}' failed: {exc}"
                ) from exc

            if not isinstance(result, dict):
                raise RuntimeError(
                    f"Tool '{tool_name}' "
                    f"returned invalid data."
                )

            # ------------------------------------------------
            # EXTRACT EVIDENCE
            # ------------------------------------------------

            extracted_claims = (
                evidence_store.extract_claims_from_finding(
                    tool_name,
                    result,
                )
            )

            state.claims.extend(
                extracted_claims
            )

            state.findings.append(
                {
                    "iteration": state.iteration,
                    "tool": tool_name,
                    "args": filtered_args,
                    "result": result,
                }
            )

            step_latency = int(
                (time.time() - step_start) * 1000
            )

            state.trace.append(
                ResearchTraceStep(
                    step_id=step_counter,
                    timestamp=time.strftime(
                        "%H:%M:%S"
                    ),
                    phase="Dynamic Investigation",
                    agent_role="Research Agent",
                    action=decision[
                        "reasoning"
                    ],
                    tool_called=tool_name,
                    findings_summary=(
                        f"Retrieved "
                        f"{list(result.keys())}"
                    ),
                    status="Completed",
                    latency_ms=max(
                        step_latency,
                        1,
                    ),
                    token_cost=0.0,
                )
            )

            step_counter += 1
            state.iteration += 1

        # ====================================================
        # RETRIEVE FINANCIAL FINDINGS
        # ====================================================

        financial_data = self._get_finding(
            state,
            [
                "get_indian_financials",
                "get_bse_financials",
                "get_nse_financials",
                "get_company_financials",
                "get_sec_financials",
                "get_financials",
            ],
        )

        # ====================================================
        # RETRIEVE MARKET FINDINGS
        # ====================================================

        market_data = self._get_finding(
            state,
            [
                "get_indian_market_data",
                "get_nse_market_data",
                "get_bse_market_data",
                "get_market_data",
            ],
        )

        # ====================================================
        # FINANCIAL DATA VALIDATION
        # ====================================================

        required_financial_fields = [
            "revenue",
            "free_cash_flow",
            "total_debt",
            "cash",
            "net_income",
            "operating_income",
        ]

        missing_financial_fields = [
            field
            for field in required_financial_fields
            if financial_data.get(field) is None
        ]

        if missing_financial_fields:

            raise ValueError(
                "Insufficient financial data for valuation. "
                f"Missing: {missing_financial_fields}"
            )

        # ====================================================
        # EXTRACT ACTUAL FINANCIAL VALUES
        # ====================================================

        revenue = float(
            financial_data["revenue"]
        )

        fcf = float(
            financial_data["free_cash_flow"]
        )

        debt = float(
            financial_data["total_debt"]
        )

        cash = float(
            financial_data["cash"]
        )

        net_income = float(
            financial_data["net_income"]
        )

        op_income = float(
            financial_data["operating_income"]
        )

        # ====================================================
        # MARKET PRICE VALIDATION
        # ====================================================

        price_value = (
            market_data.get(
                "current_stock_price"
            )
        )

        if price_value is None:

            raise ValueError(
                "Current stock price is required "
                "for valuation."
            )

        price = float(
            price_value
        )

        if price <= 0:

            raise ValueError(
                "Current stock price must be "
                "greater than zero."
            )

        # ====================================================
        # SHARES NORMALIZATION
        # ====================================================
        #
        # Provider:
        #     absolute number of shares
        #
        # DCFInput:
        #     millions of shares
        #
        # Example:
        #     13,532,736,424 shares
        #
        # becomes:
        #     13,532.736424 million shares
        #
        # ====================================================

        shares_value = (
            market_data.get(
                "shares_outstanding"
            )
            or financial_data.get(
                "shares_outstanding"
            )
        )

        if shares_value is not None:

            shares_absolute = float(
                shares_value
            )

            shares = (
                shares_absolute
                / 1_000_000.0
            )

        else:

            market_cap_val = (
                market_data.get(
                    "market_cap"
                )
            )

            if (
                market_cap_val is not None
                and price > 0
            ):

                shares_absolute = (
                    float(market_cap_val)
                    / price
                )

                shares = (
                    shares_absolute
                    / 1_000_000.0
                )

            else:

                raise ValueError(
                    "Shares outstanding are required "
                    "for DCF valuation."
                )

        if shares <= 0:

            raise ValueError(
                "Shares outstanding must be "
                "greater than zero."
            )

        # ====================================================
        # GROWTH ASSUMPTION
        # ====================================================

        growth_value = (
            market_data.get(
                "high_growth_rate"
            )
            or financial_data.get(
                "high_growth_rate"
            )
        )

        if growth_value is None:

            # This is a valuation assumption, NOT
            # fabricated financial data.

            growth = (
                0.12
                if self._is_indian_company(
                    context
                )
                else 0.09
            )

        else:

            growth = float(
                growth_value
            )

        # Normalize percentage values such as 12
        # into decimal values such as 0.12.

        if growth > 1.0:
            growth = growth / 100.0

        if growth < -1.0:
            raise ValueError(
                "High-growth assumption is invalid."
            )

        # ====================================================
        # WACC & TERMINAL GROWTH
        # ====================================================

        is_india = (
            self._is_indian_company(
                context
            )
        )

        wacc_value = financial_data.get(
            "wacc"
        )

        if wacc_value is None:

            # Valuation assumption.

            wacc = (
                0.115
                if is_india
                else 0.09
            )

        else:

            wacc = float(
                wacc_value
            )

        terminal_growth_value = (
            financial_data.get(
                "terminal_growth_rate"
            )
        )

        if terminal_growth_value is None:

            # Valuation assumption.

            terminal_growth = (
                0.04
                if is_india
                else 0.025
            )

        else:

            terminal_growth = float(
                terminal_growth_value
            )

        if wacc <= terminal_growth:

            raise ValueError(
                "WACC must be greater than "
                "terminal growth rate."
            )

        # ====================================================
        # NORMALIZE FINANCIAL VALUES FOR DCF
        # ====================================================
        #
        # Provider financial values:
        #
        #     - SEC XBRL API: "financial_scale" == "millions" (already Millions USD)
        #     - Indian / Yahoo: base units (INR)
        #
        # DCFInput expects:
        #
        #     Million INR / Million USD
        #
        # ====================================================

        is_millions = financial_data.get("financial_scale") == "millions"

        if is_millions:
            dcf_fcf = fcf
            dcf_cash = cash
            dcf_debt = debt

            fcf_base = fcf * 1_000_000.0
            cash_base = cash * 1_000_000.0
            debt_base = debt * 1_000_000.0
            revenue_base = revenue * 1_000_000.0
            net_income_base = net_income * 1_000_000.0
            op_income_base = op_income * 1_000_000.0
        else:
            dcf_fcf = fcf / 1_000_000.0
            dcf_cash = cash / 1_000_000.0
            dcf_debt = debt / 1_000_000.0

            fcf_base = fcf
            cash_base = cash
            debt_base = debt
            revenue_base = revenue
            net_income_base = net_income
            op_income_base = op_income

        # ====================================================
        # DATA DICTIONARY FOR FINANCIAL RATIOS
        # ====================================================

        data_dict = {
            # IMPORTANT:
            # market cap must use ABSOLUTE shares,
            # not shares expressed in millions.
            "market_cap": (
                price
                * shares_absolute
            ),

            "net_income": net_income_base,

            "revenue": revenue_base,

            "free_cash_flow": fcf_base,

            "total_debt": debt_base,

            "cash": cash_base,

            "operating_income": op_income_base,

            # These are retained for compatibility with
            # FinancialEngine.calculate_ratios.
            #
            # They are only populated when the provider
            # actually supplies them.

            "total_assets": financial_data.get(
                "total_assets"
            ),

            "total_equity": financial_data.get(
                "total_equity"
            ),

            "ebitda": financial_data.get(
                "ebitda"
            ),

            "revenue_history_3yr": financial_data.get(
                "revenue_history_3yr"
            ),
        }

        # ====================================================
        # FINANCIAL RATIOS
        # ====================================================

        metrics = (
            FinancialEngine.calculate_ratios(
                data_dict
            )
        )

        # ====================================================
        # DCF INPUT
        # ====================================================
        #
        # current_fcf
        # cash_and_equivalents
        # total_debt
        # shares_outstanding
        #
        # are now all expressed in MILLIONS.
        #
        # current_stock_price remains the actual
        # per-share market price.
        #
        # ====================================================

        dcf_input = DCFInput(
            current_fcf=dcf_fcf,

            cash_and_equivalents=dcf_cash,

            total_debt=dcf_debt,

            shares_outstanding=shares,

            current_stock_price=price,

            high_growth_rate=growth,

            high_growth_years=5,

            fade_growth_rate=growth * 0.5,

            fade_years=5,

            terminal_growth_rate=terminal_growth,

            wacc=wacc,
        )

        # ====================================================
        # DETERMINISTIC VALUATION
        # ====================================================

        dcf_result = (
            FinancialEngine.calculate_dcf(
                dcf_input
            )
        )

        # ====================================================
        # SENSITIVITY ANALYSIS
        # ====================================================

        sensitivity_matrix = (
            FinancialEngine.calculate_sensitivity(
                dcf_input
            )
        )

        # ====================================================
        # MONTE CARLO
        # ====================================================

        monte_carlo_result = (
            MonteCarloSimulator.run_simulation(
                dcf_input,
                num_simulations=5000,
            )
        )

        # ====================================================
        # TRACE QUANTITATIVE ANALYSIS
        # ====================================================

        state.trace.append(
            ResearchTraceStep(
                step_id=step_counter,
                timestamp=time.strftime(
                    "%H:%M:%S"
                ),
                phase="Quantitative Analysis",
                agent_role="Financial Agent",
                action=(
                    "Execute deterministic valuation "
                    "and Monte Carlo simulation"
                ),
                tool_called=(
                    "Python FinancialEngine "
                    "& MonteCarloSimulator"
                ),
                findings_summary=(
                    f"Intrinsic Value: "
                    f"{dcf_result.intrinsic_value_per_share:.2f}; "
                    f"Market Price: "
                    f"{dcf_result.current_price:.2f}; "
                    f"Status: "
                    f"{dcf_result.valuation_status}"
                ),
                status="Completed",
                latency_ms=10,
                token_cost=0.0,
            )
        )

        step_counter += 1

        # ====================================================
        # EVIDENCE
        # ====================================================

        all_claims = (
            evidence_store.get_all_claims()
        )

        confidence_breakdown = (
            evidence_store.calculate_overall_confidence()
        )

        # ====================================================
        # CONTRADICTIONS
        # ====================================================

        contradictions = (
            ContradictionEngine.detect_contradictions(
                all_claims,
                context.company_name,
            )
        )

        # ====================================================
        # BULL / BEAR DEBATE
        # ====================================================

        debate = (
            BullBearDebateEngine.run_adversarial_debate(
                context.company_name,
                state.goal,
                data_dict,
            )
        )

        # ====================================================
        # KNOWLEDGE GRAPH
        # ====================================================

        kg_data = (
            KnowledgeGraphEngine.build_company_graph(
                context.nse_symbol
                or context.ticker
                or ""
            )
        )

        # ====================================================
        # TEMPORAL MEMORY
        # ====================================================

        temporal_diff = (
            TemporalMemoryEngine.compute_temporal_diff(
                ticker=(
                    context.nse_symbol
                    or context.ticker
                    or ""
                ),
                current_val=(
                    dcf_result.intrinsic_value_per_share
                ),
                current_growth=growth,
                current_wacc=wacc,
                current_risks=[],
            )
        )

        # ====================================================
        # VALUATION STATUS
        # ====================================================

        valuation_status = (
            dcf_result.valuation_status
        )

        # ====================================================
        # RECOMMENDATION
        # ====================================================

        if (
            debate.thesis_survival_status
            == "Insufficient Evidence"
            or confidence_breakdown.get(
                "overall",
                0.0,
            ) < 50.0
        ):

            recommendation = (
                "INSUFFICIENT EVIDENCE"
            )

        elif valuation_status == "Undervalued":

            recommendation = "BUY"

        elif valuation_status == "Overvalued":

            recommendation = "SELL"

        else:

            recommendation = "HOLD"

        # ====================================================
        # CURRENCY
        # ====================================================

        currency = getattr(
            context,
            "currency",
            None,
        )

        if not currency:

            currency = (
                "INR"
                if is_india
                else "USD"
            )

        # ====================================================
        # EXECUTIVE SUMMARY
        # ====================================================

        exec_summary = (
            f"Evidence-grounded autonomous "
            f"due-diligence analysis for "
            f"{context.company_name} "
            f"({context.nse_symbol or context.ticker or ''}). "
            f"DCF intrinsic value calculated at "
            f"{currency} "
            f"{dcf_result.intrinsic_value_per_share:.2f} "
            f"per share versus current market price "
            f"{currency} "
            f"{dcf_result.current_price:.2f} "
            f"({dcf_result.valuation_status}). "
            f"Probabilistic 5,000-run Monte Carlo "
            f"simulation indicates "
            f"{monte_carlo_result.probability_undervalued_percent}% "
            f"likelihood of stock undervaluation. "
            f"Bull/Bear verdict: "
            f"{debate.thesis_survival_status}."
        )

        # ====================================================
        # FINAL METRICS
        # ====================================================

        total_latency = (
            time.time()
            - start_time
        )

        total_cost = sum(
            trace.token_cost
            for trace in state.trace
        )

        # ====================================================
        # FINAL REPORT
        # ====================================================

        return InvestmentResearchReport(
            research_id=state.research_id,

            task_id=task_id,

            company_name=context.company_name,

            ticker=(
                context.nse_symbol
                or context.ticker
                or market_data.get(
                    "ticker",
                    "",
                )
                or ""
            ),

            currency=currency,

            executive_summary=exec_summary,

            investment_recommendation=recommendation,

            confidence_score=(
                confidence_breakdown.get(
                    "overall",
                    0.0,
                )
            ),

            overall_confidence_breakdown=(
                confidence_breakdown
            ),

            financial_metrics=metrics,

            dcf_result=dcf_result,

            monte_carlo_result=(
                monte_carlo_result
            ),

            sensitivity_matrix=(
                sensitivity_matrix
            ),

            claims=all_claims,

            contradictions=contradictions,

            debate_result=debate,

            knowledge_graph=kg_data,

            temporal_diff=temporal_diff,

            execution_trace=state.trace,

            total_latency_seconds=round(
                total_latency,
                2,
            ),

            total_cost_usd=round(
                total_cost,
                4,
            ),
        )