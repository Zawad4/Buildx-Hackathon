import { useState, useEffect } from 'react';
import { ScrollText, Filter, RefreshCw, Search } from 'lucide-react';
import { api } from '../services/api';

export default function AuditTrailView() {
  const [logs, setLogs] = useState([]);
  const [purposeFilter, setPurposeFilter] = useState('');
  const [searchUser, setSearchUser] = useState('');
  const [loading, setLoading] = useState(false);

  const loadAuditLogs = () => {
    setLoading(true);
    const params = {};
    if (purposeFilter) params.purpose = purposeFilter;
    if (searchUser) params.username = searchUser;

    api.getAuditLogs(params)
      .then((data) => setLogs(data.logs || []))
      .catch((err) => console.error('Failed to load audit logs:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAuditLogs();
  }, [purposeFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadAuditLogs();
  };

  return (
    <div className="content-body">
      <div className="panel-card">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="panel-title-group">
            <div className="panel-title">
              <ScrollText size={16} color="var(--brand-accent)" />
              <span>Immutable Regulatory Compliance Audit Trail</span>
            </div>
            <span className="panel-subtitle">
              Cryptographically signed historical logs for PCI-DSS 4.0, GDPR, and RBI Cyber Security audits
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '4px' }}>
              <input
                type="search"
                className="search-input"
                style={{ width: '180px' }}
                placeholder="Filter by employee..."
                value={searchUser}
                onChange={(e) => setSearchUser(e.target.value)}
              />
            </form>

            <select
              className="filter-select"
              value={purposeFilter}
              onChange={(e) => setPurposeFilter(e.target.value)}
            >
              <option value="">All Purposes</option>
              <option value="DISPUTE_RESOLUTION">Dispute Resolution</option>
              <option value="LOAN_UNDERWRITING">Loan Underwriting</option>
              <option value="GENERAL_INQUIRY">General Inquiry</option>
              <option value="FRAUD_INVESTIGATION">Fraud Investigation</option>
              <option value="COMPLIANCE_AUDIT">Compliance Audit</option>
            </select>

            <button type="button" className="panel-action-btn" onClick={loadAuditLogs}>
              <RefreshCw size={13} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        <div className="panel-body">
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Employee</th>
                  <th>Role</th>
                  <th>Target Record</th>
                  <th>Declared Purpose</th>
                  <th>Ticket Ref</th>
                  <th>Fields Disclosed</th>
                  <th>Points Charged</th>
                  <th style={{ textAlign: 'right' }}>ABAC Verdict</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="table-timestamp">{log.timestamp}</td>
                    <td className="font-bold">{log.username}</td>
                    <td className="table-code">{log.role}</td>
                    <td className="table-code font-bold" style={{ color: 'var(--brand-accent)' }}>
                      {log.customer_code || 'N/A'}
                    </td>
                    <td>{log.purpose}</td>
                    <td className="table-code">{log.ticket_id || 'N/A'}</td>
                    <td className="table-code">{log.accessed_fields}</td>
                    <td style={{ color: 'var(--status-warning-text)', fontWeight: 'bold' }}>
                      +{log.exposure_points}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span className={`status-pill ${
                        log.status === 'GRANTED' ? 'status-allowed' : log.status === 'DENIED' ? 'status-denied' : 'status-flagged'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
