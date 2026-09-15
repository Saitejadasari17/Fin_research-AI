import React from 'react';

export default function ValuationStudio({ report }) {
  if (!report || !report.dcf_result) return null;

  const dcf = report.dcf_result;
  const mc = report.monte_carlo_result;
  const sens = report.sensitivity_matrix;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* DCF Summary Banner */}
      <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🧮</span> Multi-Stage Discounted Cash Flow (DCF) Valuation Model
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
          <div style={statCardStyle}>
            <div style={labelStyle}>Intrinsic Fair Value</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34d399' }}>${dcf.intrinsic_value_per_share}</div>
          </div>
          <div style={statCardStyle}>
            <div style={labelStyle}>Current Market Price</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f9fafb' }}>${dcf.current_price}</div>
          </div>
          <div style={statCardStyle}>
            <div style={labelStyle}>Implied Upside / Downside</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: dcf.upside_downside_percent >= 0 ? '#34d399' : '#f87171' }}>
              {dcf.upside_downside_percent > 0 ? '+' : ''}{dcf.upside_downside_percent}%
            </div>
          </div>
          <div style={statCardStyle}>
            <div style={labelStyle}>WACC Used</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fbbf24' }}>{dcf.wacc_used}%</div>
          </div>
        </div>

        {/* Cash Flow Forecast Table */}
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#9ca3af' }}>10-Year Free Cash Flow Projections ($M)</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ background: '#111827', color: '#9ca3af', textAlign: 'left' }}>
                <th style={thStyle}>Year</th>
                <th style={thStyle}>Phase</th>
                <th style={thStyle}>Projected FCF ($M)</th>
                <th style={thStyle}>Present Value ($M)</th>
              </tr>
            </thead>
            <tbody>
              {dcf.yearly_cash_flows.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #374151' }}>
                  <td style={tdStyle}>Year {row.year}</td>
                  <td style={tdStyle}>
                    <span style={{ background: row.phase === 'High Growth' ? '#1e3a8a' : '#374151', color: '#93c5fd', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                      {row.phase}
                    </span>
                  </td>
                  <td style={tdStyle}>${row.fcf.toLocaleString()}</td>
                  <td style={tdStyle}>${row.pv_fcf.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5,000-Run Monte Carlo Simulation */}
      {mc && (
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🎲</span> 5,000-Run Monte Carlo Valuation Distribution
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <div style={statCardStyle}>
              <div style={labelStyle}>Median Fair Value</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#60a5fa' }}>${mc.median_fair_value}</div>
            </div>
            <div style={statCardStyle}>
              <div style={labelStyle}>5th Percentile</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f87171' }}>${mc.percentile_5}</div>
            </div>
            <div style={statCardStyle}>
              <div style={labelStyle}>75th Percentile</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#34d399' }}>${mc.percentile_75}</div>
            </div>
            <div style={statCardStyle}>
              <div style={labelStyle}>95th Percentile</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#a78bfa' }}>${mc.percentile_95}</div>
            </div>
            <div style={statCardStyle}>
              <div style={labelStyle}>Prob. Undervalued</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fbbf24' }}>{mc.probability_undervalued_percent}%</div>
            </div>
          </div>

          {/* Histogram bar visualization */}
          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#9ca3af' }}>Probability Distribution Bins</h4>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '4px', height: '140px', background: '#111827', padding: '1rem', borderRadius: '8px' }}>
            {mc.histogram_counts.map((count, idx) => {
              const maxCount = Math.max(...mc.histogram_counts);
              const heightPct = (count / maxCount) * 100;
              const binPrice = mc.histogram_bins[idx];
              const isCurrent = Math.abs(binPrice - mc.current_price) < 15;
              return (
                <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                  <div
                    title={`Price: $${binPrice} | Count: ${count}`}
                    style={{
                      width: '100%',
                      height: `${heightPct}%`,
                      background: isCurrent ? '#f59e0b' : '#3b82f6',
                      borderRadius: '2px',
                      transition: 'height 0.3s ease'
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 2D Sensitivity Matrix */}
      {sens && (
        <div style={{ background: '#1f2937', borderRadius: '12px', padding: '1.25rem', border: '1px solid #374151' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>📊</span> 2D Sensitivity Heatmap (Growth Rate vs WACC Discount Rate)
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.82rem' }}>
              <thead>
                <tr style={{ background: '#111827', color: '#9ca3af' }}>
                  <th style={thStyle}>Growth \ WACC</th>
                  {sens.discount_rates.map(w => (
                    <th key={w} style={thStyle}>{w}%</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sens.growth_rates.map((g, rIdx) => (
                  <tr key={g}>
                    <td style={{ ...tdStyle, fontWeight: 700, color: '#9ca3af', background: '#111827' }}>{g}% Growth</td>
                    {sens.matrix[rIdx].map((val, cIdx) => {
                      const cur = report.dcf_result.current_price;
                      const isUp = val >= cur;
                      return (
                        <td
                          key={cIdx}
                          style={{
                            ...tdStyle,
                            background: isUp ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                            color: isUp ? '#34d399' : '#f87171',
                            fontWeight: 600
                          }}
                        >
                          ${val}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

const statCardStyle = {
  background: '#111827',
  padding: '0.9rem',
  borderRadius: '8px',
  border: '1px solid #374151'
};

const labelStyle = {
  fontSize: '0.75rem',
  color: '#9ca3af',
  marginBottom: '0.2rem'
};

const thStyle = {
  padding: '0.6rem 0.8rem',
  borderBottom: '1px solid #374151'
};

const tdStyle = {
  padding: '0.6rem 0.8rem',
  borderBottom: '1px solid #374151'
};
