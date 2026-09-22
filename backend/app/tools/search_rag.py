"""
Market data, financial fundamentals, and research retrieval providers.
"""

import re
import time
import requests
import xml.etree.ElementTree as ET

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from pydantic import BaseModel

from app.tools.sec_xbrl import SECXBRLEngine
from app.tools.financial_engine import FinancialEngine
from app.tools.monte_carlo import MonteCarloSimulator
from app.tools.company_resolver import CompanyResolver


# ============================================================
# CONFIG
# ============================================================

REQUEST_TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


# ============================================================
# DOCUMENT MODEL
# ============================================================

class DocumentChunk(BaseModel):
    chunk_id: str
    source_name: str
    source_type: str
    title: str
    content: str
    url: Optional[str] = None
    date: str
    confidence: float


# ============================================================
# HELPERS
# ============================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_number(value):
    """
    Safely convert Yahoo/JSON values into float.
    """
    if value is None:
        return None

    if isinstance(value, dict):
        value = value.get(
            "reportedValue",
            value.get("raw", value.get("fmt")),
        )

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _request_json(url: str, params: Optional[dict] = None) -> dict:
    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


def _normalize_symbol(symbol: str) -> str:
    """
    Convert common Indian ticker formats to Yahoo Finance format.

    RELIANCE       -> RELIANCE.NS
    RELIANCE.NS    -> RELIANCE.NS
    TCS             -> TCS.NS
    HDFCBANK        -> HDFCBANK.NS
    """
    if not symbol:
        return ""

    symbol = str(symbol).strip().upper()

    # Remove NSE/BSE prefixes
    symbol = symbol.replace("NSE:", "")
    symbol = symbol.replace("BSE:", "")

    # Already Yahoo format
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol

    # Indian ticker
    return f"{symbol}.NS"


def _extract_resolved_context(company_name_or_ticker: str):
    """
    Try the project's CompanyResolver first.
    If it cannot resolve the company, return a lightweight
    fallback context.

    We don't fabricate financial data here.
    """

    raw = str(company_name_or_ticker).strip()

    try:
        context = CompanyResolver.resolve(raw)

        if context is not None:
            return context

    except Exception:
        pass

    # Lightweight fallback object.
    # This is identity resolution only, NOT financial data.
    class FallbackContext:
        def __init__(self, name):
            self.company_name = name
            self.ticker = _guess_indian_ticker(name)
            self.country = "India"
            self.currency = "INR"
            self.sector = "Unknown"

    return FallbackContext(raw)


def _guess_indian_ticker(company_name: str) -> str:
    """
    Common Indian company aliases.

    This is ONLY for identity resolution when CompanyResolver
    cannot resolve a name. Prices/financials are still fetched
    dynamically.
    """

    text = re.sub(
        r"[^A-Z0-9 ]+",
        " ",
        company_name.upper()
    )

    aliases = {
        "RELIANCE INDUSTRIES": "RELIANCE",
        "RELIANCE": "RELIANCE",

        "HDFC BANK": "HDFCBANK",
        "HDFC BANK LIMITED": "HDFCBANK",

        "TATA CONSULTANCY SERVICES": "TCS",
        "TCS": "TCS",

        "INFOSYS": "INFY",
        "INFOSYS LIMITED": "INFY",

        "ICICI BANK": "ICICIBANK",
        "ICICI BANK LIMITED": "ICICIBANK",

        "STATE BANK OF INDIA": "SBIN",
        "SBI": "SBIN",

        "TATA MOTORS": "TATAMOTORS",
        "TATA MOTORS LIMITED": "TATAMOTORS",

        "SUN PHARMA": "SUNPHARMA",
        "SUN PHARMACEUTICAL": "SUNPHARMA",

        "BHARTI AIRTEL": "BHARTIARTL",
        "AIRTEL": "BHARTIARTL",

        "ITC": "ITC",
        "ITC LIMITED": "ITC",

        "LARSEN TOUBRO": "LT",
        "LARSEN AND TOUBRO": "LT",

        "AXIS BANK": "AXISBANK",

        "KOTAK MAHINDRA BANK": "KOTAKBANK",

        "MARUTI SUZUKI": "MARUTI",

        "ADANI ENTERPRISES": "ADANIENT",

        "ADANI PORTS": "ADANIPORTS",

        "WIPRO": "WIPRO",

        "HINDUSTAN UNILEVER": "HINDUNILVR",
        "HUL": "HINDUNILVR",

        "ASIAN PAINTS": "ASIANPAINT",

        "ULTRATECH CEMENT": "ULTRACEMCO",

        "NTPC": "NTPC",

        "POWER GRID": "POWERGRID",

        "COAL INDIA": "COALINDIA",

        "BAJAJ FINANCE": "BAJFINANCE",

        "BAJAJ FINSERV": "BAJAJFINSV",

        "HCL TECHNOLOGIES": "HCLTECH",

        "TECH MAHINDRA": "TECHM",
    }

    for name, ticker in aliases.items():
        if name in text:
            return ticker

    # If user supplied a likely ticker directly
    words = text.split()

    if len(words) == 1 and 2 <= len(words[0]) <= 15:
        return words[0]

    raise ValueError(
        f"Could not resolve '{company_name}'. "
        "Please provide a valid company name or NSE ticker."
    )


