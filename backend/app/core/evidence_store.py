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
        
        if tool_name == "get_sec_financials":
            rev = result_data.get("revenue", 0)
            op = result_data.get("operating_income", 0)
            fcf = result_data.get("free_cash_flow", 0)
            
            c = ClaimItem(
                claim_text=f"Official SEC 10-K reported annual revenue of ${rev:,.1f}M with operating cash flow of ${fcf:,.1f}M.",
                category="Financials",
                status="Verified",
                source_name=result_data.get("source", "SEC EDGAR"),
                source_type="SEC Filing",
                source_url="https://www.sec.gov",
                confidence_score=0.98,
                evidence_snippet=f"GAAP Revenue ${rev:,.1f}M, OpIncome ${op:,.1f}M.",
                corroborating_sources_count=1
            )
            extracted.append(self.add_claim(c))

        elif tool_name == "get_market_data":
            price = result_data.get("current_stock_price", 0)
            growth = result_data.get("high_growth_rate", 0)
            
            c = ClaimItem(
                claim_text=f"Market price is ${price:.2f} with consensus forward high-growth expectation of {growth*100:.1f}%.",
                category="Growth",
                status="Partially Supported",
                source_name="Market Data Provider",
                source_type="Financial DB",
                source_url="https://finance.yahoo.com",
                confidence_score=0.88,
                evidence_snippet=f"Market price ${price:.2f}, high growth rate {growth*100:.1f}%.",
                corroborating_sources_count=1
            )
            extracted.append(self.add_claim(c))

        elif tool_name == "web_search_news":
            articles = result_data.get("articles_retrieved", [])
            for art in articles:
                c = ClaimItem(
                    claim_text=f"{art['title']}: {art['snippet'][:120]}...",
                    category="Competition" if "Custom" in art["title"] or "Silicon" in art["title"] else "Risks",
                    status="Partially Supported" if "Analyst" in art["source"] else "Verified",
                    source_name=art["source"],
                    source_type="News",
                    source_url="https://bloomberg.com",
                    confidence_score=0.82 if "Bloomberg" in art["source"] else 0.75,
                    evidence_snippet=art["snippet"],
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
