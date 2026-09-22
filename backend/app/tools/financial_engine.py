import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class FinancialMetrics(BaseModel):
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_yield: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    revenue_cagr_3yr: Optional[float] = None

class DCFInput(BaseModel):
    current_fcf: float                # Million USD
    cash_and_equivalents: float       # Million USD
    total_debt: float                 # Million USD
    shares_outstanding: float         # Million
    current_stock_price: float        # USD
    high_growth_rate: float           # e.g. 0.25 (25%)
    high_growth_years: int            # e.g. 5
    fade_growth_rate: float           # e.g. 0.12 (12%)
    fade_years: int                   # e.g. 5
    terminal_growth_rate: float       # e.g. 0.03 (3%)
    wacc: float                       # e.g. 0.09 (9%)

class DCFResult(BaseModel):
    intrinsic_value_per_share: float
    current_price: float
    upside_downside_percent: float
    valuation_status: str             # "Overvalued", "Undervalued", "Fairly Valued"
    enterprise_value: float
    equity_value: float
    pv_forecast_cash_flows: float
    pv_terminal_value: float
    yearly_cash_flows: List[Dict[str, Any]]
    wacc_used: float

class SensitivityMatrix(BaseModel):
    growth_rates: List[float]
    discount_rates: List[float]
    matrix: List[List[float]]          # Rows: growth rates, Cols: discount rates

