from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoricalResearchSnapshot(BaseModel):
    snapshot_id: str
    company_ticker: str
    timestamp: str
    thesis_recommendation: Optional[str] = None
    dcf_intrinsic_value: Optional[float] = None
    high_growth_assumption: Optional[float] = None
    wacc_assumption: Optional[float] = None
    key_risks_identified: List[str] = []


class TemporalDiffResult(BaseModel):
    ticker: str
    previous_snapshot: Optional[HistoricalResearchSnapshot] = None
    current_snapshot: HistoricalResearchSnapshot
    intrinsic_value_change_percent: Optional[float] = None
    growth_rate_delta: Optional[float] = None
    invalidated_assumptions: List[str] = []
    newly_emerged_risks: List[str] = []
    summary_diff_narrative: str


class TemporalMemoryEngine:
    @staticmethod
    def get_historical_snapshot(ticker: str) -> Optional[HistoricalResearchSnapshot]:
        return None

    @staticmethod
    def compute_temporal_diff(
        ticker: str,
        current_val: float,
        current_growth: float,
        current_wacc: float,
        current_risks: List[str],
    ) -> TemporalDiffResult:
        previous = TemporalMemoryEngine.get_historical_snapshot(ticker)
        current = HistoricalResearchSnapshot(
            snapshot_id=f"SNAP-{ticker.upper()}-CURRENT",
            company_ticker=ticker.upper(),
            timestamp=datetime.now().strftime("%Y-%m-%d"),
            dcf_intrinsic_value=current_val,
            high_growth_assumption=current_growth,
            wacc_assumption=current_wacc,
            key_risks_identified=current_risks,
        )

        if previous is None:
            return TemporalDiffResult(
                ticker=ticker.upper(),
                current_snapshot=current,
                newly_emerged_risks=current_risks,
                summary_diff_narrative="No prior research snapshot is available for comparison.",
            )

        value_change = None
        if previous.dcf_intrinsic_value:
            value_change = (
                (current_val - previous.dcf_intrinsic_value)
                / previous.dcf_intrinsic_value
                * 100
            )
        growth_delta = None
        if previous.high_growth_assumption is not None:
            growth_delta = (current_growth - previous.high_growth_assumption) * 100

        return TemporalDiffResult(
            ticker=ticker.upper(),
            previous_snapshot=previous,
            current_snapshot=current,
            intrinsic_value_change_percent=value_change,
            growth_rate_delta=growth_delta,
            newly_emerged_risks=[
                risk for risk in current_risks
                if risk not in previous.key_risks_identified
            ],
            summary_diff_narrative="Compared current research with the available historical snapshot.",
        )