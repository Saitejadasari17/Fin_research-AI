import React from 'react';

export default function EvidenceView({ report }) {
  if (!report) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Contradiction Engine Alerts */}
      {report.contradictions && report.contradictions.length > 0 && (
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #f59e0b' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#fbbf24', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>⚠️</span> Contradiction Detection & Resolution Engine
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {report.contradictions.map(item => (
              <div key={item.alert_id} style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <strong style={{ color: '#f9fafb', fontSize: '0.95rem' }}>{item.topic}</strong>
                  <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '0.1rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                    {item.resolution_status}
                  </span>
                </div>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.83rem', color: '#9ca3af' }}>
                  {item.discrepancy_reason}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem', background: '#1f2937', padding: '0.6rem', borderRadius: '6px' }}>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Source A ({item.source_a}):</span>
                    <div style={{ color: '#60a5fa', fontWeight: 600 }}>{item.value_a}</div>
                  </div>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Source B ({item.source_b}):</span>
                    <div style={{ color: '#f87171', fontWeight: 600 }}>{item.value_b}</div>
                  </div>
                </div>

                <div style={{ marginTop: '0.5rem', fontSize: '0.83rem', color: '#34d399' }}>
                  <strong>Resolved Action:</strong> {item.resolved_truth}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Claims Matrix */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🛡️</span> Grounded Claim-Level Verification Matrix
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {report.claims.map(claim => {
            const statusBg = claim.status === 'Verified' ? '#34d399' :
                             claim.status === 'Partially Supported' ? '#fbbf24' : '#f87171';
            return (
              <div key={claim.claim_id} style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span style={{ background: '#374151', color: '#d1d5db', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.75rem' }}>
                      {claim.category}
                    </span>
                    <span style={{ color: '#9ca3af', fontSize: '0.78rem', fontFamily: 'monospace' }}>{claim.claim_id}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>Confidence: {Math.round(claim.confidence_score * 100)}%</span>
                    <span style={{ background: `${statusBg}22`, color: statusBg, border: `1px solid ${statusBg}`, padding: '0.15rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 700 }}>
                      {claim.status === 'Verified' ? '✓ Verified' : claim.status === 'Partially Supported' ? '⚠️ Partial' : '❌ Contradicted'}
                    </span>
                  </div>
                </div>

                <div style={{ fontWeight: 600, color: '#f9fafb', fontSize: '0.92rem', marginBottom: '0.4rem' }}>
                  "{claim.claim_text}"
                </div>

                <div style={{ background: '#1f2937', borderRadius: '6px', padding: '0.6rem 0.8rem', fontSize: '0.82rem', color: '#d1d5db' }}>
                  <strong style={{ color: '#9ca3af' }}>Source:</strong> {claim.source_name} ({claim.source_type})
                  <br />
                  <strong style={{ color: '#9ca3af' }}>Evidence Snippet:</strong> {claim.evidence_snippet}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
