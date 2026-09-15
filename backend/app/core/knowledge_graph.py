import networkx as nx
from typing import List, Dict, Any
from pydantic import BaseModel

class GraphNode(BaseModel):
    id: str
    label: str
    type: str         # "Company", "Product", "Competitor", "Customer", "Risk", "Metric"

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str     # "competes_with", "supplies_to", "manufactures", "threatens_margin"

class KnowledgeGraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    multi_hop_insights: List[str]

class KnowledgeGraphEngine:
    @staticmethod
    def build_company_graph(company_name: str) -> KnowledgeGraphData:
        comp = company_name.upper()
        
        if "NVDA" in comp or "NVIDIA" in comp:
            nodes = [
                GraphNode(id="NVDA", label="NVIDIA", type="Company"),
                GraphNode(id="B200", label="Blackwell B200", type="Product"),
                GraphNode(id="CUDA", label="CUDA Platform", type="Product"),
                GraphNode(id="AMD", label="AMD (MI300X)", type="Competitor"),
                GraphNode(id="MSFT", label="Microsoft Azure", type="Customer"),
                GraphNode(id="AMZN", label="Amazon AWS", type="Customer"),
                GraphNode(id="ASIC", label="In-house Custom Silicon", type="Risk"),
                GraphNode(id="TSMC", label="TSMC (CoWoS Packaging)", type="Supplier"),
            ]
            edges = [
                GraphEdge(source="NVDA", target="B200", relation="manufactures"),
                GraphEdge(source="NVDA", target="CUDA", relation="powers_ecosystem"),
                GraphEdge(source="NVDA", target="AMD", relation="competes_with"),
                GraphEdge(source="NVDA", target="MSFT", relation="supplies_gpus_to"),
                GraphEdge(source="NVDA", target="AMZN", relation="supplies_gpus_to"),
                GraphEdge(source="MSFT", target="ASIC", relation="developing_maia_chips"),
                GraphEdge(source="AMZN", target="ASIC", relation="deploying_trainium_chips"),
                GraphEdge(source="ASIC", target="NVDA", relation="threatens_longterm_margin"),
                GraphEdge(source="TSMC", target="B200", relation="exclusive_packaging_provider"),
            ]
            insights = [
                "Multi-Hop Risk Path Identified: [MSFT/AMZN] -> [Developing Custom Silicon] -> [Bypasses NVIDIA CUDA Ecosystem] -> [Reduces Forward GPU Pricing Power].",
                "Single-Point Supply Chain Bottleneck: [TSMC CoWoS Packaging] -> [Constrains B200 Delivery Schedule]."
            ]
        else:
            nodes = [
                GraphNode(id="TARGET", label=company_name, type="Company"),
                GraphNode(id="PROD", label="Core Offerings", type="Product"),
                GraphNode(id="COMP", label="Sector Peers", type="Competitor"),
                GraphNode(id="RISK", label="Macro Headwinds", type="Risk"),
            ]
            edges = [
                GraphEdge(source="TARGET", target="PROD", relation="manufactures"),
                GraphEdge(source="TARGET", target="COMP", relation="competes_with"),
                GraphEdge(source="RISK", target="TARGET", relation="impacts_valuation"),
            ]
            insights = [
                "Graph Traversal: Identified core competitive links and key macroeconomic sensitivities."
            ]

        return KnowledgeGraphData(nodes=nodes, edges=edges, multi_hop_insights=insights)
