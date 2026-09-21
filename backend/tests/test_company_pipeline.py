from app.tools.company_resolver import CompanyResolver, CompanyContext
from app.core.orchestrator import DynamicOrchestrator
import pytest


def test_company_resolver_resolves_aliases():
    google = CompanyResolver.resolve("Google")
    assert google.company_name == "Alphabet Inc."
    assert google.ticker == "GOOGL"
    assert google.cik is not None

    nvidia = CompanyResolver.resolve("NVIDIA")
    assert nvidia.company_name == "NVIDIA Corporation"
    assert nvidia.ticker == "NVDA"
    assert nvidia.cik == "0001045810"


def test_company_resolver_resolves_indian_aliases_and_identifiers():
    reliance = CompanyResolver.resolve("Reliance Industries")
    assert reliance.company_name == "Reliance Industries Limited"
    assert reliance.ticker == "RELIANCE"
    assert reliance.bse_code == "500325"
    assert reliance.country == "India"

    bank = CompanyResolver.resolve("500180")
    assert bank.company_name == "HDFC Bank Limited"
    assert bank.ticker == "HDFCBANK"
    assert bank.industry == "Banking"


def test_company_resolver_rejects_unknown_input():
    with pytest.raises(ValueError, match="Company could not be resolved"):
        CompanyResolver.resolve("asdfgh")


def test_orchestrator_uses_canonical_context_for_company_specific_research():
    report = DynamicOrchestrator().run_investigation("NVIDIA", max_iterations=3)

    assert report.company_name == "NVIDIA Corporation"
    assert report.ticker == "NVDA"
    assert report.financial_metrics is not None
    assert report.dcf_result.intrinsic_value_per_share > 0


def test_market_data_is_company_specific_not_static_template():
    nvidia = CompanyResolver.resolve("NVIDIA")
    from app.tools.search_rag import get_market_data

    market = get_market_data(nvidia.ticker)
    assert market["ticker"] == "NVDA"
    assert market["sector"]
    assert market["current_stock_price"] > 0
    assert market["shares_outstanding"] > 0


def test_indian_market_provider_preserves_unavailable_values(monkeypatch):
    from app.providers.indian_market import IndianMarketProvider

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"chart": {"result": [{"meta": {
                "regularMarketPrice": 2500.0,
                "previousClose": 2480.0,
                "currency": "INR",
                "regularMarketTime": 1789475400,
            }}]}}

    monkeypatch.setattr("app.providers.indian_market.requests.get", lambda *args, **kwargs: FakeResponse())
    market = IndianMarketProvider.get_quote(CompanyResolver.resolve("TCS"))

    assert market["ticker"] == "TCS"
    assert market["currency"] == "INR"
    assert market["current_stock_price"] == 2500.0
    assert market["market_cap"] is None
    assert market["shares_outstanding"] is None
