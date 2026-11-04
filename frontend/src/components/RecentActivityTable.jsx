import { useState, useMemo } from 'react';
import { ShieldCheck, Filter, ArrowUpRight } from 'lucide-react';
import { ENRICHED_ACTIVITY_EVENTS } from '../data/mockSecurityData';

function getRiskBadgeClass(risk) {
  switch ((risk || '').toLowerCase()) {
    case 'critical':
      return 'badge-danger';
    case 'high':
      return 'badge-warning';
    case 'medium':
      return 'badge-warning';
    case 'low':
    default:
      return 'badge-neutral';
  }
}

export default function RecentActivityTable({ onNavigate, events }) {
  const [decisionFilter, setDecisionFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const sourceEvents = events && events.length > 0 ? events : ENRICHED_ACTIVITY_EVENTS;

  const filteredEvents = useMemo(() => {
    return sourceEvents.filter((ev) => {
      const matchDecision =
        decisionFilter === 'ALL' || ev.decision === decisionFilter;
      const matchRisk = riskFilter === 'ALL' || ev.riskLevel === riskFilter;
      return matchDecision && matchRisk;
    });
  }, [sourceEvents, decisionFilter, riskFilter]);

  return (
    <div className="panel-card activity-panel">
      <div className="panel-header activity-panel-header">
        <div className="panel-title-group">
          <div className="panel-title">
            <ShieldCheck size={16} color="var(--status-success-text)" />
            <span>Vault Egress & Sensitive-Data Leakage Defense</span>
          </div>
          <span className="panel-subtitle">
            Live field-level DLP enforcement, tokenization & redaction activity from SQLite Audit Logs
          </span>
        </div>

        <div className="activity-header-actions">
          <div className="filter-controls">
            <div className="filter-item">
              <Filter size={13} className="filter-icon" />
              <select
                className="filter-select"
                value={decisionFilter}
                onChange={(e) => setDecisionFilter(e.target.value)}
                aria-label="Filter by access decision"
              >
                <option value="ALL">All Decisions</option>
                <option value="Allowed">Allowed</option>
                <option value="Denied">Denied</option>
                <option value="Flagged">Flagged</option>
              </select>
            </div>

            <div className="filter-item">
              <select
                className="filter-select"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                aria-label="Filter by risk level"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
                <option value="Critical">Critical Risk</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            className="panel-action-btn"
            onClick={() => onNavigate('records')}
          >
            View Customer Records{' '}
            <ArrowUpRight
              size={13}
              style={{ display: 'inline', verticalAlign: 'middle' }}
            />
          </button>
        </div>
      </div>

      <div className="panel-body">
        <div className="table-filter-stats">
          <span>
            Showing {filteredEvents.length} of {sourceEvents.length} recorded events
          </span>
          {(decisionFilter !== 'ALL' || riskFilter !== 'ALL') && (
            <button
              type="button"
              className="text-action-link"
              onClick={() => {
                setDecisionFilter('ALL');
                setRiskFilter('ALL');
              }}
            >
              Reset Filters
            </button>
          )}
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Timestamp</th>
                <th>Actor / Service</th>
                <th>Target Vault Record</th>
                <th>Disclosed Fields</th>
                <th>Action Taken</th>
                <th>Declared Purpose</th>
                <th>Decision</th>
                <th>Risk Rating</th>
                <th>Protection</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((ev) => (
                <tr key={ev.id}>
                  <td className="table-code font-bold">{ev.id}</td>
                  <td className="table-timestamp">{ev.timestamp}</td>
                  <td className="table-code">{ev.actor}</td>
                  <td className="table-code">{ev.destination}</td>
                  <td className="table-code">{ev.field}</td>
                  <td>{ev.action}</td>
                  <td>{ev.purpose}</td>
                  <td>
                    <span
                      className={`status-pill ${
                        ev.decision === 'Allowed'
                          ? 'status-allowed'
                          : ev.decision === 'Denied'
                          ? 'status-denied'
                          : 'status-flagged'
                      }`}
                    >
                      {ev.decision}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${getRiskBadgeClass(ev.riskLevel)}`}>
                      {ev.riskLevel}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-accent">{ev.status}</span>
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
