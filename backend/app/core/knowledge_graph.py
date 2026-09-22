from typing import List

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class KnowledgeGraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    multi_hop_insights: List[str]


class KnowledgeGraphEngine:
    @staticmethod
    def build_company_graph(company_name: str) -> KnowledgeGraphData:
        company_id = company_name.strip().upper().replace(" ", "_")
        financial_id = f"{company_id}_FINANCIALS"
        risk_id = f"{company_id}_RISKS"

        return KnowledgeGraphData(
            nodes=[
                GraphNode(id=company_id, label=company_name.strip(), type="Company"),
                GraphNode(id=financial_id, label="Verified financial evidence", type="Metric"),
                GraphNode(id=risk_id, label="Research gaps and risks", type="Risk"),
            ],
            edges=[
                GraphEdge(source=company_id, target=financial_id, relation="has_verified_evidence"),
                GraphEdge(source=risk_id, target=company_id, relation="requires_review"),
            ],
            multi_hop_insights=[
                f"Evidence path: [{company_name.strip()}] -> [Verified financial evidence].",
                f"Review path: [Research gaps and risks] -> [{company_name.strip()}].",
            ],
        )