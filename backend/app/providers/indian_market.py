from typing import Any, Dict

import requests

from app.tools.company_resolver import CompanyContext


class IndianMarketProvider:
    """Retrieve Indian listed quote data without inventing unavailable values."""

    @staticmethod
    def get_quote(context: CompanyContext) -> Dict[str, Any]:
        symbol = context.yahoo_symbol or f"{context.ticker}.NS"
        response = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            params={"range": "5d", "interval": "1d"},
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()["chart"]["result"][0]
        meta = result.get("meta", {})
        indicators = result.get("indicators", {})
        quote = (indicators.get("quote") or [{}])[0]
        closes = [value for value in quote.get("close", []) if value is not None]
        highs = [value for value in quote.get("high", []) if value is not None]
        lows = [value for value in quote.get("low", []) if value is not None]
        volumes = [value for value in quote.get("volume", []) if value is not None]
        price = meta.get("regularMarketPrice")
        previous_close = meta.get("previousClose")
        change = (
            price - previous_close
            if price is not None and previous_close is not None
            else None
        )
        change_percent = (
            change / previous_close * 100
            if change is not None and previous_close
            else None
        )
        return {
            "ticker": context.ticker,
            "yahoo_symbol": symbol,
            "company_name": context.company_name,
            "exchange": context.exchange,
            "sector": context.sector,
            "industry": context.industry,
            "current_stock_price": price,
            "previous_close": previous_close,
            "price_change": change,
            "price_change_percent": change_percent,
            "fifty_two_week_high": meta.get("fiftyTwoWeekHigh") or (max(highs) if highs else None),
            "fifty_two_week_low": meta.get("fiftyTwoWeekLow") or (min(lows) if lows else None),
            "volume": meta.get("regularMarketVolume") or (volumes[-1] if volumes else None),
            "currency": meta.get("currency", "INR"),
            "market_cap": None,
            "shares_outstanding": None,
            "high_growth_rate": None,
            "source": "Yahoo Finance chart API",
            "source_type": "Market data",
            "timestamp": meta.get("regularMarketTime"),
            "source_url": f"https://finance.yahoo.com/quote/{symbol}",
            "data_status": "available" if price is not None else "DATA_UNAVAILABLE",
        }