from typing import Dict, Any, Optional, List
import requests


SEC_HEADERS = {
    "User-Agent": "FinResearchAI research contact@example.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value: Any) -> Optional[float]:
    """
    Convert a value to float safely.
    """
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _get_company_facts(cik: str) -> Dict[str, Any]:
    """
    Retrieve SEC companyfacts XBRL data.
    """

    cik_padded = str(cik).zfill(10)

    url = (
        f"https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik_padded}.json"
    )

    response = requests.get(
        url,
        headers=SEC_HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def _get_fact_series(
    facts: Dict[str, Any],
    namespace: str,
    tags: List[str],
) -> Dict[str, Any]:
    """
    Find the first available XBRL tag from a list.
    """

    namespace_facts = (
        facts.get("facts", {})
        .get(namespace, {})
    )

    for tag in tags:

        fact = namespace_facts.get(tag)

        if fact:
            return fact

    return {}


def _get_latest_fact_value(
    fact: Dict[str, Any],
    preferred_forms: Optional[List[str]] = None,
) -> Optional[float]:
    """
    Extract the latest usable USD fact.

    Preference:
        1. 10-K annual facts
        2. latest annual-compatible fact
        3. latest available fact
    """

    if not fact:
        return None

    units = fact.get("units", {})

    # Most US financial statement values are USD.
    unit_data = (
        units.get("USD")
        or units.get("shares")
        or units.get("USD/shares")
    )

    if not unit_data:
        return None

    preferred_forms = (
        preferred_forms
        or ["10-K", "10-K/A"]
    )

    # --------------------------------------------------------
    # First preference: annual 10-K values
    # --------------------------------------------------------

    annual_candidates = [
        item
        for item in unit_data
        if item.get("form") in preferred_forms
        and item.get("val") is not None
    ]

    if annual_candidates:

        annual_candidates.sort(
            key=lambda x: (
                x.get("fy") or 0,
                x.get("filed") or "",
            ),
            reverse=True,
        )

        value = _safe_float(
            annual_candidates[0].get("val")
        )

        if value is not None:
            return value

    # --------------------------------------------------------
    # Fallback: latest available value
    # --------------------------------------------------------

    candidates = [
        item
        for item in unit_data
        if item.get("val") is not None
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            x.get("filed") or "",
            x.get("end") or "",
        ),
        reverse=True,
    )

    return _safe_float(
        candidates[0].get("val")
    )


def _get_latest_balance_sheet_value(
    fact: Dict[str, Any],
) -> Optional[float]:
    """
    Extract the latest balance-sheet value.

    Balance-sheet facts are point-in-time values, so we prefer
    the latest filed annual/quarterly fact.
    """

    if not fact:
        return None

    units = fact.get("units", {})

    unit_data = units.get("USD")

    if not unit_data:
        return None

    candidates = [
        item
        for item in unit_data
        if item.get("val") is not None
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            x.get("filed") or "",
            x.get("end") or "",
        ),
        reverse=True,
    )

    return _safe_float(
        candidates[0].get("val")
    )


def _find_fact_value(
    facts: Dict[str, Any],
    tags: List[str],
    balance_sheet: bool = False,
) -> Optional[float]:
    """
    Try multiple XBRL tags until a usable value is found.
    """

    fact = _get_fact_series(
        facts,
        "us-gaap",
        tags,
    )

    if not fact:
        return None

    if balance_sheet:
        return _get_latest_balance_sheet_value(
            fact
        )

    return _get_latest_fact_value(
        fact
    )


# ============================================================
# FINANCIAL EXTRACTION
# ============================================================

