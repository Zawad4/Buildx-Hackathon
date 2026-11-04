import { useState, useMemo } from 'react';
import { ShieldCheck, Filter, ArrowUpRight } from 'lucide-react';
import { ENRICHED_ACTIVITY_EVENTS } from '../data/mockSecurityData';

function getRiskBadgeClass(risk) {
  switch (risk.toLowerCase()) {
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

export default function RecentActivityTable({ onNavigate }) {
  const [decisionFilter, setDecisionFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const filteredEvents = useMemo(() => {
    return ENRICHED_ACTIVITY_EVENTS.filter((ev) => {
      const matchDecision =
        decisionFilter === 'ALL' || ev.decision === decisionFilter;
      const matchRisk = riskFilter === 'ALL' || ev.riskLevel === riskFilter;
      return matchDecision && matchRisk;
    });
  }, [decisionFilter, riskFilter]);

  return (
    <div className="panel-card activity-panel">
      <div className="panel-header activity-panel-header">
        <div className="panel-title-group">
          <div className="panel-title">
            <ShieldCheck size={16} color="var(--status-success-text)" />
            <span>Vault Egress & Sensitive-Data Leakage Defense</span>
          </div>
          <span className="panel-subtitle">
            Field-level DLP enforcement, tokenization & redaction activity
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
            Showing {filteredEvents.length} of {ENRICHED_ACTIVITY_EVENTS.length} recorded events
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
                <th>Source / Actor</th>
                <th>Target Resource</th>
                <th>Requested Purpose</th>
                <th>Sensitive Field</th>
                <th>Access Decision</th>
                <th>Risk Level</th>
                <th>Applied Policy</th>
                <th>Enforcement</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.length > 0 ? (
                filteredEvents.map((event) => (
                  <tr key={event.id}>
                    <td className="table-code">{event.id}</td>
                    <td className="table-timestamp">{event.timestamp}</td>
                    <td className="table-code">{event.actor}</td>
                    <td className="table-code">{event.destination}</td>
                    <td className="table-purpose">{event.purpose}</td>
                    <td>{event.field}</td>
                    <td>
                      <span className={`decision-pill decision-${event.decision.toLowerCase()}`}>
                        {event.decision}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getRiskBadgeClass(event.riskLevel)}`}>
                        <span className="badge-dot" />
                        {event.riskLevel}
                      </span>
                    </td>
                    <td>{event.action}</td>
                    <td>
                      <span className={`badge badge-${event.statusType}`}>
                        <span className="badge-dot" />
                        {event.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="empty-table-cell">
                    No activity logs match the selected decision and risk filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
