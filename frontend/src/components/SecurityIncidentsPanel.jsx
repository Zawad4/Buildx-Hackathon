import { ShieldAlert, ArrowUpRight } from 'lucide-react';
import { SECURITY_INCIDENTS } from '../data/mockSecurityData';

function getSeverityClass(severity) {
  switch ((severity || '').toLowerCase()) {
    case 'critical':
      return 'severity-critical';
    case 'high':
      return 'severity-high';
    case 'medium':
      return 'severity-medium';
    case 'low':
    default:
      return 'severity-low';
  }
}

export default function SecurityIncidentsPanel({ onNavigate, incidents }) {
  const displayIncidents = incidents && incidents.length > 0 ? incidents : SECURITY_INCIDENTS;

  return (
    <div className="panel-card incidents-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <div className="panel-title">
            <ShieldAlert size={16} color="var(--status-danger-text)" />
            <span>Recent Security Incidents</span>
          </div>
          <span className="panel-subtitle">
            Anomalous exfiltration alerts requiring secops evaluation (Live from SQLite / ABAC Engine)
          </span>
        </div>
        <button
          type="button"
          className="panel-action-btn"
          onClick={() => onNavigate('monitoring')}
        >
          View All Incidents{' '}
          <ArrowUpRight
            size={13}
            style={{ display: 'inline', verticalAlign: 'middle' }}
          />
        </button>
      </div>

      <div className="panel-body">
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Incident Type</th>
                <th>Source / Actor</th>
                <th>Severity</th>
                <th>Timestamp</th>
                <th>Investigation Status</th>
              </tr>
            </thead>
            <tbody>
              {displayIncidents.map((inc) => (
                <tr key={inc.id}>
                  <td className="table-code font-bold">{inc.id}</td>
                  <td className="incident-type-cell">{inc.type}</td>
                  <td className="table-code">{inc.source}</td>
                  <td>
                    <span className={`severity-badge ${getSeverityClass(inc.severity)}`}>
                      <span className="badge-dot" />
                      {inc.severity}
                    </span>
                  </td>
                  <td className="table-timestamp">{inc.timestamp}</td>
                  <td>
                    <span className="incident-status-tag">{inc.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