class FinancialEngine:
    """
    Financial calculation engine for DCF valuation, Monte Carlo simulations, and key ratios.
    """

    @staticmethod
    def calculate_ratios(data: Dict[str, float]) -> FinancialMetrics:
        market_cap = data.get("market_cap")
        net_income = data.get("net_income")
        revenue = data.get("revenue")
        fcf = data.get("free_cash_flow")
        total_equity = data.get("total_equity")
        total_debt = data.get("total_debt")
        ebitda = data.get("ebitda")
        cash = data.get("cash")
        operating_income = data.get("operating_income")

        ev = (
            market_cap + total_debt - cash
            if all(value is not None for value in (market_cap, total_debt, cash))
            else None
        )

        pe = market_cap / net_income if market_cap is not None and net_income and net_income > 0 else None
        ps = market_cap / revenue if market_cap is not None and revenue and revenue > 0 else None
        pb = market_cap / total_equity if market_cap is not None and total_equity and total_equity > 0 else None
        ev_ebitda = ev / ebitda if ev is not None and ebitda and ebitda > 0 else None
        op_margin = operating_income / revenue if operating_income is not None and revenue and revenue > 0 else None
        net_margin = net_income / revenue if net_income is not None and revenue and revenue > 0 else None
        fcf_yield = fcf / market_cap if fcf is not None and market_cap and market_cap > 0 else None
        debt_to_equity = total_debt / total_equity if total_debt is not None and total_equity and total_equity > 0 else None
        current_assets = data.get("current_assets")
        current_liabilities = data.get("current_liabilities")
        current_ratio = current_assets / current_liabilities if current_assets is not None and current_liabilities and current_liabilities > 0 else None

        rev_hist = data.get("revenue_history_3yr")
        if rev_hist and len(rev_hist) >= 2 and rev_hist[0] > 0:
            cagr = ((rev_hist[-1] / rev_hist[0]) ** (1 / (len(rev_hist) - 1))) - 1
        else:
            cagr = None

        return FinancialMetrics(
            pe_ratio=round(pe, 2) if pe is not None else None,
            forward_pe=round(pe * 0.85, 2) if pe is not None else None,
            pb_ratio=round(pb, 2) if pb is not None else None,
            ps_ratio=round(ps, 2) if ps is not None else None,
            ev_ebitda=round(ev_ebitda, 2) if ev_ebitda is not None else None,
            operating_margin=round(op_margin * 100, 2) if op_margin is not None else None,
            net_margin=round(net_margin * 100, 2) if net_margin is not None else None,
            fcf_yield=round(fcf_yield * 100, 2) if fcf_yield is not None else None,
            debt_to_equity=round(debt_to_equity, 2) if debt_to_equity is not None else None,
            current_ratio=round(current_ratio, 2) if current_ratio is not None else None,
            revenue_cagr_3yr=round(cagr * 100, 2) if cagr is not None else None
        )

    @staticmethod
    def calculate_dcf(inputs: DCFInput) -> DCFResult:
        if inputs.current_fcf is None:
            raise ValueError("Current FCF is required for DCF valuation.")
        if inputs.shares_outstanding <= 0:
            raise ValueError("Shares outstanding must be greater than zero.")
        if inputs.current_stock_price <= 0:
            raise ValueError("Current stock price must be greater than zero.")
        if inputs.high_growth_years <= 0 or inputs.fade_years <= 0:
            raise ValueError("DCF growth periods must be greater than zero.")
        if inputs.wacc <= inputs.terminal_growth_rate:
            raise ValueError("WACC must be greater than terminal growth.")

        cf = inputs.current_fcf
        pv_cf_sum = 0.0
        yearly_details = []

        # Stage 1: High Growth Period
        current_year = 1
        for yr in range(1, inputs.high_growth_years + 1):
            cf = cf * (1 + inputs.high_growth_rate)
            discount_factor = (1 + inputs.wacc) ** yr
            pv = cf / discount_factor
            pv_cf_sum += pv
            yearly_details.append({"year": yr, "phase": "High Growth", "fcf": round(cf, 2), "pv_fcf": round(pv, 2)})
            current_year += 1

        # Stage 2: Fade Growth Period
        for yr in range(1, inputs.fade_years + 1):
            # Interpolate growth rate down to terminal growth rate
            growth_step = (inputs.high_growth_rate - inputs.fade_growth_rate) / inputs.fade_years
            g = max(inputs.high_growth_rate - (growth_step * yr), inputs.terminal_growth_rate)
            cf = cf * (1 + g)
            discount_factor = (1 + inputs.wacc) ** current_year
            pv = cf / discount_factor
            pv_cf_sum += pv
            yearly_details.append({"year": current_year, "phase": "Fade Growth", "fcf": round(cf, 2), "pv_fcf": round(pv, 2)})
            current_year += 1

        # Terminal Value via Gordon Growth Model
        terminal_fcf = cf * (1 + inputs.terminal_growth_rate)
        terminal_value = terminal_fcf / (inputs.wacc - inputs.terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1 + inputs.wacc) ** (current_year - 1))

        enterprise_value = pv_cf_sum + pv_terminal_value
        equity_value = enterprise_value + inputs.cash_and_equivalents - inputs.total_debt
        
        fair_value_per_share = equity_value / inputs.shares_outstanding

        diff_percent = ((fair_value_per_share - inputs.current_stock_price) / inputs.current_stock_price) * 100

        if diff_percent > 15.0:
            status = "Undervalued"
        elif diff_percent < -15.0:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

        return DCFResult(
            intrinsic_value_per_share=round(fair_value_per_share, 2),
            current_price=round(inputs.current_stock_price, 2),
            upside_downside_percent=round(diff_percent, 2),
            valuation_status=status,
            enterprise_value=round(enterprise_value, 2),
            equity_value=round(equity_value, 2),
            pv_forecast_cash_flows=round(pv_cf_sum, 2),
            pv_terminal_value=round(pv_terminal_value, 2),
            yearly_cash_flows=yearly_details,
            wacc_used=round(inputs.wacc * 100, 2)
        )

    @staticmethod
    def calculate_sensitivity(inputs: DCFInput) -> SensitivityMatrix:
        g_base = inputs.high_growth_rate
        wacc_base = inputs.wacc

        growth_rates = [round(g_base * mult, 3) for mult in [0.6, 0.8, 1.0, 1.2, 1.4]]
        discount_rates = [round(wacc_base + delta, 3) for delta in [-0.02, -0.01, 0.0, 0.01, 0.02]]

        matrix = []
        for g in growth_rates:
            row = []
            for d in discount_rates:
                temp_input = inputs.model_copy(update={"high_growth_rate": g, "wacc": d})
                res = FinancialEngine.calculate_dcf(temp_input)
                row.append(res.intrinsic_value_per_share)
            matrix.append(row)

        return SensitivityMatrix(
            growth_rates=[round(g * 100, 1) for g in growth_rates],
            discount_rates=[round(d * 100, 1) for d in discount_rates],
            matrix=matrix
        )
