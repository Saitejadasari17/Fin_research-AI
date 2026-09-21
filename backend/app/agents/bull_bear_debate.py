from typing import Any, Dict, List

from pydantic import BaseModel


class DebateArgument(BaseModel):
    agent_role: str
    point_title: str
    argument: str
    evidence_citation: str
    impact_rating: str


class DebateResult(BaseModel):
    bull_arguments: List[DebateArgument]
    bear_arguments: List[DebateArgument]
    judge_verdict: str
    thesis_survival_status: str
    confidence_delta: float
    key_takeaway: str


class BullBearDebateEngine:
    @staticmethod
    def run_adversarial_debate(
        company_name: str,
        base_thesis: str,
        financial_data: Dict[str, Any],
    ) -> DebateResult:
        revenue = financial_data.get("revenue")
        free_cash_flow = financial_data.get("free_cash_flow")
        debt = financial_data.get("total_debt")
        cash = financial_data.get("cash")
        operating_income = financial_data.get("operating_income")

        bulls = []
        bears = []

        if free_cash_flow is not None and free_cash_flow > 0:
            bulls.append(DebateArgument(
                agent_role="Bull Agent",
                point_title="Positive Free Cash Flow",
                argument=(
                    f"{company_name} reported positive free cash flow of "
                    f"{free_cash_flow:,.2f} in the supplied financial data."
                ),
                evidence_citation="Verified financial data: free_cash_flow",
                impact_rating="High",
            ))
        else:
            bears.append(DebateArgument(
                agent_role="Bear Agent",
                point_title="Free Cash Flow Unavailable or Negative",
                argument="The supplied evidence does not establish positive free cash flow.",
                evidence_citation="Verified financial data: free_cash_flow",
                impact_rating="Critical",
            ))

        if cash is not None and debt is not None and cash >= debt:
            bulls.append(DebateArgument(
                agent_role="Bull Agent",
                point_title="Cash Exceeds Debt",
                argument=f"Cash of {cash:,.2f} is at least as large as debt of {debt:,.2f}.",
                evidence_citation="Verified financial data: cash and total_debt",
                impact_rating="Medium",
            ))
        elif cash is not None and debt is not None:
            bears.append(DebateArgument(
                agent_role="Bear Agent",
                point_title="Debt Exceeds Cash",
                argument=f"Debt of {debt:,.2f} exceeds cash of {cash:,.2f}.",
                evidence_citation="Verified financial data: cash and total_debt",
                impact_rating="Medium",
            ))
        else:
            bears.append(DebateArgument(
                agent_role="Bear Agent",
                point_title="Balance Sheet Evidence Gap",
                argument="Cash and debt evidence is incomplete, limiting the balance-sheet case.",
                evidence_citation="Verified financial data: cash and total_debt",
                impact_rating="High",
            ))

        if not bulls:
            bulls.append(DebateArgument(
                agent_role="Bull Agent",
                point_title="Insufficient Positive Evidence",
                argument="No verified positive financial driver was available for the bull case.",
                evidence_citation="Collected financial evidence",
                impact_rating="Low",
            ))

        evidence_count = sum(
            value is not None
            for value in (revenue, free_cash_flow, debt, cash, operating_income)
        )
        if evidence_count < 3:
            verdict = "Evidence is insufficient for a reliable directional thesis."
            status = "Insufficient Evidence"
            takeaway = "Collect missing financial evidence before making an investment decision."
        elif len(bulls) > len(bears):
            verdict = f"The available evidence supports a cautious bull case for {company_name}."
            status = "Thesis Supported - Review Risks"
            takeaway = "Validate competitive, regulatory, and valuation evidence before acting."
        else:
            verdict = f"The available evidence supports a cautious bear case for {company_name}."
            status = "Thesis Challenged - More Research Required"
            takeaway = "Resolve the identified evidence gaps before acting."

        return DebateResult(
            bull_arguments=bulls,
            bear_arguments=bears,
            judge_verdict=verdict,
            thesis_survival_status=status,
            confidence_delta=0.0,
            key_takeaway=takeaway,
        )