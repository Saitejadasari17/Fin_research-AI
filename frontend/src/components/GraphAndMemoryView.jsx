import React from 'react';

export default function GraphAndMemoryView({ report }) {
  if (!report) return null;

  const kg = report.knowledge_graph;
  const temp = report.temporal_diff;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Knowledge Graph (GraphRAG) */}
      {kg && (
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🕸️</span> GraphRAG Entity-Relationship Network
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
            {/* Entity Nodes List */}
            <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
              <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem', color: '#60a5fa' }}>Extracted Entities</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {kg.nodes.map(node => (
                  <span key={node.id} style={{
                    background: node.type === 'Company' ? '#1e3a8a' : node.type === 'Competitor' ? '#831843' : node.type === 'Risk' ? '#7f1d1d' : '#374151',
                    color: '#fff',
                    padding: '0.3rem 0.6rem',
                    borderRadius: '6px',
                    fontSize: '0.78rem'
                  }}>
                    {node.label} ({node.type})
                  </span>
                ))}
              </div>
            </div>

            {/* Entity Edges List */}
            <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
              <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem', color: '#a78bfa' }}>Grounded Relationships</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.8rem', maxHeight: '160px', overflowY: 'auto' }}>
                {kg.edges.map((edge, idx) => (
                  <div key={idx} style={{ color: '#d1d5db' }}>
                    <strong style={{ color: '#60a5fa' }}>{edge.source}</strong>
                    <span style={{ color: '#9ca3af', margin: '0 0.4rem' }}>──[{edge.relation}]──►</span>
                    <strong style={{ color: '#34d399' }}>{edge.target}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Multi-hop insights */}
          <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', borderLeft: '4px solid #3b82f6' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.88rem', color: '#60a5fa' }}>Multi-Hop Graph Traversal Risk Insights</h4>
            {kg.multi_hop_insights.map((insight, idx) => (
              <p key={idx} style={{ margin: '0 0 0.4rem 0', fontSize: '0.83rem', color: '#d1d5db' }}>
                • {insight}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Temporal Memory Snapshot Diff */}
      {temp && (
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🧠</span> Temporal Research Memory & Assumption Diff Engine
          </h3>

          <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.9rem', color: '#34d399', fontWeight: 600, marginBottom: '0.5rem' }}>
              {temp.summary_diff_narrative}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.82rem', marginTop: '0.75rem' }}>
              <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '6px' }}>
                <strong style={{ color: '#9ca3af' }}>Previous Snapshot ({temp.previous_snapshot.timestamp}):</strong>
                <div style={{ marginTop: '0.3rem', color: '#d1d5db' }}>
                  DCF Value: <strong>${temp.previous_snapshot.dcf_intrinsic_value}</strong>
                  <br />
                  Growth Assumption: <strong>{temp.previous_snapshot.high_growth_assumption * 100}%</strong>
                  <br />
                  Recommendation: <strong>{temp.previous_snapshot.thesis_recommendation}</strong>
                </div>
              </div>
              <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '6px' }}>
                <strong style={{ color: '#9ca3af' }}>Current Research Snapshot ({temp.current_snapshot.timestamp}):</strong>
                <div style={{ marginTop: '0.3rem', color: '#d1d5db' }}>
                  DCF Value: <strong>${temp.current_snapshot.dcf_intrinsic_value}</strong>
                  <br />
                  Growth Assumption: <strong>{temp.current_snapshot.high_growth_assumption * 100}%</strong>
                  <br />
                  Recommendation: <strong>{temp.current_snapshot.thesis_recommendation}</strong>
                </div>
              </div>
            </div>
          </div>

          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.88rem', color: '#fbbf24' }}>Invalidated Assumptions & Evolving Risks</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.83rem' }}>
            {temp.invalidated_assumptions.map((inv, idx) => (
              <div key={idx} style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                ⚠️ {inv}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
