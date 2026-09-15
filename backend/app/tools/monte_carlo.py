import numpy as np
from typing import Dict, Any, List
from pydantic import BaseModel
from app.tools.financial_engine import DCFInput, FinancialEngine

class MonteCarloResult(BaseModel):
    num_simulations: int
    mean_fair_value: float
    median_fair_value: float
    std_dev: float
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float
    current_price: float
    probability_undervalued_percent: float
    histogram_bins: List[float]
    histogram_counts: List[int]
    current_price_percentile: float

class MonteCarloSimulator:
    @staticmethod
    def run_simulation(
        dcf_base_inputs: DCFInput,
        num_simulations: int = 5000,
        growth_std_dev: float = 0.05,
        wacc_std_dev: float = 0.015
    ) -> MonteCarloResult:
        np.random.seed(42) # Reproducible seed for auditability

        # Sample growth rates and WACCs from normal distributions
        sampled_growths = np.random.normal(dcf_base_inputs.high_growth_rate, growth_std_dev, num_simulations)
        sampled_waccs = np.random.normal(dcf_base_inputs.wacc, wacc_std_dev, num_simulations)

        # Enforce valid physical bounds
        sampled_growths = np.clip(sampled_growths, -0.20, 0.60)
        sampled_waccs = np.clip(sampled_waccs, 0.04, 0.20)

        results = []
        for i in range(num_simulations):
            g = float(sampled_growths[i])
            w = float(sampled_waccs[i])
            
            # Fast DCF iteration calculation
            cf = dcf_base_inputs.current_fcf
            pv_sum = 0.0
            
            for yr in range(1, dcf_base_inputs.high_growth_years + 1):
                cf *= (1 + g)
                pv_sum += cf / ((1 + w) ** yr)

            term_g = dcf_base_inputs.terminal_growth_rate
            term_wacc = max(w, term_g + 0.005)
            term_val = (cf * (1 + term_g)) / (term_wacc - term_g)
            pv_term = term_val / ((1 + w) ** dcf_base_inputs.high_growth_years)

            ev = pv_sum + pv_term
            eq_val = ev + dcf_base_inputs.cash_and_equivalents - dcf_base_inputs.total_debt
            share_val = eq_val / max(dcf_base_inputs.shares_outstanding, 0.001)
            results.append(share_val)

        arr = np.array(results)
        arr = np.nan_to_num(arr, nan=dcf_base_inputs.current_stock_price)

        mean_val = float(np.mean(arr))
        median_val = float(np.median(arr))
        std_val = float(np.std(arr))

        p5 = float(np.percentile(arr, 5))
        p25 = float(np.percentile(arr, 25))
        p50 = float(np.percentile(arr, 50))
        p75 = float(np.percentile(arr, 75))
        p95 = float(np.percentile(arr, 95))

        cur_price = dcf_base_inputs.current_stock_price
        prob_undervalued = float(np.sum(arr > cur_price) / num_simulations * 100)

        # Current price percentile in the distribution
        cur_percentile = float(np.sum(arr <= cur_price) / num_simulations * 100)

        # Build histogram data
        counts, bin_edges = np.histogram(arr, bins=25)

        return MonteCarloResult(
            num_simulations=num_simulations,
            mean_fair_value=round(mean_val, 2),
            median_fair_value=round(median_val, 2),
            std_dev=round(std_val, 2),
            percentile_5=round(p5, 2),
            percentile_25=round(p25, 2),
            percentile_50=round(p50, 2),
            percentile_75=round(p75, 2),
            percentile_95=round(p95, 2),
            current_price=round(cur_price, 2),
            probability_undervalued_percent=round(prob_undervalued, 1),
            histogram_bins=[round(float(b), 2) for b in bin_edges],
            histogram_counts=[int(c) for c in counts],
            current_price_percentile=round(cur_percentile, 1)
        )
