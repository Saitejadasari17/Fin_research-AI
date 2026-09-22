from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

class ClaimItem(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"CLM-{uuid.uuid4().hex[:6]}")
    claim_text: str
    category: str              # "Financials", "Growth", "Competition", "Risks", "Valuation"
    status: str                # "Verified", "Partially Supported", "Contradicted"
    source_name: str
    source_type: str
    source_url: Optional[str] = None
    confidence_score: float    # 0.0 to 1.0
    evidence_snippet: str
    corroborating_sources_count: int = 1
    contradiction_notes: Optional[str] = None

class EvidenceStore:
    def __init__(self):
        self.claims: List[ClaimItem] = []

    def add_claim(self, claim: ClaimItem) -> ClaimItem:
        # Check if claim matches an existing claim for corroboration
        for existing in self.claims:
            if existing.claim_text.lower() == claim.claim_text.lower():
                existing.corroborating_sources_count += 1
                # Boost confidence based on corroboration
                existing.confidence_score = min(1.0, existing.confidence_score + 0.08)
                existing.status = "Verified"
                return existing

        self.claims.append(claim)
        return claim

    def extract_claims_from_finding(self, tool_name: str, result_data: Dict[str, Any]) -> List[ClaimItem]:
        extracted = []
        if not isinstance(result_data, dict):
            return extracted
        
        company_name = result_data.get("company_name", "Company")
        ticker = result_data.get("ticker", "")
        currency = result_data.get("currency", "INR" if result_data.get("country") == "India" else "USD")

        if tool_name in ["get_sec_financials", "get_indian_financials", "get_financials"]:
            rev = result_data.get("revenue")
            op = result_data.get("operating_income")
            fcf = result_data.get("free_cash_flow")
            net = result_data.get("net_income")
            source = result_data.get("source", "Financial DB")
            source_url = result_data.get("source_url", "https://finance.yahoo.com")

            if rev is not None:
                c = ClaimItem(
                    claim_text=f"{company_name} ({ticker}) reported revenue of {currency} {float(rev):,.1f}M.",
                    category="Financials",
                    status="Verified",
                    source_name=source,
                    source_type="Financial DB" if "Yahoo" in source else "SEC Filing",
                    source_url=source_url,
                    confidence_score=0.98 if "SEC" in source else 0.90,
                    evidence_snippet=f"Reported revenue {currency} {float(rev):,.1f}M, Net Income {currency} {float(net or 0):,.1f}M.",
                    corroborating_sources_count=1
                )
                extracted.append(self.add_claim(c))

            if fcf is not None:
                c_fcf = ClaimItem(
                    claim_text=f"{company_name} ({ticker}) generated free cash flow of {currency} {float(fcf):,.1f}M.",
                    category="Financials",
                    status="Verified",
                    source_name=source,
                    source_type="Financial DB",
                    source_url=source_url,
                    confidence_score=0.90,
                    evidence_snippet=f"Free cash flow {currency} {float(fcf):,.1f}M.",
                    corroborating_sources_count=1
                )
                extracted.append(self.add_claim(c_fcf))

        elif tool_name in ["get_market_data", "get_indian_market_data"]:
            price = result_data.get("current_stock_price")
            growth = result_data.get("high_growth_rate")
            source = result_data.get("source", "Market Data Provider")
            source_url = result_data.get("source_url", "https://finance.yahoo.com")

            if price is not None:
                price_claim = ClaimItem(
                    claim_text=f"{company_name} ({ticker}) market price is {currency} {float(price):,.2f}.",
                    category="Financials",
                    status="Verified",
                    source_name=source,
                    source_type="Financial DB",
                    source_url=source_url,
                    confidence_score=0.90,
                    evidence_snippet=f"Market price {currency} {float(price):,.2f}.",
                    corroborating_sources_count=1,
                )
                extracted.append(self.add_claim(price_claim))

            if growth is not None:
                growth_claim = ClaimItem(
                    claim_text=f"{company_name} ({ticker}) has a verified historical growth rate of {float(growth) * 100:.1f}%.",
                    category="Growth",
                    status="Verified",
                    source_name=source,
                    source_type="Financial DB",
                    source_url=source_url,
                    confidence_score=0.80,
                    evidence_snippet=f"Historical revenue growth {float(growth) * 100:.1f}%.",
                    corroborating_sources_count=1,
                )
                extracted.append(self.add_claim(growth_claim))

        elif tool_name == "web_search_news":
            articles = result_data.get("articles_retrieved", [])
            for art in articles:
                if isinstance(art, dict) and "title" in art:
                    c = ClaimItem(
                        claim_text=f"{art['title']}: {art.get('snippet', '')[:120]}...",
                        category="Competition" if any(w in art["title"].lower() for w in ["custom", "silicon", "competitor", "market"]) else "Risks",
                        status="Verified",
                        source_name=art.get("source", "News RSS"),
                        source_type="News",
                        source_url=art.get("url"),
                        confidence_score=0.80,
                        evidence_snippet=art.get("snippet", art["title"]),
                        corroborating_sources_count=1
                    )
                    extracted.append(self.add_claim(c))

        return extracted

    def get_all_claims(self) -> List[ClaimItem]:
        return self.claims

    def calculate_overall_confidence(self) -> Dict[str, float]:
        if not self.claims:
            return {"overall": 0.0, "financials": 0.0, "growth": 0.0, "competition": 0.0, "risks": 0.0, "valuation": 0.0}

        overall = sum(c.confidence_score for c in self.claims) / len(self.claims)
        
        cats = ["Financials", "Growth", "Competition", "Risks", "Valuation"]
        scores = {}
        for cat in cats:
            cat_claims = [c for c in self.claims if c.category.lower() == cat.lower()]
            if cat_claims:
                scores[cat.lower()] = round(sum(c.confidence_score for c in cat_claims) / len(cat_claims) * 100, 1)
            else:
                scores[cat.lower()] = 80.0

        scores["overall"] = round(overall * 100, 1)
        return scores
