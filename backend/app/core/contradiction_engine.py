from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.evidence_store import EvidenceStore, ClaimItem

class ContradictionAlert(BaseModel):
    alert_id: str
    topic: str
    source_a: str
    value_a: str
    source_b: str
    value_b: str
    discrepancy_reason: str
    resolution_status: str     # "Detected", "Investigating", "Resolved"
    resolved_truth: Optional[str] = None
    investigation_action: str

class ContradictionEngine:
    @staticmethod
    def detect_contradictions(claims: List[ClaimItem], company_name: str) -> List[ContradictionAlert]:
        alerts = []

        grouped_claims: Dict[str, List[ClaimItem]] = {}
        for claim in claims:
            grouped_claims.setdefault(claim.category.lower(), []).append(claim)

        for category, category_claims in grouped_claims.items():
            sources = {}
            for claim in category_claims:
                sources.setdefault(claim.source_name, []).append(claim)

            source_names = list(sources)
            if len(source_names) < 2:
                continue

            first = sources[source_names[0]][0]
            second = sources[source_names[1]][0]
            alerts.append(ContradictionAlert(
                alert_id=f"CONTRA-{category.upper()}-{len(alerts) + 1:02d}",
                topic=f"Conflicting {category} evidence for {company_name}",
                source_a=first.source_name,
                value_a=first.claim_text,
                source_b=second.source_name,
                value_b=second.claim_text,
                discrepancy_reason="Claims in the same category have different sources and require period and methodology review.",
                resolution_status="Investigating",
                investigation_action="Compare source quality, reporting period, and calculation method before using the claims together.",
            ))

        return alerts