def get_sec_financials(
    ticker: str,
) -> Dict[str, Any]:
    """
    Retrieve company financial data from SEC EDGAR XBRL.

    Returned financial values are normalized to:
        USD millions

    Fields:
        revenue
        net_income
        operating_income
        free_cash_flow
        total_debt
        cash
        shares_outstanding
    """

    ticker = (
        str(ticker)
        .strip()
        .upper()
    )

    # --------------------------------------------------------
    # Resolve ticker -> CIK
    # --------------------------------------------------------

    ticker_url = (
        "https://www.sec.gov/files/"
        "company_tickers.json"
    )

    response = requests.get(
        ticker_url,
        headers={
            "User-Agent": SEC_HEADERS["User-Agent"]
        },
        timeout=20,
    )

    response.raise_for_status()

    ticker_data = response.json()

    cik = None
    company_name = None

    for item in ticker_data.values():

        item_ticker = str(
            item.get("ticker", "")
        ).upper()

        if item_ticker == ticker:

            cik = str(
                item.get("cik_str")
            ).zfill(10)

            company_name = item.get(
                "title"
            )

            break

    if cik is None:

        raise ValueError(
            f"Could not resolve SEC CIK for ticker '{ticker}'."
        )

    # --------------------------------------------------------
    # Company facts
    # --------------------------------------------------------

    facts = _get_company_facts(
        cik
    )

    # ========================================================
    # REVENUE
    # ========================================================

    revenue = _find_fact_value(
        facts,
        [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
        ],
    )

    # ========================================================
    # NET INCOME
    # ========================================================

    net_income = _find_fact_value(
        facts,
        [
            "NetIncomeLoss",
            "ProfitLoss",
        ],
    )

    # ========================================================
    # OPERATING INCOME
    # ========================================================

    operating_income = _find_fact_value(
        facts,
        [
            "OperatingIncomeLoss",
        ],
    )

    # ========================================================
    # OPERATING CASH FLOW
    # ========================================================

    operating_cash_flow = _find_fact_value(
        facts,
        [
            "NetCashProvidedByUsedInOperatingActivities",
        ],
    )

    # ========================================================
    # CAPITAL EXPENDITURE
    # ========================================================

    capital_expenditure = _find_fact_value(
        facts,
        [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
        ],
    )

    # ========================================================
    # FREE CASH FLOW
    # ========================================================
    #
    # SEC generally reports:
    #
    # Operating Cash Flow
    # -
    # Capital Expenditure
    #
    # Capex is usually represented as a positive cash
    # outflow in SEC XBRL.
    #
    # Therefore:
    #
    # FCF = OCF - Capex
    #
    # If a provider happens to expose capex as negative,
    # normalize accordingly.
    #
    # ========================================================

    free_cash_flow = None

    if (
        operating_cash_flow is not None
        and capital_expenditure is not None
    ):

        if capital_expenditure < 0:

            free_cash_flow = (
                operating_cash_flow
                + capital_expenditure
            )

        else:

            free_cash_flow = (
                operating_cash_flow
                - capital_expenditure
            )

    # ========================================================
    # CASH
    # ========================================================

    cash = _find_fact_value(
        facts,
        [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "CashAndDueFromBanks",
        ],
        balance_sheet=True,
    )

    # ========================================================
    # DEBT
    # ========================================================

    short_term_debt = _find_fact_value(
        facts,
        [
            "ShortTermBorrowings",
            "ShortTermDebt",
            "DebtCurrent",
            "LongTermDebtCurrent",
        ],
        balance_sheet=True,
    )

    long_term_debt = _find_fact_value(
        facts,
        [
            "LongTermDebtNoncurrent",
            "LongTermDebt",
            "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
        ],
        balance_sheet=True,
    )

    total_debt = None

    if (
        short_term_debt is not None
        or long_term_debt is not None
    ):

        total_debt = (
            (short_term_debt or 0.0)
            + (long_term_debt or 0.0)
        )

    # --------------------------------------------------------
    # Alternative debt tag
    # --------------------------------------------------------

    if total_debt is None:

        total_debt = _find_fact_value(
            facts,
            [
                "LongTermDebtAndFinanceLeaseObligationsCurrent",
                "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
            ],
            balance_sheet=True,
        )

    # ========================================================
    # SHARES OUTSTANDING
    # ========================================================

    shares_outstanding = _find_fact_value(
        facts,
        [
            "EntityCommonStockSharesOutstanding",
        ],
        balance_sheet=True,
    )

    # ========================================================
    # NORMALIZE USD -> MILLIONS USD
    # ========================================================

    monetary_fields = [
        "revenue",
        "net_income",
        "operating_income",
        "free_cash_flow",
        "total_debt",
        "cash",
    ]

    values = {
        "revenue": revenue,
        "net_income": net_income,
        "operating_income": operating_income,
        "free_cash_flow": free_cash_flow,
        "total_debt": total_debt,
        "cash": cash,
    }

    for field in monetary_fields:

        value = values.get(field)

        if value is not None:

            values[field] = (
                value / 1_000_000.0
            )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "ticker": ticker,

        "company_name": company_name,

        "cik": cik,

        "source": (
            "SEC EDGAR XBRL API "
            "(data.sec.gov)"
        ),

        "revenue": values["revenue"],

        "net_income": values["net_income"],

        "operating_income": values[
            "operating_income"
        ],

        "free_cash_flow": values[
            "free_cash_flow"
        ],

        "total_debt": values[
            "total_debt"
        ],

        "cash": values["cash"],

        "shares_outstanding": (
            shares_outstanding
        ),

        "currency": "USD",

        "financial_scale": "millions",

        "verified_by_sec": True,
    }# ============================================================
# BACKWARD-COMPATIBILITY ENGINE
# ============================================================

class SECXBRLEngine:
    """
    Backward-compatible SEC XBRL interface.

    Existing application code imports SECXBRLEngine,
    while the canonical financial extraction is handled
    by get_sec_financials().
    """

    @staticmethod
    def get_financials(
        ticker: str,
    ) -> Dict[str, Any]:
        return get_sec_financials(ticker)

    @staticmethod
    def get_xbrl_financials(
        ticker: str,
    ) -> Dict[str, Any]:
        return get_sec_financials(ticker)

    @staticmethod
    def get_company_financials(
        ticker: str,
    ) -> Dict[str, Any]:
        return get_sec_financials(ticker)

    @staticmethod
    def fetch_financials(
        ticker: str,
    ) -> Dict[str, Any]:
        return get_sec_financials(ticker)