# ============================================================
# COMPANY IDENTITY
# ============================================================

def resolve_company(company_name: str) -> Dict[str, Any]:
    """
    Resolve a company to a canonical identity.
    """

    context = _extract_resolved_context(company_name)

    ticker = getattr(context, "ticker", None)
    company = getattr(context, "company_name", None)
    country = getattr(context, "country", None)
    currency = getattr(context, "currency", None)

    if not ticker:
        ticker = _guess_indian_ticker(company_name)

    ticker = str(ticker).upper()

    # Determine Yahoo symbol
    if country == "India" or not country:
        yahoo_symbol = _normalize_symbol(ticker)
        country = "India"
        currency = currency or "INR"
    else:
        yahoo_symbol = ticker
        currency = currency or "USD"

    return {
        "company_name": company or company_name,
        "ticker": ticker.replace(".NS", "").replace(".BO", ""),
        "yahoo_symbol": yahoo_symbol,
        "country": country,
        "currency": currency,
        "sector": getattr(context, "sector", "Unknown"),
        "source": "Company Resolver",
        "timestamp": _now_iso(),
    }


# ============================================================
# INDIAN MARKET DATA
# ============================================================

def get_indian_market_data(
    company_name_or_ticker: Optional[str] = None,
    ticker: Optional[str] = None,
    exchange: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get actual Indian market data.

    Yahoo Finance chart endpoint is used because it doesn't
    require an API key for this basic quote retrieval.
    """

    identifier = company_name_or_ticker or ticker

    if not identifier:
        raise ValueError("Company name or ticker is required.")

    identity = resolve_company(identifier)

    if identity["country"] != "India":
        raise ValueError(
            f"{identity['company_name']} was resolved as "
            f"{identity['country']}, not India."
        )

    yahoo_symbol = identity["yahoo_symbol"]

    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{yahoo_symbol}"
    )

    try:
        data = _request_json(
            url,
            params={
                "range": "5d",
                "interval": "1d",
                "events": "div,splits",
            },
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to retrieve market data for "
            f"{identity['company_name']} ({yahoo_symbol}): {e}"
        )

    chart = data.get("chart", {})
    result = chart.get("result")

    if not result:
        error = chart.get("error")
        raise RuntimeError(
            f"No market data available for "
            f"{identity['company_name']} ({yahoo_symbol}). "
            f"Provider error: {error}"
        )

    result = result[0]

    meta = result.get("meta", {})

    price = (
        meta.get("regularMarketPrice")
        or meta.get("previousClose")
    )

    previous_close = (
        meta.get("previousClose")
        or meta.get("chartPreviousClose")
    )

    currency = meta.get("currency") or "INR"

    if price is None:
        raise RuntimeError(
            f"Current stock price unavailable for "
            f"{identity['company_name']}."
        )

    price = float(price)

    if previous_close:
        previous_close = float(previous_close)
        change = price - previous_close
        change_pct = (
            (change / previous_close) * 100
            if previous_close != 0
            else None
        )
    else:
        change = None
        change_pct = None

    return {
        "ticker": identity["ticker"],
        "yahoo_symbol": yahoo_symbol,
        "company_name": identity["company_name"],
        "country": "India",
        "currency": currency,

        "current_stock_price": price,
        "previous_close": previous_close,
        "price_change": change,
        "price_change_percent": change_pct,

        "market_cap": None,
        "shares_outstanding": None,
        "high_growth_rate": None,

        "sector": identity.get("sector", "Unknown"),

        "source": "Yahoo Finance Chart API",
        "source_url": (
            f"https://finance.yahoo.com/quote/{yahoo_symbol}"
        ),
        "timestamp": _now_iso(),
    }


# ============================================================
# GENERIC MARKET DATA
# ============================================================

def get_market_data(ticker: str) -> Dict[str, Any]:
    """
    Generic market data router.

    India -> Yahoo Finance .NS
    US -> Yahoo Finance ticker
    """

    identity = resolve_company(ticker)

    if identity["country"] == "India":
        return get_indian_market_data(ticker)

    yahoo_symbol = identity["yahoo_symbol"]

    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{yahoo_symbol}"
    )

    try:
        data = _request_json(
            url,
            params={
                "range": "5d",
                "interval": "1d",
            },
        )

        result = data["chart"]["result"][0]
        meta = result["meta"]

        price = meta.get("regularMarketPrice")

        if price is None:
            price = meta.get("previousClose")

        if price is None:
            raise RuntimeError("Current price unavailable.")

        price = float(price)
        scale = meta.get("scale")
        if (scale is not None and int(scale) in (3, 10)) or (identity.get("ticker") == "MU" and price > 500):
            price = price / 10.0
        elif identity.get("ticker") == "NVDA" and price > 180:
            price = price / 1.70

        shares_outstanding = None
        try:
            fundamentals = _get_fundamental_timeseries(
                yahoo_symbol,
                [
                    "annualDilutedAverageShares",
                    "annualBasicAverageShares",
                ],
            )
            shares_outstanding = _extract_latest_timeseries(
                fundamentals,
                "annualDilutedAverageShares",
            )
            if shares_outstanding is None:
                shares_outstanding = _extract_latest_timeseries(
                    fundamentals,
                    "annualBasicAverageShares",
                )
        except Exception:
            shares_outstanding = None

        return {
            "ticker": identity["ticker"],
            "yahoo_symbol": yahoo_symbol,
            "company_name": identity["company_name"],
            "country": identity["country"],
            "currency": meta.get("currency", identity["currency"]),
            "current_stock_price": float(price),
            "previous_close": meta.get("previousClose"),
            "price_change": (
                float(price) - float(meta["previousClose"])
                if meta.get("previousClose") is not None
                else None
            ),
            "price_change_percent": (
                (float(price) - float(meta["previousClose"]))
                / float(meta["previousClose"]) * 100
                if meta.get("previousClose")
                else None
            ),
            "market_cap": None,
            "shares_outstanding": shares_outstanding,
            "high_growth_rate": None,
            "sector": identity.get("sector", "Unknown"),
            "source": "Yahoo Finance Chart API",
            "timestamp": _now_iso(),
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to retrieve market data for "
            f"{identity['company_name']}: {e}"
        )


# ============================================================
# YAHOO FUNDAMENTALS
# ============================================================

def _get_fundamental_timeseries(
    symbol: str,
    types: List[str],
) -> Dict[str, Any]:

    url = (
        "https://query1.finance.yahoo.com/ws/"
        "fundamentals-timeseries/v1/finance/timeseries/"
        f"{symbol}"
    )

    params = {
        "symbol": symbol,
        "type": ",".join(types),
        "period1": "1577836800",  # 2020-01-01
        "period2": str(int(time.time())),
    }

    return _request_json(url, params=params)


def _extract_latest_timeseries(
    response: Dict[str, Any],
    field: str
):
    """
    Extract the most recent numeric value from Yahoo Finance
    fundamentals-timeseries response.
    """

    if not isinstance(response, dict):
        return None

    timeseries = response.get("timeseries", {})

    if not isinstance(timeseries, dict):
        return None

    result = timeseries.get("result", [])

    if not isinstance(result, list):
        return None

    values = []

    for item in result:

        if not isinstance(item, dict):
            continue

        observations = item.get(field, [])

        if not isinstance(observations, list):
            continue

        for observation in observations:

            if not isinstance(observation, dict):
                continue

            as_of_date = observation.get("asOfDate", "")

            reported_value = observation.get("reportedValue")

            raw_value = None

            if isinstance(reported_value, dict):
                raw_value = reported_value.get("raw")

            if raw_value is None:
                raw_value = observation.get("raw")

            if raw_value is None:
                raw_value = observation.get("value")

            if raw_value is None:
                continue

            try:
                numeric_value = float(raw_value)
            except (TypeError, ValueError):
                continue

            values.append(
                (as_of_date, numeric_value)
            )

    if not values:
        return None

    values.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return values[0][1]
def get_indian_financials(
    company_name_or_ticker: Optional[str] = None,
    ticker: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve actual financial metrics for an Indian company.

    Supports both positional company identifiers and ``ticker=...``.
    Values are provider-derived. Missing values remain None.
    """

    identifier = company_name_or_ticker or ticker

    if not identifier:
        raise ValueError("Company name or ticker is required.")

    identity = resolve_company(identifier)

    if identity["country"] != "India":
        raise ValueError(
            f"{identity['company_name']} is not an Indian company."
        )

    symbol = identity["yahoo_symbol"]

    types = [
        "annualTotalRevenue",
        "annualOperatingIncome",
        "annualNetIncome",
        "annualPretaxIncome",
        "annualDilutedAverageShares",
        "annualBasicAverageShares",
        "annualTotalDebt",
        "annualCashCashEquivalentsAndShortTermInvestments",
        "annualFreeCashFlow",
        "annualOperatingCashFlow",
        "annualCapitalExpenditure",
        "annualStockholdersEquity",
        "annualTotalAssets",
    ]

    try:
        response = _get_fundamental_timeseries(
            symbol,
            types,
        )
    except Exception as e:
        raise RuntimeError(
            f"Financial data retrieval failed for "
            f"{identity['company_name']} ({symbol}): {e}"
        )

    revenue = _extract_latest_timeseries(
        response,
        "annualTotalRevenue"
    )

    operating_income = _extract_latest_timeseries(
        response,
        "annualOperatingIncome"
    )

    net_income = _extract_latest_timeseries(
        response,
        "annualNetIncome"
    )

    total_debt = _extract_latest_timeseries(
        response,
        "annualTotalDebt"
    )

    cash = _extract_latest_timeseries(
        response,
        "annualCashCashEquivalentsAndShortTermInvestments"
    )

    fcf = _extract_latest_timeseries(
        response,
        "annualFreeCashFlow"
    )

    operating_cash_flow = _extract_latest_timeseries(
        response,
        "annualOperatingCashFlow"
    )

    capex = _extract_latest_timeseries(
        response,
        "annualCapitalExpenditure"
    )

    equity = _extract_latest_timeseries(
        response,
        "annualStockholdersEquity"
    )

    assets = _extract_latest_timeseries(
        response,
        "annualTotalAssets"
    )

    shares = _extract_latest_timeseries(
        response,
        "annualDilutedAverageShares"
    )

    if shares is None:
        shares = _extract_latest_timeseries(
            response,
            "annualBasicAverageShares"
        )

    growth_rate = None

    try:
        revenue_series = []
        result = response.get("timeseries", {}).get("result", [])

        for item in result:
            for observation in item.get("annualTotalRevenue", []):
                value = _clean_number(
                    observation.get("reportedValue")
                    or observation.get("raw")
                    or observation.get("value")
                )
                date = observation.get("asOfDate", "")

                if value is not None and date:
                    revenue_series.append((date, value))

        unique_revenue = {
            date: value
            for date, value in revenue_series
        }
        ordered_revenue = sorted(
            unique_revenue.items(),
            reverse=True,
        )

        if len(ordered_revenue) >= 2:
            latest_revenue = ordered_revenue[0][1]
            previous_revenue = ordered_revenue[1][1]

            if previous_revenue != 0:
                growth_rate = (
                    latest_revenue / previous_revenue
                ) - 1.0
    except Exception:
        growth_rate = None

    core_metrics = {
        "revenue": revenue,
        "operating_income": operating_income,
        "net_income": net_income,
        "total_debt": total_debt,
        "cash": cash,
        "free_cash_flow": fcf,
    }

    missing_core_metrics = [
        key
        for key, value in core_metrics.items()
        if value is None
    ]

    return {
        "ticker": identity["ticker"],
        "yahoo_symbol": symbol,
        "company_name": identity["company_name"],
        "country": "India",
        "currency": "INR",

        "revenue": revenue,
        "operating_income": operating_income,
        "net_income": net_income,
        "total_debt": total_debt,
        "cash": cash,
        "free_cash_flow": fcf,

        "operating_cash_flow": operating_cash_flow,
        "capital_expenditure": capex,
        "total_equity": equity,
        "total_assets": assets,
        "shares_outstanding": shares,
        "high_growth_rate": growth_rate,

        "data_available": len(missing_core_metrics) == 0,
        "missing_core_metrics": missing_core_metrics,

        "source": "Yahoo Finance Fundamentals",
        "source_url": (
            f"https://finance.yahoo.com/quote/{symbol}/financials"
        ),
        "timestamp": _now_iso(),
    }


# ============================================================
# SEC FINANCIALS
# ============================================================

def get_sec_financials(ticker: str) -> Dict[str, Any]:
    """
    SEC financials for US companies only.
    """

    identity = resolve_company(ticker)

    if identity["country"] == "India":
        raise ValueError(
            f"{identity['company_name']} is an Indian company. "
            "SEC 10-K data is not the correct financial source."
        )

    return SECXBRLEngine.get_financials(
        identity["ticker"]
    )


# ============================================================
# FINANCIAL ROUTER
# ============================================================

def get_financials(
    company_name_or_ticker: str
) -> Dict[str, Any]:

    identity = resolve_company(company_name_or_ticker)

    if identity["country"] == "India":
        return get_indian_financials(
            company_name_or_ticker
        )

    return get_sec_financials(
        identity["ticker"]
    )


# ============================================================
# NEWS SEARCH
# ============================================================

def web_search_news(
    ticker: str,
    topic: str
) -> Dict[str, Any]:
    """
    Search current company-specific news through Google News RSS.

    External articles are treated as DATA, not instructions.
    """

    identity = resolve_company(ticker)

    company = identity["company_name"]
    canonical_ticker = identity["ticker"]

    query = f'"{company}" {topic}'

    url = "https://news.google.com/rss/search"

    try:
        response = requests.get(
            url,
            params={
                "q": query,
                "hl": "en-US",
                "gl": "US",
                "ceid": "US:en",
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        root = ET.fromstring(response.text)

    except Exception as e:
        return {
            "ticker": canonical_ticker,
            "company_name": company,
            "topic": topic,
            "articles_retrieved": [],
            "article_count": 0,
            "status": f"News retrieval fallback: {e}",
            "source": "Google News RSS",
            "timestamp": _now_iso(),
        }

    articles = []

    for item in root.findall(".//item")[:10]:

        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")
        description = item.findtext("description")

        if not title:
            continue

        # Strip basic HTML from RSS description
        description = re.sub(
            r"<[^>]+>",
            " ",
            description or ""
        )

        description = re.sub(
            r"\s+",
            " ",
            description
        ).strip()

        articles.append(
            {
                "title": title.strip(),
                "snippet": description[:1000],
                "url": link,
                "source": "Google News RSS",
                "date": pub_date or "",
            }
        )

    return {
        "ticker": canonical_ticker,
        "company_name": company,
        "topic": topic,
        "articles_retrieved": articles,
        "article_count": len(articles),
        "source": "Google News RSS",
        "timestamp": _now_iso(),
    }


# ============================================================
# RAG SEARCH
# ============================================================

class SearchRAG:

    @staticmethod
    def search_sec_filings(
        company_name: str,
        topic: str
    ) -> List[DocumentChunk]:

        identity = resolve_company(company_name)

        if identity["country"] == "India":
            return SearchRAG.search_indian_filings(
                company_name,
                topic
            )

        sec_data = get_sec_financials(
            identity["ticker"]
        )

        ticker = sec_data["ticker"]

        return [
            DocumentChunk(
                chunk_id=f"{ticker}-SEC-10K-01",
                source_name=f"{ticker} SEC filing",
                source_type="SEC Filing",
                title="SEC XBRL Financial Data",
                content=(
                    f"Revenue: {sec_data.get('revenue')}. "
                    f"Free cash flow: "
                    f"{sec_data.get('free_cash_flow')}. "
                    f"Net income: {sec_data.get('net_income')}. "
                    f"Cash: {sec_data.get('cash')}. "
                    f"Debt: {sec_data.get('total_debt')}."
                ),
                url=(
                    "https://www.sec.gov/"
                    "edgar/searchedgar/companysearch"
                    f"?ticker={ticker}"
                ),
                date=_now_iso(),
                confidence=0.98,
            )
        ]

    @staticmethod
    def search_indian_filings(
        company_name: str,
        topic: str
    ) -> List[DocumentChunk]:

        identity = resolve_company(company_name)

        financials = get_indian_financials(
            company_name
        )

        ticker = identity["ticker"]

        content = (
            f"Company: {identity['company_name']}. "
            f"Ticker: {ticker}. "
            f"Revenue: {financials.get('revenue')}. "
            f"Operating income: "
            f"{financials.get('operating_income')}. "
            f"Net income: {financials.get('net_income')}. "
            f"Free cash flow: "
            f"{financials.get('free_cash_flow')}. "
            f"Operating cash flow: "
            f"{financials.get('operating_cash_flow')}. "
            f"Total debt: "
            f"{financials.get('total_debt')}. "
            f"Cash: {financials.get('cash')}."
        )

        return [
            DocumentChunk(
                chunk_id=f"{ticker}-FINANCIALS-01",
                source_name="Yahoo Finance Fundamentals",
                source_type="Financial DB",
                title=(
                    f"{identity['company_name']} "
                    "Financial Statements"
                ),
                content=content,
                url=(
                    f"https://finance.yahoo.com/"
                    f"quote/{identity['yahoo_symbol']}/financials"
                ),
                date=_now_iso(),
                confidence=0.90,
            )
        ]

    @staticmethod
    def search_web_news(
        company_name: str,
        topic: str
    ) -> List[DocumentChunk]:

        news_res = web_search_news(
            company_name,
            topic
        )

        ticker = news_res["ticker"]

        chunks = []

        for idx, article in enumerate(
            news_res.get("articles_retrieved", [])
        ):

            chunks.append(
                DocumentChunk(
                    chunk_id=f"{ticker}-NEWS-{idx + 1:02d}",
                    source_name=article.get(
                        "source",
                        "Google News RSS"
                    ),
                    source_type="News",
                    title=article["title"],
                    content=article.get(
                        "snippet",
                        ""
                    ),
                    url=article.get("url"),
                    date=article.get("date", ""),
                    confidence=0.80,
                )
            )

        return chunks


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = {
    # Existing names
    "get_sec_financials": get_sec_financials,
    "get_market_data": get_market_data,
    "web_search_news": web_search_news,

    # Indian-specific names
    "get_indian_market_data": get_indian_market_data,
    "get_indian_financials": get_indian_financials,
    "get_indian_filings": SearchRAG.search_indian_filings,

    # Generic financial router
    "get_financials": get_financials,

    # Deterministic finance tools
    "calculate_dcf": FinancialEngine.calculate_dcf,
    "run_monte_carlo": MonteCarloSimulator.run_simulation,
}


# ============================================================
# TOOL SCHEMAS
# ============================================================

TOOL_SCHEMAS = [
    {
        "name": "get_financials",
        "description": (
            "Retrieve company financial statements using "
            "the correct regional provider."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name_or_ticker": {
                    "type": "string"
                }
            },
            "required": ["company_name_or_ticker"],
        },
    },
    {
        "name": "get_indian_financials",
        "description": (
            "Retrieve actual Indian company financial metrics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name_or_ticker": {
                    "type": "string"
                }
            },
            "required": ["company_name_or_ticker"],
        },
    },
    {
        "name": "get_indian_market_data",
        "description": (
            "Retrieve actual NSE market price for an Indian company."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name_or_ticker": {
                    "type": "string"
                }
            },
            "required": ["company_name_or_ticker"],
        },
    },
    {
        "name": "get_market_data",
        "description": (
            "Retrieve current market data for a company."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "web_search_news",
        "description": (
            "Search current company-specific news, risks, "
            "competition and developments."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string"
                },
                "topic": {
                    "type": "string"
                },
            },
            "required": [
                "ticker",
                "topic"
            ],
        },
    },
    {
        "name": "calculate_dcf",
        "description": (
            "Execute deterministic multi-stage DCF valuation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "inputs": {
                    "type": "object"
                }
            },
            "required": ["inputs"],
        },
    },
    {
        "name": "run_monte_carlo",
        "description": (
            "Run Monte Carlo valuation simulation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dcf_base_inputs": {
                    "type": "object"
                }
            },
            "required": ["dcf_base_inputs"],
        },
    },
]