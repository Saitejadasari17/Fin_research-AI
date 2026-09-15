import React from 'react';

export default function BullBearView({ report }) {
  if (!report || !report.debate_result) return null;

  const debate = report.debate_result;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Judge Verdict Banner */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.5rem', border: '1px solid #8b5cf6' }}>
        <div style={{ fontSize: '0.8rem', color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>
          ⚖️ Judge Agent Thesis Verdict
        </div>
        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.4rem', color: '#f9fafb' }}>
          {debate.thesis_survival_status}
        </h3>
        <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.92rem', color: '#d1d5db' }}>
          {debate.judge_verdict}
        </p>
        <div style={{ background: '#111827', padding: '0.75rem', borderRadius: '8px', borderLeft: '4px solid #8b5cf6', fontSize: '0.85rem', color: '#c4b5fd' }}>
          <strong>Key Analyst Takeaway:</strong> {debate.key_takeaway}
        </div>
      </div>

      {/* Bull vs Bear Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        {/* Bull Case */}
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #10b981' }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#34d399', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🐂</span> Bull Agent Arguments
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {debate.bull_arguments.map((arg, idx) => (
              <div key={idx} style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                  <strong style={{ color: '#f9fafb', fontSize: '0.95rem' }}>{arg.point_title}</strong>
                  <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.75rem' }}>
                    {arg.impact_rating} Impact
                  </span>
                </div>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#d1d5db' }}>
                  {arg.argument}
                </p>
                <div style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                  <strong>Citation:</strong> {arg.evidence_citation}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bear Case */}
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #f43f5e' }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#f87171', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🐻</span> Bear Agent Arguments
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {debate.bear_arguments.map((arg, idx) => (
              <div key={idx} style={{ background: '#111827', borderRadius: '8px', padding: '1rem', border: '1px solid #374151' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                  <strong style={{ color: '#f9fafb', fontSize: '0.95rem' }}>{arg.point_title}</strong>
                  <span style={{ background: 'rgba(244, 63, 94, 0.2)', color: '#f87171', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.75rem' }}>
                    {arg.impact_rating} Impact
                  </span>
                </div>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#d1d5db' }}>
                  {arg.argument}
                </p>
                <div style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                  <strong>Citation:</strong> {arg.evidence_citation}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
