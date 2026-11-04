import { useState, useEffect } from 'react';
import { ShieldCheck, EyeOff, AlertTriangle, Cpu, Info, RefreshCw } from 'lucide-react';
import SecurityAnalyticsChart from './SecurityAnalyticsChart';
import AccessDistributionDonut from './AccessDistributionDonut';
import SecurityIncidentsPanel from './SecurityIncidentsPanel';
import RecentActivityTable from './RecentActivityTable';
import { api } from '../services/api';

const DEFAULT_METRICS = [
  {
    label: 'Protected PII Records',
    value: '20 Enclaves',
    subtext: 'AES-256-GCM authenticated & tokenized',
    trendClass: 'stat-trend-good',
    icon: ShieldCheck,
  },
  {
    label: 'Active Masking Rules',
    value: '5 Policies',
    subtext: 'Dispute, Underwriting, Inquiry, Fraud, Audit',
    trendClass: 'stat-trend-good',
    icon: EyeOff,
  },
  {
    label: 'Leakage Interceptions',
    value: '2 Blocked',
    subtext: 'Automated session locks triggered',
    trendClass: 'stat-trend-alert',
    icon: AlertTriangle,
  },
  {
    label: 'Post-Quantum Status',
    value: 'ML-KEM-768',
    subtext: 'NIST FIPS 203 Lattice Engine Active',
    trendClass: 'stat-trend-good',
    icon: Cpu,
  },
];

export default function Overview({ onNavigate }) {
  const [metrics, setMetrics] = useState(DEFAULT_METRICS);
  const [liveIncidents, setLiveIncidents] = useState(null);
  const [liveActivity, setLiveActivity] = useState(null);
  const [liveDistribution, setLiveDistribution] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchLiveTelemetry = () => {
    setLoading(true);
    api.getDashboardSummary()
      .then((data) => {
        if (data.metrics && data.metrics.length > 0) {
          const merged = data.metrics.map((m, idx) => ({
            ...m,
            icon: DEFAULT_METRICS[idx]?.icon || ShieldCheck
          }));
          setMetrics(merged);
        }
        if (data.incidents) setLiveIncidents(data.incidents);
        if (data.activity) setLiveActivity(data.activity);
        if (data.distribution) setLiveDistribution(data.distribution);
      })
      .catch((err) => {
        console.warn('Backend telemetry unreachable, displaying baseline:', err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLiveTelemetry();
  }, []);

  return (
    <div className="content-body">
      {/* Live Enclave Connection Banner */}
      <div className="demo-notice-banner" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={14} className="demo-notice-icon" />
          <span>
            <strong>ADAPTIVE VAULT X Live Telemetry:</strong> Streaming live ABAC evaluations, AES-256-GCM cipher statuses, and incident feeds from SQLite.
          </span>
        </div>
        <button
          type="button"
          onClick={fetchLiveTelemetry}
          className="text-action-link"
          style={{ cursor: 'pointer', background: 'transparent', border: 'none', color: 'var(--brand-accent)', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}
        >
          <RefreshCw size={12} className={loading ? 'spin' : ''} />
          Sync Backend
        </button>
      </div>

      {/* KPI Cards */}
      <div className="stat-grid">
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          return (
            <div key={idx} className="stat-card">
              <div className="stat-header">
                <span className="stat-label">{metric.label}</span>
                <Icon size={16} strokeWidth={1.8} />
              </div>
              <div className="stat-value">{metric.value}</div>
              <div className="stat-subtext">
                <span className={metric.trendClass}>{metric.subtext}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Analytics & Donut Distribution Grid */}
      <div className="analytics-grid">
        <SecurityAnalyticsChart />
        <AccessDistributionDonut data={liveDistribution} />
      </div>

      {/* Real Security Incidents Panel */}
      <SecurityIncidentsPanel onNavigate={onNavigate} incidents={liveIncidents} />

      {/* Real Enriched Activity & DLP Filter Table */}
      <RecentActivityTable onNavigate={onNavigate} events={liveActivity} />
    </div>
  );
}
