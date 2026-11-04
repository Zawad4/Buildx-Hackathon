import { ShieldCheck, EyeOff, AlertTriangle, Cpu, Info } from 'lucide-react';
import SecurityAnalyticsChart from './SecurityAnalyticsChart';
import AccessDistributionDonut from './AccessDistributionDonut';
import SecurityIncidentsPanel from './SecurityIncidentsPanel';
import RecentActivityTable from './RecentActivityTable';

// Preserved Stage 1 KPI metrics exactly per requirement
const SAMPLE_METRICS = [
  {
    label: 'Protected PII Records',
    value: '148,290',
    subtext: '+1,420 tokenized today',
    trendClass: 'stat-trend-good',
    icon: ShieldCheck,
  },
  {
    label: 'Active Masking Rules',
    value: '42 Policies',
    subtext: 'PAN, SSN, IBAN, routing numbers',
    trendClass: 'stat-trend-good',
    icon: EyeOff,
  },
  {
    label: 'Leakage Interceptions',
    value: '17 Blocked',
    subtext: '3 high-entropy exfiltrations halted',
    trendClass: 'stat-trend-alert',
    icon: AlertTriangle,
  },
  {
    label: 'Hardware Enclave Health',
    value: '99.99%',
    subtext: '12 / 12 HSM nodes synchronized',
    trendClass: 'stat-trend-good',
    icon: Cpu,
  },
];

export default function Overview({ onNavigate }) {
  return (
    <div className="content-body">
      {/* Simulation / Hackathon evaluation disclosure */}
      <div className="demo-notice-banner">
        <Info size={14} className="demo-notice-icon" />
        <span>
          <strong>Hackathon Sandbox Enclave:</strong> All telemetry, tokenized accounts, and incident records are demonstration fixtures.
        </span>
      </div>

      {/* Preserved Stage 1 KPI Cards */}
      <div className="stat-grid">
        {SAMPLE_METRICS.map((metric, idx) => {
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

      {/* Stage 2 Security Analytics & Donut Distribution Grid */}
      <div className="analytics-grid">
        <SecurityAnalyticsChart />
        <AccessDistributionDonut />
      </div>

      {/* Stage 2 Security Incidents Panel */}
      <SecurityIncidentsPanel onNavigate={onNavigate} />

      {/* Stage 2 Enriched Activity & DLP Filter Table */}
      <RecentActivityTable onNavigate={onNavigate} />
    </div>
  );
}
