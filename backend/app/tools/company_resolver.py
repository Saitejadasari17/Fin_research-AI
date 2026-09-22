from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, Optional


@dataclass
class CompanyContext:
    query: str
    company_name: str
    ticker: str
    cik: Optional[str] = None
    exchange: Optional[str] = None
    bse_code: Optional[str] = None
    isin: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "India"
    currency: str = "INR"
    nse_symbol: Optional[str] = None
    yahoo_symbol: Optional[str] = None

    @property
    def legal_name(self) -> str:
        return self.company_name


class CompanyResolver:
    """Resolve a user-friendly company string to canonical company metadata."""

    ALIAS_MAP: Dict[str, str] = {
        "RELIANCE": "RELIANCE",
        "RELIANCE INDUSTRIES": "RELIANCE",
        "500325": "RELIANCE",
        "TCS": "TCS",
        "TATA CONSULTANCY SERVICES": "TCS",
        "532540": "TCS",
        "HDFC BANK": "HDFCBANK",
        "HDFCBANK": "HDFCBANK",
        "500180": "HDFCBANK",
        "ICICI BANK": "ICICIBANK",
        "ICICIBANK": "ICICIBANK",
        "532174": "ICICIBANK",
        "INFOSYS": "INFY",
        "INFY": "INFY",
        "500209": "INFY",
        "TATA MOTORS": "TATAMOTORS",
        "TATAMOTORS": "TATAMOTORS",
        "500570": "TATAMOTORS",
        "SUN PHARMA": "SUNPHARMA",
        "SUNPHARMA": "SUNPHARMA",
        "524715": "SUNPHARMA",
        "BHARTI AIRTEL": "BHARTIARTL",
        "BHARTIARTL": "BHARTIARTL",
        "532454": "BHARTIARTL",
        "LARSEN & TOUBRO": "LT",
        "L&T": "LT",
        "LT": "LT",
        "500510": "LT",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "GOOG": "GOOGL",
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "AMAZON": "AMZN",
        "META": "META",
        "FACEBOOK": "META",
        "TESLA": "TSLA",
        "NVIDIA": "NVDA",
        "AMD": "AMD",
        "INTEL": "INTC",
        "INTC": "INTC",
        "NETFLIX": "NFLX",
        "MICRON": "MU",
        "MICRON TECHNOLOGY": "MU",
        "MU": "MU",
        "BROADCOM": "AVGO",
        "AVGO": "AVGO",
        "QUALCOMM": "QCOM",
        "QCOM": "QCOM",
        "TSMC": "TSM",
        "TAIWAN SEMICONDUCTOR": "TSM",
        "TSM": "TSM",
        "ASML": "ASML",
        "ARM": "ARM",
        "ARM HOLDINGS": "ARM",
    }

    COMPANY_METADATA: Dict[str, Dict[str, str]] = {
        "RELIANCE": {"company_name": "Reliance Industries Limited", "ticker": "RELIANCE", "bse_code": "500325", "isin": "INE002A01018", "exchange": "NSE/BSE", "sector": "Conglomerate", "industry": "Diversified Operations"},
        "TCS": {"company_name": "Tata Consultancy Services Limited", "ticker": "TCS", "bse_code": "532540", "isin": "INE467B01029", "exchange": "NSE/BSE", "sector": "Information Technology", "industry": "IT Services"},
        "HDFCBANK": {"company_name": "HDFC Bank Limited", "ticker": "HDFCBANK", "bse_code": "500180", "isin": "INE040A01034", "exchange": "NSE/BSE", "sector": "Financials", "industry": "Banking"},
        "ICICIBANK": {"company_name": "ICICI Bank Limited", "ticker": "ICICIBANK", "bse_code": "532174", "isin": "INE090A01021", "exchange": "NSE/BSE", "sector": "Financials", "industry": "Banking"},
        "INFY": {"company_name": "Infosys Limited", "ticker": "INFY", "bse_code": "500209", "isin": "INE009A01021", "exchange": "NSE/BSE", "sector": "Information Technology", "industry": "IT Services"},
        "TATAMOTORS": {"company_name": "Tata Motors Limited", "ticker": "TATAMOTORS", "bse_code": "500570", "isin": "INE155A01022", "exchange": "NSE/BSE", "sector": "Automotive", "industry": "Automobiles"},
        "SUNPHARMA": {"company_name": "Sun Pharmaceutical Industries Limited", "ticker": "SUNPHARMA", "bse_code": "524715", "isin": "INE044A01036", "exchange": "NSE/BSE", "sector": "Pharmaceuticals", "industry": "Pharmaceuticals"},
        "BHARTIARTL": {"company_name": "Bharti Airtel Limited", "ticker": "BHARTIARTL", "bse_code": "532454", "isin": "INE397D01024", "exchange": "NSE/BSE", "sector": "Telecommunications", "industry": "Telecom Services"},
        "LT": {"company_name": "Larsen & Toubro Limited", "ticker": "LT", "bse_code": "500510", "isin": "INE018A01030", "exchange": "NSE/BSE", "sector": "Engineering", "industry": "Construction & Engineering"},
        "NVDA": {"company_name": "NVIDIA Corporation", "ticker": "NVDA", "cik": "0001045810", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
        "MU": {"company_name": "Micron Technology, Inc.", "ticker": "MU", "cik": "0000723125", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors & Memory"},
        "TSLA": {"company_name": "Tesla, Inc.", "ticker": "TSLA", "cik": "0001318605", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
        "GOOGL": {"company_name": "Alphabet Inc.", "ticker": "GOOGL", "cik": "0001652044", "exchange": "NASDAQ", "sector": "Communication Services", "industry": "Internet Content & Information"},
        "AAPL": {"company_name": "Apple Inc.", "ticker": "AAPL", "cik": "0000320193", "exchange": "NASDAQ", "sector": "Technology", "industry": "Consumer Electronics"},
        "MSFT": {"company_name": "Microsoft Corporation", "ticker": "MSFT", "cik": "0000789019", "exchange": "NASDAQ", "sector": "Technology", "industry": "Systems Software"},
        "AMZN": {"company_name": "Amazon.com, Inc.", "ticker": "AMZN", "cik": "0001018724", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
        "META": {"company_name": "Meta Platforms, Inc.", "ticker": "META", "cik": "0001326801", "exchange": "NASDAQ", "sector": "Communication Services", "industry": "Internet Content & Information"},
        "AMD": {"company_name": "Advanced Micro Devices, Inc.", "ticker": "AMD", "cik": "0000002488", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
        "AVGO": {"company_name": "Broadcom Inc.", "ticker": "AVGO", "cik": "0001730168", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
        "QCOM": {"company_name": "Qualcomm Incorporated", "ticker": "QCOM", "cik": "0000804328", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
        "TSM": {"company_name": "Taiwan Semiconductor Manufacturing Company Limited", "ticker": "TSM", "cik": "0001046170", "exchange": "NYSE", "sector": "Technology", "industry": "Semiconductors"},
        "ASML": {"company_name": "ASML Holding N.V.", "ticker": "ASML", "cik": "0000937966", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductor Equipment"},
        "ARM": {"company_name": "Arm Holdings plc", "ticker": "ARM", "cik": "0001979040", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
        "INTC": {"company_name": "Intel Corporation", "ticker": "INTC", "cik": "0000050863", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
    }

    @classmethod
    def normalize_ticker(cls, query: str) -> str:
        cleaned = re.sub(r"\s+", " ", (query or "").strip().upper())
        if not cleaned:
            return ""
        if cleaned in cls.ALIAS_MAP:
            return cls.ALIAS_MAP[cleaned]
        for alias, ticker in cls.ALIAS_MAP.items():
            if alias in cleaned:
                return ticker
        normalized = cleaned.replace(".", "").replace(",", "")
        for alias, ticker in cls.ALIAS_MAP.items():
            if alias in normalized:
                return ticker
        return normalized

    @classmethod
    def resolve(cls, query: str) -> CompanyContext:
        if not query or not query.strip():
            raise ValueError("Company name or ticker is required.")

        raw_query = query.strip()
        ticker = cls.normalize_ticker(raw_query)
        metadata = cls.COMPANY_METADATA.get(ticker)

        if metadata:
            is_us_company = metadata.get("cik") is not None or metadata.get("country") == "United States"
            country = metadata.get(
                "country",
                "United States" if is_us_company else "India",
            )
            currency = "USD" if is_us_company else "INR"
            nse_symbol = None if is_us_company else metadata["ticker"]
            yahoo_symbol = (
                metadata["ticker"]
                if is_us_company
                else f"{metadata['ticker']}.NS"
            )

            return CompanyContext(
                query=raw_query,
                company_name=metadata["company_name"],
                ticker=metadata["ticker"],
                cik=metadata.get("cik"),
                exchange=metadata.get("exchange"),
                bse_code=metadata.get("bse_code"),
                isin=metadata.get("isin"),
                sector=metadata.get("sector"),
                industry=metadata.get("industry"),
                country=country,
                currency=currency,
                nse_symbol=nse_symbol,
                yahoo_symbol=yahoo_symbol,
            )

        # Fallback for standard US tickers not explicitly in metadata dictionary
        if re.match(r"^[A-Z]{1,5}$", ticker):
            return CompanyContext(
                query=raw_query,
                company_name=raw_query.upper(),
                ticker=ticker,
                cik=None,
                exchange="US Equity",
                country="United States",
                currency="USD",
                nse_symbol=None,
                yahoo_symbol=ticker,
            )

        raise ValueError(f"Company could not be resolved: {raw_query}")
