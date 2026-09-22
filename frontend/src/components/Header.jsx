import React, { useState } from 'react';

export default function Header({ onSearch, loading, activeTab, setActiveTab }) {
  const [query, setQuery] = useState('NVIDIA');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query);
    }
  };

  const quickLaunch = (name) => {
    setQuery(name);
    onSearch(name);
  };

  const tabs = [
    { id: 'dashboard', label: '🔍 Dashboard & Trace' },
    { id: 'evidence', label: '🛡️ Evidence & Claims' },
    { id: 'debate', label: '⚔️ Bull vs Bear Debate' },
    { id: 'valuation', label: '🧮 Valuation & Monte Carlo' },
    { id: 'graph', label: '🕸️ Knowledge Graph & Memory' },
    { id: 'eval', label: '🧪 Evaluation Lab' }
  ];

  return (
    <header style={{ background: '#111827', borderBottom: '1px solid #374151', padding: '1rem 2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            fontSize: '1.25rem',
            color: '#fff',
            boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
          }}>
            FA
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700, color: '#f9fafb', letterSpacing: '-0.02em' }}>
              FinResearch <span style={{ color: '#60a5fa' }}>AI</span>
            </h1>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#9ca3af' }}>
              Investment Research & Financial Valuation Platform
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', flex: 1, maxWidth: '520px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Analyze company (e.g. NVIDIA, Tesla, Apple)..."
            style={{
              flex: 1,
              background: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              padding: '0.6rem 1rem',
              color: '#fff',
              fontSize: '0.9rem',
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading ? '#4b5563' : '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              padding: '0.6rem 1.25rem',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {loading ? 'Investigating...' : 'Investigate'}
          </button>
        </form>

        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#6b7280', marginRight: '0.2rem' }}>Quick Test:</span>
          <button onClick={() => quickLaunch('NVIDIA')} style={quickBtnStyle}>NVIDIA</button>
          <button onClick={() => quickLaunch('Micron')} style={quickBtnStyle}>Micron (MU)</button>
          <button onClick={() => quickLaunch('AMD')} style={quickBtnStyle}>AMD</button>
          <button onClick={() => quickLaunch('Tesla')} style={quickBtnStyle}>Tesla</button>
        </div>
      </div>

      <nav style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem', borderTop: '1px solid #1f2937', paddingTop: '0.75rem', overflowX: 'auto' }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              background: activeTab === t.id ? '#1f2937' : 'transparent',
              color: activeTab === t.id ? '#60a5fa' : '#9ca3af',
              border: activeTab === t.id ? '1px solid #3b82f6' : '1px solid transparent',
              borderRadius: '6px',
              padding: '0.5rem 0.9rem',
              fontSize: '0.85rem',
              fontWeight: activeTab === t.id ? 600 : 400,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease'
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>
    </header>
  );
}

const quickBtnStyle = {
  background: '#1f2937',
  color: '#9ca3af',
  border: '1px solid #374151',
  borderRadius: '6px',
  padding: '0.3rem 0.6rem',
  fontSize: '0.75rem',
  cursor: 'pointer'
};
