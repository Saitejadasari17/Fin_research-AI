import React from 'react';

export default function GraphAndMemoryView({ report }) {
  if (!report) return null;

  const kg = report.knowledge_graph || { nodes: [], edges: [], multi_hop_insights: [] };
  const temp = report.temporal_diff || {};
  const currencySymbol = (report.currency === 'INR' || report.currency === '₹' || report.ticker?.endsWith('.NS')) ? '₹' : '$';

  const nodes = kg.nodes || [];
  const edges = kg.edges || [];
  const insights = kg.multi_hop_insights || [];

  const prevSnap = temp.previous_snapshot;
  const currSnap = temp.current_snapshot;
  const invalidated = temp.invalidated_assumptions || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Knowledge Graph (GraphRAG) */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🕸️</span> GraphRAG Entity-Relationship Network
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
          {/* Entity Nodes List */}
          <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem', color: '#60a5fa' }}>Extracted Entities ({nodes.length})</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {nodes.length > 0 ? (
                nodes.map((node, idx) => (
                  <span key={node.id || idx} style={{
                    background: node.type === 'Company' ? '#1e3a8a' : node.type === 'Competitor' ? '#831843' : node.type === 'Risk' ? '#7f1d1d' : '#374151',
                    color: '#fff',
                    padding: '0.3rem 0.6rem',
                    borderRadius: '6px',
                    fontSize: '0.78rem'
                  }}>
                    {node.label || node.name} ({node.type || 'Entity'})
                  </span>
                ))
              ) : (
                <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>No entity nodes available.</span>
              )}
            </div>
          </div>

          {/* Entity Edges List */}
          <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem', color: '#a78bfa' }}>Grounded Relationships ({edges.length})</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.8rem', maxHeight: '160px', overflowY: 'auto' }}>
              {edges.length > 0 ? (
                edges.map((edge, idx) => (
                  <div key={idx} style={{ color: '#d1d5db' }}>
                    <strong style={{ color: '#60a5fa' }}>{edge.source}</strong>
                    <span style={{ color: '#9ca3af', margin: '0 0.4rem' }}>──[{edge.relation}]──►</span>
                    <strong style={{ color: '#34d399' }}>{edge.target}</strong>
                  </div>
                ))
              ) : (
                <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>No relationships mapped.</span>
              )}
            </div>
          </div>
        </div>

        {/* Multi-hop insights */}
        {insights.length > 0 && (
          <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', borderLeft: '4px solid #3b82f6' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.88rem', color: '#60a5fa' }}>Multi-Hop Graph Traversal Risk Insights</h4>
            {insights.map((insight, idx) => (
              <p key={idx} style={{ margin: '0 0 0.4rem 0', fontSize: '0.83rem', color: '#d1d5db' }}>
                • {insight}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Temporal Memory Snapshot Diff */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🧠</span> Temporal Research Memory & Assumption Diff Engine
        </h3>

        <div style={{ background: '#111827', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.9rem', color: '#34d399', fontWeight: 600, marginBottom: '0.5rem' }}>
            {temp.summary_diff_narrative || 'Research snapshot memory active.'}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.82rem', marginTop: '0.75rem' }}>
            <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '6px' }}>
              <strong style={{ color: '#9ca3af' }}>Previous Snapshot:</strong>
              {prevSnap ? (
                <div style={{ marginTop: '0.3rem', color: '#d1d5db' }}>
                  Timestamp: <strong>{prevSnap.timestamp}</strong><br />
                  DCF Value: <strong>{prevSnap.dcf_intrinsic_value ? `${currencySymbol}${prevSnap.dcf_intrinsic_value}` : 'N/A'}</strong><br />
                  Growth Assumption: <strong>{prevSnap.high_growth_assumption != null ? `${(prevSnap.high_growth_assumption * 100).toFixed(1)}%` : 'N/A'}</strong><br />
                  Recommendation: <strong>{prevSnap.thesis_recommendation || 'N/A'}</strong>
                </div>
              ) : (
                <div style={{ marginTop: '0.3rem', color: '#9ca3af', fontStyle: 'italic' }}>
                  No prior historical snapshot stored for this company yet.
                </div>
              )}
            </div>
            <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '6px' }}>
              <strong style={{ color: '#9ca3af' }}>Current Research Snapshot:</strong>
              {currSnap ? (
                <div style={{ marginTop: '0.3rem', color: '#d1d5db' }}>
                  Timestamp: <strong>{currSnap.timestamp || 'Initial Run'}</strong><br />
                  DCF Value: <strong>{currSnap.dcf_intrinsic_value ? `${currencySymbol}${currSnap.dcf_intrinsic_value}` : 'N/A'}</strong><br />
                  Growth Assumption: <strong>{currSnap.high_growth_assumption != null ? `${(currSnap.high_growth_assumption * 100).toFixed(1)}%` : 'N/A'}</strong><br />
                  Recommendation: <strong>{currSnap.thesis_recommendation || report.investment_recommendation || 'N/A'}</strong>
                </div>
              ) : (
                <div style={{ marginTop: '0.3rem', color: '#9ca3af' }}>
                  Current snapshot initialized.
                </div>
              )}
            </div>
          </div>
        </div>

        {invalidated.length > 0 && (
          <>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.88rem', color: '#fbbf24' }}>Invalidated Assumptions & Evolving Risks</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.83rem' }}>
              {invalidated.map((inv, idx) => (
                <div key={idx} style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                  ⚠️ {inv}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
