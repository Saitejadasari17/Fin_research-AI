import React, { useState, useEffect } from 'react';

export default function EvaluationLabView() {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(true);

  const rawApiUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
  let API_BASE_URL = rawApiUrl || 'http://127.0.0.1:8000';
  if (API_BASE_URL && !API_BASE_URL.startsWith('http://') && !API_BASE_URL.startsWith('https://')) {
    API_BASE_URL = `https://${API_BASE_URL}`;
  }
  API_BASE_URL = API_BASE_URL.replace(/\/+$/, '');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/eval/benchmark`)
      .then(res => res.json())
      .then(data => {
        setEvalData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Eval fetch error:", err);
        setLoading(false);
      });
  }, [API_BASE_URL]);

  if (loading) return <div style={{ padding: '2rem', color: '#9ca3af' }}>Loading Benchmark Results...</div>;
  if (!evalData) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Benchmark Header */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#f9fafb', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🧪</span> System Architecture & Performance Benchmark Lab
        </h3>
        <p style={{ margin: '0 0 1rem 0', fontSize: '0.88rem', color: '#9ca3af' }}>
          Comparative performance benchmark across 25 target companies comparing <strong>Basic API Search</strong> vs <strong>Fixed Script Pipeline</strong> vs <strong>FinResearch Analytics Engine</strong>.
        </p>

        {/* Comparative Metrics Table */}
        <div style={{ overflowX: 'auto', marginBottom: '1.25rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ background: '#111827', color: '#9ca3af', textAlign: 'left' }}>
                <th style={thStyle}>Architecture Mode</th>
                <th style={thStyle}>Factual Accuracy</th>
                <th style={thStyle}>Citation Precision</th>
                <th style={thStyle}>Error Rate</th>
                <th style={thStyle}>Contradiction Resolution</th>
                <th style={thStyle}>Valuation Precision</th>
                <th style={thStyle}>Avg Latency</th>
                <th style={thStyle}>Cost / Memo</th>
              </tr>
            </thead>
            <tbody>
              {evalData.metrics_summary.map(m => {
                const isEngine = m.architecture.includes('Engine');
                return (
                  <tr key={m.architecture} style={{
                    borderBottom: '1px solid #374151',
                    background: isEngine ? 'rgba(59, 130, 246, 0.1)' : 'transparent'
                  }}>
                    <td style={{ ...tdStyle, fontWeight: isEngine ? 700 : 500, color: isEngine ? '#60a5fa' : '#f9fafb' }}>
                      {m.architecture}
                    </td>
                    <td style={{ ...tdStyle, color: m.factual_accuracy_percent > 90 ? '#34d399' : '#fbbf24' }}>
                      {m.factual_accuracy_percent}%
                    </td>
                    <td style={tdStyle}>{m.citation_precision_percent}%</td>
                    <td style={{ ...tdStyle, color: m.hallucination_rate_percent < 5 ? '#34d399' : '#f87171', fontWeight: 600 }}>
                      {m.hallucination_rate_percent}%
                    </td>
                    <td style={{ ...tdStyle, color: m.contradiction_resolution_percent > 80 ? '#34d399' : '#9ca3af' }}>
                      {m.contradiction_resolution_percent}%
                    </td>
                    <td style={{ ...tdStyle, color: m.deterministic_math_compliance === 100 ? '#34d399' : '#f87171', fontWeight: 700 }}>
                      {m.deterministic_math_compliance}%
                    </td>
                    <td style={tdStyle}>{m.avg_latency_seconds}s</td>
                    <td style={tdStyle}>${m.est_cost_per_memo_usd}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Key Findings */}
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#34d399' }}>Key Performance Findings</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
          {evalData.key_findings.map((finding, idx) => (
            <div key={idx} style={{ background: '#111827', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem', color: '#d1d5db', borderLeft: '3px solid #34d399' }}>
              {finding}
            </div>
          ))}
        </div>

        {/* System Architecture Takeaway Box */}
        <div style={{ background: 'linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9))', padding: '1rem', borderRadius: '8px', border: '1px solid #3b82f6' }}>
          <strong style={{ color: '#60a5fa', fontSize: '0.9rem' }}>🎯 System Architecture Takeaway:</strong>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.85rem', color: '#f9fafb', lineHeight: 1.5 }}>
            "{evalData.architectural_takeaway}"
          </p>
        </div>
      </div>
    </div>
  );
}

const thStyle = {
  padding: '0.75rem 0.8rem',
  borderBottom: '1px solid #374151'
};

const tdStyle = {
  padding: '0.75rem 0.8rem',
  borderBottom: '1px solid #374151'
};
