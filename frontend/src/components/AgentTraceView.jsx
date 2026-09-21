import React from 'react';

export default function AgentTraceView({ report }) {
  if (!report) return null;

  const recColor = report.investment_recommendation === 'BUY' ? '#34d399' :
                   report.investment_recommendation === 'SELL' ? '#f87171' : '#fbbf24';

  const currencySymbol = (report.currency === 'INR' || report.currency === '₹' || report.ticker?.endsWith('.NS')) ? '₹' : '$';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.25rem' }}>
      {/* Main Executive Summary & Trace */}
      <div>
        {/* Recommendation Banner */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9))',
          border: `1px solid ${recColor}`,
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.25rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontSize: '0.85rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Autonomous Due-Diligence Recommendation
            </div>
            <h2 style={{ margin: '0.2rem 0', fontSize: '1.8rem', color: '#f9fafb' }}>
              {report.company_name} ({report.ticker})
            </h2>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#d1d5db', maxWidth: '680px' }}>
              {report.executive_summary}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{
              background: `${recColor}22`,
              color: recColor,
              border: `1px solid ${recColor}`,
              padding: '0.5rem 1.25rem',
              borderRadius: '8px',
              fontWeight: 800,
              fontSize: '1.4rem',
              display: 'inline-block',
              letterSpacing: '0.05em'
            }}>
              {report.investment_recommendation}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '0.4rem' }}>
              Grounding Confidence: <strong style={{ color: '#fff' }}>{report.confidence_score}%</strong>
            </div>
          </div>
        </div>

        {/* Live Agent Execution Trace */}
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f9fafb', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>📡</span> Live Agent Investigation Trace
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#9ca3af', fontFamily: 'monospace' }}>
              {report.execution_trace.length} Steps Executed
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {report.execution_trace.map((step) => (
              <div
                key={step.step_id}
                style={{
                  background: '#111827',
                  borderLeft: '4px solid #3b82f6',
                  borderRadius: '6px',
                  padding: '0.9rem 1.1rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: '#9ca3af', marginBottom: '0.3rem' }}>
                  <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
                    <span style={{ color: '#60a5fa', fontWeight: 600 }}>Step {step.step_id}</span>
                    <span style={{ background: '#374151', padding: '0.1rem 0.4rem', borderRadius: '4px', color: '#d1d5db' }}>{step.phase}</span>
                    <span style={{ color: '#a7f3d0' }}>{step.agent_role}</span>
                  </div>
                  <span style={{ fontFamily: 'monospace' }}>{step.timestamp} ({step.latency_ms}ms)</span>
                </div>

                <div style={{ fontWeight: 600, color: '#f9fafb', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                  {step.action}
                </div>

                <div style={{ fontSize: '0.83rem', color: '#d1d5db', background: '#1f2937', padding: '0.5rem 0.75rem', borderRadius: '6px', marginTop: '0.4rem' }}>
                  <strong style={{ color: '#9ca3af' }}>Tool Called:</strong> <code style={{ color: '#fbbf24' }}>{step.tool_called}</code>
                  <br />
                  <strong style={{ color: '#9ca3af' }}>Findings:</strong> {step.findings_summary}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar Metrics & Observability */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Observability Telemetry */}
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#f9fafb' }}>
            ⚡ Agent Observability
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={telemetryBoxStyle}>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Total Latency</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#60a5fa' }}>{report.total_latency_seconds}s</div>
            </div>
            <div style={telemetryBoxStyle}>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Est. Token Cost</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#34d399' }}>${report.total_cost_usd}</div>
            </div>
            <div style={telemetryBoxStyle}>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>DCF Intrinsic</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fbbf24' }}>{currencySymbol}{report.dcf_result.intrinsic_value_per_share}</div>
            </div>
            <div style={telemetryBoxStyle}>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Market Price</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f9fafb' }}>{currencySymbol}{report.dcf_result.current_price}</div>
            </div>
          </div>
        </div>

        {/* Grounding Confidence Gauge */}
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#f9fafb' }}>
            🛡️ Grounding Confidence
          </h4>
          {Object.entries(report.overall_confidence_breakdown).map(([cat, score]) => (
            <div key={cat} style={{ marginBottom: '0.6rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#d1d5db', marginBottom: '0.2rem' }}>
                <span style={{ textTransform: 'capitalize' }}>{cat}</span>
                <span style={{ fontWeight: 600 }}>{score}%</span>
              </div>
              <div style={{ background: '#111827', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{
                  width: `${score}%`,
                  height: '100%',
                  background: score > 85 ? '#34d399' : score > 70 ? '#fbbf24' : '#f87171'
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const telemetryBoxStyle = {
  background: '#111827',
  padding: '0.75rem',
  borderRadius: '8px',
  border: '1px solid #374151'
};
