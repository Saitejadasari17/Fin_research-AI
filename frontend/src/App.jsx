import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AgentTraceView from './components/AgentTraceView';
import EvidenceView from './components/EvidenceView';
import BullBearView from './components/BullBearView';
import ValuationStudio from './components/ValuationStudio';
import GraphAndMemoryView from './components/GraphAndMemoryView';
import EvaluationLabView from './components/EvaluationLabView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  const fetchAnalysis = (companyName) => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE_URL}/api/research/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: companyName })
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to execute dynamic investigation.`);
        return res.json();
      })
      .then(data => {
        setReport(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("API error:", err);
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    // Initial default research on launch
    fetchAnalysis('NVIDIA');
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#0b0f19', color: '#f9fafb' }}>
      <Header
        onSearch={fetchAnalysis}
        loading={loading}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main style={{ padding: '1.5rem 2rem', maxWidth: '1440px', margin: '0 auto' }}>
        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', color: '#f87171', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
            ⚠️ Error: {error}
          </div>
        )}

        {loading && (
          <div style={{
            background: '#1f2937',
            borderRadius: '12px',
            padding: '3rem',
            textAlign: 'center',
            border: '1px solid #374151',
            boxShadow: '0 0 25px rgba(59, 130, 246, 0.15)'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem', animation: 'spin 2s linear infinite' }}>
              📡
            </div>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#60a5fa', fontSize: '1.3rem' }}>
              Autonomous Research Agent Investigating...
            </h3>
            <p style={{ color: '#9ca3af', margin: 0, fontSize: '0.9rem' }}>
              Retrieving SEC 10-K filings, executing zero-LLM DCF math, running 5,000 Monte Carlo simulations, verifying claim grounding, and launching Bull vs Bear debate.
            </p>
          </div>
        )}

        {!loading && report && activeTab === 'dashboard' && <AgentTraceView report={report} />}
        {!loading && report && activeTab === 'evidence' && <EvidenceView report={report} />}
        {!loading && report && activeTab === 'debate' && <BullBearView report={report} />}
        {!loading && report && activeTab === 'valuation' && <ValuationStudio report={report} />}
        {!loading && report && activeTab === 'graph' && <GraphAndMemoryView report={report} />}
        {!loading && activeTab === 'eval' && <EvaluationLabView />}
      </main>
    </div>
  );
}
